"""Bounded per-instance abuse protection; host-level limits are still required."""
import os
import time
from collections import deque
from threading import Lock
from fastapi.responses import JSONResponse

_requests = {}
_lock = Lock()


async def guard(request, call_next):
    origin = request.headers.get("origin")
    allowed = {s.strip().rstrip("/") for s in os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",") if s.strip()}
    if origin and origin.rstrip("/") not in allowed:
        return JSONResponse({"detail": "This website is not an allowed origin."}, status_code=403)
    limit = 10 * 1024 * 1024 if request.url.path.endswith("/knowledge/pdf") else 256 * 1024
    try:
        length = int(request.headers.get("content-length", "0"))
    except ValueError:
        return JSONResponse({"detail": "Invalid request length."}, status_code=400)
    if length < 0:
        return JSONResponse({"detail": "Invalid request length."}, status_code=400)
    if length > limit:
        return JSONResponse({"detail": "Request is too large."}, status_code=413)
    if request.method == "POST":
        host = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with _lock:
            # Never trust forwarded IP headers from arbitrary callers.
            for key in list(_requests):
                if not _requests[key] or now - _requests[key][-1] >= 60:
                    del _requests[key]
            queue = _requests.setdefault(host, deque())
            while queue and now - queue[0] >= 60:
                queue.popleft()
            maximum = int(os.getenv("REQUESTS_PER_MINUTE", "120"))
            if len(queue) >= maximum or len(_requests) > 10000:
                return JSONResponse({"detail": "Too many requests. Wait a minute and try again."}, status_code=429, headers={"Retry-After": "60"})
            queue.append(now)
        if not request.url.path.endswith("/knowledge/pdf"):
            raw = bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > limit:
                    return JSONResponse({"detail": "Request is too large."}, status_code=413)
            # Starlette's cached request forwards this bounded body to FastAPI.
            request._body = bytes(raw)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response
