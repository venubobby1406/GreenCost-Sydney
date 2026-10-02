"""Persistent Chroma knowledge base with page citations and explicit embeddings."""

import hashlib
import json
import os
import re
from functools import lru_cache
from threading import RLock
import chromadb
from chromadb.config import Settings
import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.research.sources import DATA

INDEX_DIR = DATA / "chroma"
MODEL = os.getenv("RAG_EMBEDDING_MODEL", "local-hash-v1")
COLLECTION = "building_knowledge_" + hashlib.sha256(MODEL.encode()).hexdigest()[:12]
_INGEST_LOCK = RLock()


@lru_cache(maxsize=4)
def client(path: str):
    return chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))


def collection():
    return client(str(INDEX_DIR)).get_or_create_collection(
        COLLECTION, embedding_function=None, metadata={"hnsw:space": "cosine", "embedding_model": MODEL}
    )


@lru_cache(maxsize=1)
def semantic_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL, local_files_only=True)


def embed(texts):
    if MODEL != "local-hash-v1":
        return semantic_model().encode(texts, normalize_embeddings=True).astype("float32").tolist()
    vectors = np.zeros((len(texts), 2048), dtype="float32")
    for i, text in enumerate(texts):
        words = re.findall(r"[a-z0-9]+", text.lower())
        for token in words + [" ".join(words[j : j + 2]) for j in range(len(words) - 1)]:
            slot = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "little") % 2048
            vectors[i, slot] += 1
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return (vectors / np.maximum(norms, 1e-12)).tolist()


def ingest(force=False):
    with _INGEST_LOCK:
        return _ingest(force)


def _ingest(force=False):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store = collection()
    existing = set(store.get(include=[])["ids"])
    splitter = RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=160)
    chunks, files = [], {}
    paths = sorted((DATA / "knowledge").glob("*.pdf")) + sorted((DATA / "knowledge").glob("*.json"))
    paths += sorted((DATA / "verified").glob("*.json"))
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files[path.relative_to(DATA).as_posix()] = digest
        if path.suffix == ".pdf":
            pages = [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(path).pages)]
            meta = dict(source=path.name, title=path.stem, source_type="PROJECT_RESEARCH", date="", url="")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            pages = [(1, json.dumps(data, ensure_ascii=False, indent=2))]
            meta = dict(source=path.name, title=data["title"], source_type=data["source_category"],
                        date=data.get("publication_date") or data.get("date") or "", url=data.get("url") or "")
        for page, text in pages:
            for n, chunk in enumerate(splitter.split_text(text)):
                chunks.append(dict(id=f"{path.name}:{digest}:{page}:{n}", text=chunk,
                                   page=page, document_hash=digest, **meta))
    if not chunks:
        raise ValueError("No readable knowledge documents found")
    fresh = [d for d in chunks if force or d["id"] not in existing]
    for start in range(0, len(fresh), 64):
        batch = fresh[start:start + 64]
        store.upsert(ids=[d["id"] for d in batch], documents=[d["text"] for d in batch],
                     embeddings=embed([d["text"] for d in batch]),
                     metadatas=[{k: v for k, v in d.items() if k not in ("id", "text")} for d in batch])
    removed = existing - {d["id"] for d in chunks}
    if removed:
        store.delete(ids=sorted(removed))
    manifest = dict(model=MODEL, files=files, chunks=len(chunks), collection=COLLECTION)
    target = INDEX_DIR / "manifest.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(target)
    return dict(documents=len(paths), chunks=len(chunks), new_embeddings=len(fresh), model=MODEL)


def readiness():
    path = INDEX_DIR / "manifest.json"
    if not path.exists():
        return dict(ready=False, documents=0, chunks=0)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        store = collection()
        return dict(ready=manifest["model"] == MODEL and store.count() == manifest["chunks"],
                    documents=len(manifest["files"]), chunks=store.count())
    except (ValueError, KeyError, OSError, chromadb.errors.ChromaError):
        return dict(ready=False, documents=0, chunks=0)


def retrieve(query: str, limit=4, source_type=None):
    if not (INDEX_DIR / "manifest.json").exists():
        return []
    manifest = json.loads((INDEX_DIR / "manifest.json").read_text(encoding="utf-8"))
    if manifest["model"] != MODEL:
        raise ValueError("Embedding model changed; run scripts/ingest_knowledge.py first.")
    store = collection()
    if not store.count():
        return []
    found = store.query(query_embeddings=embed([query]), n_results=min(limit, store.count()),
                        where={"source_type": source_type} if source_type else None,
                        include=["documents", "metadatas", "distances"])
    return [dict(id=id, text=text, score=1 - distance, **meta)
            for id, text, meta, distance in zip(found["ids"][0], found["documents"][0],
                                                found["metadatas"][0], found["distances"][0])
            if distance < 1]
