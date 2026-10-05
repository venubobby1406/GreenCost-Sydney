"""PDF passages in ordinary JSON files, ranked with in-memory NumPy arrays."""
import hashlib
import json
import re
from functools import lru_cache
from threading import RLock
import numpy as np
from pypdf import PdfReader
from backend.app.research.sources import DATA
from backend.app.services.files import atomic_json

INDEX_DIR = DATA / "research_index"
MODEL = "local-hash-v1"
_INGEST_LOCK = RLock()


def embed(texts):
    vectors = np.zeros((len(texts), 2048), dtype="float32")
    for i, text in enumerate(texts):
        words = re.findall(r"[a-z0-9]+", text.lower())
        for token in words + [" ".join(words[j:j + 2]) for j in range(len(words) - 1)]:
            slot = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "little") % 2048
            vectors[i, slot] += 1
    return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)


@lru_cache(maxsize=4)
def _read(path, modified):
    return json.loads(open(path, encoding="utf-8").read())


def records():
    path = INDEX_DIR / "passages.json"
    return _read(str(path), path.stat().st_mtime_ns) if path.exists() else []


def ingest(force=False):
    with _INGEST_LOCK:
        paths = sorted((DATA / "knowledge").glob("*.pdf")) + sorted((DATA / "knowledge").glob("*.json"))
        paths += sorted((DATA / "verified").glob("*.json"))
        previous = {d["id"]: d for d in records()}
        chunks, files, fresh = [], {}, 0
        for path in paths:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files[path.relative_to(DATA).as_posix()] = digest
            old = [d for d in previous.values() if d.get("source") == path.name and d.get("document_hash") == digest]
            if old and not force:
                chunks.extend(old)
                continue
            if path.suffix == ".pdf":
                pages = [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(path).pages)]
                meta = dict(source=path.name, title=path.stem, source_type="PROJECT_RESEARCH", date="", url="")
            else:
                data = json.loads(path.read_text(encoding="utf-8"))
                pages = [(1, json.dumps(data, ensure_ascii=False, indent=2))]
                meta = dict(source=path.name, title=data["title"], source_type=data["source_category"],
                            date=data.get("publication_date") or data.get("date") or "", url=data.get("url") or "")
            for page, content in pages:
                for n, start in enumerate(range(0, len(content.strip()), 940)):
                    text = content[start:start + 1100].strip()
                    if text:
                        chunks.append(dict(id=f"{path.name}:{digest}:{page}:{n}", text=text, page=page,
                                           document_hash=digest, **meta))
                        fresh += 1
        if not chunks:
            raise ValueError("No readable knowledge documents found")
        atomic_json(INDEX_DIR / "passages.json", chunks)
        atomic_json(INDEX_DIR / "manifest.json", dict(model=MODEL, files=files, chunks=len(chunks)))
        _read.cache_clear()
        return dict(documents=len(paths), chunks=len(chunks), new_embeddings=fresh, model=MODEL)


def readiness():
    try:
        manifest = json.loads((INDEX_DIR / "manifest.json").read_text(encoding="utf-8"))
        count = len(records())
        return dict(ready=manifest["model"] == MODEL and count == manifest["chunks"],
                    documents=len(manifest["files"]), chunks=count)
    except (ValueError, KeyError, OSError):
        return dict(ready=False, documents=0, chunks=0)


def retrieve(query: str, limit=4, source_type=None):
    chunks = [d for d in records() if source_type is None or d["source_type"] == source_type]
    if not chunks:
        return []
    scores = embed([d["text"] for d in chunks]) @ embed([query])[0]
    ordered = np.argsort(-scores, kind="stable")[:max(0, min(limit, len(chunks)))]
    return [dict(chunks[i], score=float(scores[i])) for i in ordered if scores[i] > 0]
