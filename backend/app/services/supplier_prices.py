"""Bounded Tavily discovery using source-page text; snippets never become prices.

Only price metadata is cached. No page copies, direct scraping or arbitrary URL fetches.
Ambiguous variants, 'from' prices, missing GST or unit mismatches require a quote.
"""
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from threading import Lock
from urllib.parse import urlparse

import httpx

from backend.app.research.sources import DATA
from backend.app.services.budget import reserve
from backend.app.services.files import atomic_json

PRODUCTS = {
    "concrete": ("ready mix concrete supply price per m3 Sydney GST", "m³", ["bunnings.com.au"]),
    "timber": ("structural timber supply price per m3 Sydney GST", "m³", ["bunnings.com.au"]),
    "roofing": ("metal roof sheet supply price per m2 Sydney GST", "m²", ["bunnings.com.au"]),
    "windows": ("window glazing supply price per m2 Sydney GST", "m²", ["bunnings.com.au"]),
    "insulation": ("wall insulation R2.5 supply price per m2 inc GST", "m²", ["pricewiseinsulation.com.au", "insulationeasy.com.au"]),
    "finishes": ("internal finishes fittings Sydney quote", "allowance", ["bunnings.com.au"]),
}
_lock = Lock()
_memory = {}
_attempts = {}
TTL = 86400


def allowed_url(url, domains):
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        return p.scheme == "https" and not p.username and not p.password and p.port in (None, 443) and any(host == d or host.endswith("." + d) for d in domains)
    except ValueError:
        return False


def price_from_page(content, unit):
    """Accept only explicit, unambiguous tax-inclusive per-unit supply prices."""
    if unit not in ("m²", "m³") or not isinstance(content, str):
        return None
    # A variant/range or installed price cannot safely replace a supply allowance.
    if re.search(r"\b(from|starting at|ex\.?\s*gst|excl\w*\s*gst|installed price)\b", content, re.I):
        return None
    u = r"m(?:²|2|\^2)" if unit == "m²" else r"m(?:³|3|\^3)"
    matches = re.findall(r"(?:AUD\s*|A)?\$\s*([\d,]+(?:\.\d{1,2})?)\s*(?:/|per\s+|p/)" + u + r"\s*(?:\*\s*)?(?:inc\.?|including|inclusive of)\s*GST", content, re.I)
    values = {float(x.replace(",", "")) for x in matches}
    if len(values) != 1:
        return None
    value = values.pop()
    return value if .1 <= value <= 100000 else None


def _read(key):
    if key in _memory:
        return _memory[key]
    path = DATA / "prices" / ("supplier_" + key + ".json")
    if not os.getenv("VERCEL") and path.exists():
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(entry, dict) and isinstance(entry.get("saved_at"), (int, float)) and isinstance(entry.get("result"), dict) and isinstance(entry["result"].get("candidates"), list):
                return entry
        except (OSError, ValueError):
            pass
    return None


def supplier_price(request):
    query, unit, domains = PRODUCTS[request.item]
    key = hashlib.sha256((request.item + ":Sydney").encode()).hexdigest()[:20]
    with _lock:
        cached = _read(key)
        if cached and 0 <= time.time() - cached["saved_at"] < TTL:
            return {**cached["result"], "cached": True}
        if time.time() - _attempts.get(key, 0) < 60:
            return dict(status="cooldown", candidates=[], message="Wait a minute before checking this item again.")
        _attempts[key] = time.time()
    if unit == "allowance":
        return dict(status="quote_required", candidates=[], message="This category covers multiple products; a project quote is required.")
    if not os.getenv("TAVILY_API_KEY"):
        return dict(status="not_configured", candidates=[], message="No Tavily key configured. Your estimate remains unchanged.")
    if not reserve("tavily"):
        return dict(status="budget_or_host_limit", candidates=[], message="Search quota or hosted setting prevents a refresh. Your estimate remains unchanged.")
    checked = datetime.now(timezone.utc).isoformat()
    try:
        response = httpx.post("https://api.tavily.com/search", json={
            "api_key": os.environ["TAVILY_API_KEY"], "query": query,
            "include_domains": domains, "max_results": 3, "search_depth": "basic",
            "include_answer": False, "include_raw_content": "text",
        }, timeout=15)
        response.raise_for_status()
        candidates = []
        for result in response.json().get("results", [])[:3]:
            url = result.get("url", "")
            if not allowed_url(url, domains):
                continue
            raw = result.get("raw_content")
            price = price_from_page(raw, unit)
            candidates.append(dict(title=str(result.get("title", "Supplier product"))[:180], url=url,
                                   unit=unit, unit_price=price, checked_at=checked,
                                   status="Published supply price" if price is not None else "Quote required",
                                   gst="Included" if price is not None else "Unconfirmed",
                                   delivery="Excluded / unconfirmed", installation="Excluded",
                                   specification="Confirm exact product, dimensions and performance before using this price."))
        output = dict(status="complete" if candidates else "no_results", candidates=candidates, cached=False,
                      message="Supply prices only. Quantities, installation, delivery and product suitability need review.")
        if candidates:
            entry = dict(saved_at=time.time(), result=output)
            with _lock:
                _memory[key] = entry
                if not os.getenv("VERCEL"):
                    try:
                        atomic_json(DATA / "prices" / ("supplier_" + key + ".json"), entry)
                    except OSError:
                        pass
        return output
    except (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError):
        return dict(status="unavailable", candidates=[], message="Supplier research unavailable. Your estimate remains unchanged.")
