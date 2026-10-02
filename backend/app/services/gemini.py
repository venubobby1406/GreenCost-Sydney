"""Server-side Gemini REST adapter. No API keys or raw responses reach the client."""

import os
import re
import httpx


def configured():
    return bool(os.getenv("GEMINI_API_KEY"))


def generate(system: str, context: str):
    if not configured():
        return None, 0, "not_configured"
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", model):
        return None, 0, "invalid_model"
    try:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            json={"systemInstruction": {"parts": [{"text": system}]},
                  "contents": [{"role": "user", "parts": [{"text": context}]}],
                  "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1800}}, timeout=30,
        )
        response.raise_for_status()
        parts = response.json()["candidates"][0]["content"]["parts"]
        text = "\n".join(p["text"] for p in parts if isinstance(p.get("text"), str) and not p.get("thought"))
        return (text[:7000], 1, "complete") if text.strip() else (None, 1, "empty_response")
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None, 1, "unavailable"
