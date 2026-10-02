"""Tavily discovery supplies cited context, never authoritative financial inputs."""

import os
from datetime import datetime, timezone
import httpx
from backend.app.research.sources import official_domain

DOMAINS = {"aer.gov.au", "sydneywater.com.au", "abs.gov.au", "planning.nsw.gov.au", "planningportal.nsw.gov.au"}


def research(query: str, enabled=True):
    if not enabled:
        return [], 0, "disabled"
    if not os.getenv("TAVILY_API_KEY"):
        return [], 0, "not_configured"
    try:
        response = httpx.post("https://api.tavily.com/search", json={
            "api_key": os.environ["TAVILY_API_KEY"], "query": query[:600],
            "include_domains": sorted(DOMAINS), "max_results": 4,
            "search_depth": "basic", "include_answer": False, "include_raw_content": False,
        }, timeout=15)
        response.raise_for_status()
        evidence = []
        for item in response.json().get("results", [])[:4]:
            if official_domain(item.get("url", ""), DOMAINS) and isinstance(item.get("content"), str):
                evidence.append(dict(source=item.get("title", "Official web source")[:180],
                                     title=item.get("title", "Official web source")[:180], page=0,
                                     text=item["content"][:1800], url=item["url"], source_type="WEB_RESEARCH",
                                     retrieved_at=datetime.now(timezone.utc).isoformat()))
        return evidence, 1, "complete" if evidence else "no_results"
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        return [], 1, "unavailable"
