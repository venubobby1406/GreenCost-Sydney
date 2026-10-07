"""Sequential, bounded explanation fallback; never changes financial calculations."""
import json
import os
import re
import time
from contextvars import ContextVar
import httpx
from backend.app.services import gemini
from backend.app.services.budget import reserve

_trace = ContextVar("ai_provider_trace", default=None)
PROVIDERS = ("openrouter", "groq", "gemini")

def trace():
    return dict(_trace.get() or {p: "not_requested" for p in PROVIDERS})

def usable(text, context):
    if not isinstance(text, str) or not text.strip() or len(text) > 7000:
        return False
    if re.search(r"\b(?:user safety|safety classification|request status|backend request|reply received)\s*:", text, re.I):
        return False
    try:
        count = len(json.loads(context).get("evidence", []))
    except (ValueError, TypeError):
        count = 0
    citations = re.findall(r"\[S(\d+)\]", text)
    clean = re.sub(r"\[S\d+\]", "", text)
    # Ordinary phrases such as "one option" are not financial claims.
    return not re.search(r"[\d$%€£]|\b(three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|dollars?|percent(?:age)?s?)\b", clean, re.I) and all(1 <= int(n) <= count for n in citations)

def chat(provider, system, context, timeout):
    key = os.getenv(provider.upper() + "_API_KEY", "")
    if not key:
        return None, 0, "not_configured"
    model = os.getenv(provider.upper() + "_MODEL", "openai/gpt-oss-20b" if provider == "groq" else "openrouter/free")
    if provider == "openrouter" and not (model.endswith(":free") or model == "openrouter/free"):
        return None, 0, "free_model_required"
    if not re.fullmatch(r"[a-zA-Z0-9._:/-]+", model):
        return None, 0, "invalid_model"
    if not reserve(provider):
        return None, 0, "budget_or_host_limit"
    url = "https://api.groq.com/openai/v1/chat/completions" if provider == "groq" else "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": context}], "temperature": .2, "max_tokens": 4096}
    # Reasoning shares the output budget; leave room for the final explanation.
    if provider == "groq" and model in ("openai/gpt-oss-20b", "openai/gpt-oss-120b"):
        payload.update(reasoning_effort="low", include_reasoning=False)
    elif provider == "openrouter":
        payload["reasoning"] = {"effort": "low", "exclude": True}
    try:
        r = httpx.post(url, headers={"Authorization": "Bearer " + key},
                       json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            return None, 1, "unavailable"
        choice = data["choices"][0]
        if choice.get("finish_reason") != "stop":
            return None, 1, "incomplete_response"
        text = choice["message"]["content"]
        return (text, 1, "complete") if isinstance(text, str) and text.strip() else (None, 1, "empty_response")
    except httpx.HTTPStatusError as e:
        return None, 1, {401: "invalid_key", 402: "quota_reached", 403: "permission_denied", 404: "model_unavailable", 429: "quota_reached", 503: "provider_busy"}.get(e.response.status_code, "unavailable")
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None, 1, "unavailable"

def generate(system, context):
    statuses = {p: "not_requested" for p in PROVIDERS}
    statuses["explanation_provider"] = "calculated"
    _trace.set(statuses)
    calls = 0
    deadline = time.monotonic() + 45
    for provider in PROVIDERS:
        remaining = deadline - time.monotonic()
        if remaining < 1:
            statuses[provider] = "time_limit"
            break
        timeout = min(12, remaining)
        text, count, status = gemini.generate(system, context, timeout=timeout) if provider == "gemini" else chat(provider, system, context, timeout)
        calls += count
        if text and not usable(text, context):
            text, status = None, "rejected_response"
        statuses[provider] = status
        if text and status == "complete":
            statuses["explanation_provider"] = provider
            return text, calls, "complete"
    return None, calls, statuses["gemini"] if statuses["gemini"] != "not_configured" else "not_configured"
