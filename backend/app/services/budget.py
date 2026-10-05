"""Conservative counters; hosted instances cannot share a quota without storage."""
import os
from datetime import datetime, timezone
from threading import Lock
from backend.app.research.sources import DATA
from backend.app.services.files import atomic_json
import json

_lock = Lock()
_memory = {}


def reserve(provider):
    # Free hosting defaults to AI off to prevent unbounded calls across instances.
    if os.getenv("VERCEL") and os.getenv("ENABLE_HOSTED_AI", "false").lower() != "true":
        return False
    now = datetime.now(timezone.utc)
    try:
        daily = int(os.getenv(provider.upper() + "_DAILY_CAP", "10" if provider == "tavily" else "20"))
        monthly = int(os.getenv(provider.upper() + "_MONTHLY_CAP", "200" if provider == "tavily" else "400"))
    except ValueError:
        return False
    path = DATA / "prices" / "usage.json"
    with _lock:
        counters = _memory
        if not os.getenv("VERCEL") and path.exists():
            try:
                counters = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(counters, dict) or any(not isinstance(v, int) or v < 0 for v in counters.values()):
                    return False
            except (OSError, ValueError):
                return False
        keys = [f"{provider}:day:{now:%Y-%m-%d}", f"{provider}:month:{now:%Y-%m}"]
        if counters.get(keys[0], 0) >= daily or counters.get(keys[1], 0) >= monthly:
            return False
        for key in keys:
            counters[key] = counters.get(key, 0) + 1
        if not os.getenv("VERCEL"):
            try:
                atomic_json(path, counters)
            except OSError:
                return False
        return True
