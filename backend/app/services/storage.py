import json
import os
import re
from uuid import uuid4
from datetime import datetime, timezone
from backend.app.research.sources import DATA
from backend.app.services.files import atomic_json


def save(result):
    id = str(uuid4())
    result["id"] = id
    result["created_at"] = datetime.now(timezone.utc).isoformat()
    if not os.getenv("VERCEL") and os.getenv("SAVE_LOCAL_ANALYSES", "true").lower() == "true":
        atomic_json(DATA / "analyses" / (id + ".json"), result)
    return result


def get(id):
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", id):
        return None
    path = DATA / "analyses" / (id + ".json")
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
