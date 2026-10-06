"""Server-side Gemini REST adapter. No API keys or raw responses reach the client."""

import os
import re
import httpx
from backend.app.services.budget import reserve


def configured():
    return bool(os.getenv("GEMINI_API_KEY"))


def generate(system: str, context: str):
    if not configured():
        return None, 0, "not_configured"
    if not reserve("gemini"):
        return None, 0, "budget_or_host_limit"
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        return None, 0, "invalid_model"
    try:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            json={"systemInstruction": {"parts": [{"text": system}]},
                  "contents": [{"role": "user", "parts": [{"text": context}]}],
                  "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}}, timeout=30,
        )
        response.raise_for_status()
        candidate = response.json()["candidates"][0]
        if candidate.get("finishReason", "STOP") != "STOP":
            return None, 1, "incomplete_response"
        parts = candidate["content"]["parts"]
        text = "\n".join(p["text"] for p in parts if isinstance(p.get("text"), str) and not p.get("thought"))
        if len(text) > 7000:
            return None, 1, "incomplete_response"
        return (text, 1, "complete") if text.strip() else (None, 1, "empty_response")
    except httpx.HTTPStatusError as error:
        status = {401: "invalid_key", 403: "permission_denied", 404: "model_unavailable", 429: "quota_reached", 503: "provider_busy"}.get(error.response.status_code, "unavailable")
        return None, 1, status
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None, 1, "unavailable"
