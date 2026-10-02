import json
import sqlite3
from uuid import uuid4
from datetime import datetime, timezone
from backend.app.research.sources import DATA


def connection():
    conn = sqlite3.connect(DATA / "greencost.sqlite3", timeout=20)
    conn.execute("CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, result TEXT NOT NULL)")
    return conn


def save(result):
    id = str(uuid4())
    result["id"] = id
    result["created_at"] = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        conn.execute("INSERT INTO analyses VALUES (?,?,?)", (id, result["created_at"], json.dumps(result)))
    return result


def get(id):
    with connection() as conn:
        row = conn.execute("SELECT result FROM analyses WHERE id=?", (id,)).fetchone()
    return json.loads(row[0]) if row else None
