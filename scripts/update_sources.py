"""Explicit refresh: at most three Tavily searches. Original pages, never answer text.

Conservatively re-verifies the current schema. Changed periods/values are staged for
manual review; never silently promote ambiguous extraction into current pricing.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
import httpx
from bs4 import BeautifulSoup
from backend.app.research.sources import DATA, official_domain, load_sources, validate_source
from backend.app.services.budget import reserve


def verify_page(source, text):
    """Require dated original numerical table context, not search-engine answer text."""
    normalized = re.sub(r"\s+", " ", text).replace("–", "-").replace("−", "-")
    if source["id"] == "aer_2026_27":
        if not re.search(r"2026\s*-\s*27", normalized) or "30 June 2027" not in normalized:
            raise ValueError("AER effective period missing")
        for zone in ("Ausgrid", "Endeavour Energy", "Essential Energy"):
            short = zone.replace(" Energy", "")
            usage = source["values"][zone + "_usage"]["value"] * 100
            supply = source["values"][zone + "_supply"]["value"]
            if not re.search(
                re.escape(short)
                + rf".{{0,180}}Single/flat rate plan\s*\$\s*{supply:.2f}\s*All day\s*{usage:.2f}\s*c/kWh",
                normalized,
            ):
                raise ValueError("Cannot confirm zone, customer, unit and flat tariff together: " + zone)
    elif source["id"] == "sydney_water_2026_27":
        expected = {
            "drinking_usage": 3.41,
            "drought_usage": 3.84,
            "water_service": 26.65,
            "wastewater": 189.88,
            "stormwater_house": 30.26,
            "stormwater_unit": 9.67,
        }
        if any(source["values"].get(k, {}).get("value") != v for k, v in expected.items()):
            raise ValueError("Cached values differ from this audited 2026–27 extraction schema")
        if not re.search(r"1 July 2026\s+to\s+30 June 2027", normalized):
            raise ValueError("Sydney Water effective period missing")
        checks = {
            "drinking_usage": r"Drinking water usage\s*\$3\.17 a kilolitre\s*\$3\.41 a kilolitre",
            "water_service": r"If you have a meter\s*\$29\.73 a quarter\s*\$26\.65 a quarter",
            "wastewater": r"Your wastewater service\s*\$174\.40 a quarter\s*\$189\.88 a quarter",
            "stormwater_house": r"If you live in a house\s*\$29\.07\s*\$30\.26",
            "stormwater_unit": r"If you live in a unit or are low impact\s*\$9\.29\s*\$9\.67",
            "drought_usage": r"Drought drinking water usage\s*\^?\s*\$3\.58 a kilolitre\s*\$3\.84 a kilolitre",
        }
        if "92 days" not in normalized:
            raise ValueError("Fixed-charge daily basis missing")
        for key, pattern in checks.items():
            if not re.search(pattern, normalized):
                raise ValueError("Cannot confirm current table cell: " + key)
    elif source["id"] == "abs_ppi_2026":
        expected = {"building_construction": 163.3, "quarter_change": 1.4, "annual_change": 4.9}
        if any(source["values"].get(k, {}).get("value") != v for k, v in expected.items()):
            raise ValueError("Cached values differ from this audited June 2026 extraction schema")
        if (
            not re.search(r"Jun 2026\s+163\.3\s+1\.4\s+4\.9", normalized)
            or "31/07/2026" not in normalized
            or "Output of Building construction" not in normalized
        ):
            raise ValueError("Cannot confirm ABS building construction reference row")
    else:
        raise ValueError("No audited parser for this source")


def refresh(direct=False, offline=False):
    sources = [s for s in load_sources() if s["id"] in ("aer_2026_27", "sydney_water_2026_27", "abs_ppi_2026")]
    if offline:
        for s in sources:
            validate_source(s)
        return {"status": "cached records valid", "tavily_calls": 0}
    if direct:
        return {"status": "Direct scraping disabled. Use Tavily mode or reviewed manual records.", "tavily_calls": 0}
    if not direct and not os.getenv("TAVILY_API_KEY"):
        return {"status": "No Tavily key; retained local cache without network calls.", "tavily_calls": 0}
    calls, results = 0, []
    with httpx.Client(timeout=25, follow_redirects=False) as client:
        for source in sources:
            domain = source["url"].split("/")[2].removeprefix("www.")
            try:
                if not direct:
                    if not reserve("tavily"):
                        raise ValueError("Daily or monthly request cap reached")
                    calls += 1
                    response = client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": os.environ["TAVILY_API_KEY"],
                            "query": source["title"] + " official numerical prices reference period",
                            "include_domains": [domain],
                            "max_results": 3,
                            "search_depth": "basic",
                            "include_answer": False,
                        },
                    )
                    response.raise_for_status()
                    hits = [
                        r for r in response.json().get("results", []) if official_domain(r.get("url", ""), {domain})
                    ]
                    if not hits:
                        raise ValueError("No official discovery result; cache preserved")
                # Extract pinned official URLs through Tavily; retain no page copies.
                if not reserve("tavily"):
                    raise ValueError("Daily or monthly request cap reached")
                calls += 1
                response = client.post("https://api.tavily.com/extract", json={
                    "api_key": os.environ["TAVILY_API_KEY"], "urls": [source["url"]],
                    "extract_depth": "basic", "format": "text",
                })
                response.raise_for_status()
                extracted = response.json().get("results", [])
                text = next(item["raw_content"] for item in extracted if item.get("url") == source["url"])
                text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
                verify_page(source, text)
                source["retrieved_at"] = date.today().isoformat()
                validate_source(source)
                target = DATA / "verified" / f"{source['id']}.json"
                temp = target.with_suffix(".tmp")
                temp.write_text(json.dumps(source, indent=2, ensure_ascii=False), encoding="utf-8")
                temp.replace(target)
                results.append(
                    {
                        "id": source["id"],
                        "status": "verified",
                        "snapshot_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    }
                )
            except (httpx.HTTPError, ValueError, KeyError, StopIteration) as error:
                # Never echo response headers, payloads, API keys or arbitrary remote error text.
                results.append(
                    {
                        "id": source["id"],
                        "status": "retained; original-page verification failed",
                        "reason": type(error).__name__,
                    }
                )
    log = {"date": date.today().isoformat(), "tavily_calls": calls, "results": results}
    (DATA / "snapshots").mkdir(exist_ok=True)
    (DATA / "snapshots/refresh_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--direct", action="store_true", help="Disabled: direct scraping is not allowed; use Tavily search and extract")
    args = parser.parse_args()
    print(json.dumps(refresh(args.direct, args.offline), indent=2))
