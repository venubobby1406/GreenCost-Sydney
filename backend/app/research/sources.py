import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from backend.app.schemas.models import Source

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
ALLOWED = {"aer.gov.au", "sydneywater.com.au", "abs.gov.au"}


def official_domain(url: str, allowed=ALLOWED) -> bool:
    p = urlparse(url)
    return p.scheme == "https" and any(p.hostname == d or (p.hostname or "").endswith("." + d) for d in allowed)


def validate_source(raw: dict, as_of: date | None = None) -> Source:
    s = Source.model_validate(raw)
    if s.source_category != "REGULATORY_CONTEXT" and not official_domain(s.url):
        raise ValueError("Primary financial sources must use official allowlisted HTTPS domains.")
    if s.effective_from.year < 2026:
        raise ValueError("Pre-2026 values cannot become current financial sources.")
    if s.publication_date and s.publication_date > (as_of or date.today()):
        raise ValueError("Unpublished future data rejected.")
    if s.effective_from > (as_of or date.today()):
        raise ValueError("Not yet effective.")
    if s.source_category == "CURRENT_OFFICIAL_PRICING" and (
        not s.effective_to or s.effective_to < (as_of or date.today())
    ):
        raise ValueError("Tariff cache has expired. Refresh or supply applicable user rates.")
    if not s.evidence or not s.values:
        raise ValueError("Original-page numerical evidence is required.")
    if s.source_category == "CURRENT_OFFICIAL_PRICING":
        if s.customer_type != "Residential" or s.jurisdiction != "NSW":
            raise ValueError("This tariff cache is residential NSW only.")
        if s.id == "aer_2026_27":
            required = {
                zone + "_" + key: unit
                for zone in ("Ausgrid", "Endeavour Energy", "Essential Energy")
                for key, unit in (("usage", "AUD/kWh"), ("supply", "AUD/day"))
            }
            domain = "aer.gov.au"
        elif s.id == "sydney_water_2026_27":
            required = {
                k: ("AUD/kL" if "usage" in k else "AUD/92 days")
                for k in (
                    "drinking_usage",
                    "drought_usage",
                    "water_service",
                    "wastewater",
                    "stormwater_house",
                    "stormwater_unit",
                )
            }
            domain = "sydneywater.com.au"
        else:
            raise ValueError("No audited tariff schema for this source identifier.")
        if not official_domain(s.url, {domain}) or not required.keys() <= s.values.keys():
            raise ValueError("Source domain or required tariff fields mismatch.")
        for k, unit in required.items():
            if (
                s.values[k].get("unit") != unit
                or not isinstance(s.values[k].get("value"), (int, float))
                or s.values[k]["value"] < 0
            ):
                raise ValueError("Tariff value/unit mismatch: " + k)
    for value in s.values.values():
        if not isinstance(value, dict) or not {"value", "unit", "evidence"} <= value.keys():
            raise ValueError("Each value requires a unit and numerical evidence.")
        if s.source_category == "OFFICIAL_INDEX" and value["unit"] not in ("index points", "%"):
            raise ValueError("ABS PPI is an index, never AUD/m².")
    return s


def load_sources() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((DATA / "verified").glob("*.json"))]


def tariffs(project):
    if project.building_type == "Apartment Building" and project.tariff_mode != "user":
        raise ValueError("Use whole-building utility rates and aggregate fixed charges; single-house references do not represent an apartment block.")
    if project.tariff_mode == "user":
        return dict(
            electricity_rate=project.electricity_rate,
            electricity_daily=project.electricity_daily,
            water_rate=project.water_rate,
            water_fixed=project.water_fixed_annual,
        )
    sources = {s["id"]: s for s in load_sources()}
    for key in ("aer_2026_27", "sydney_water_2026_27"):
        validate_source(sources[key], project.price_date)
    aer, water = sources["aer_2026_27"]["values"], sources["sydney_water_2026_27"]["values"]

    def w(k):
        return water[k]["value"]

    # Provider publishes maximum quarterly charges for 92 days; normalize to 365 days.
    fixed = (w("water_service") if project.water_connected else 0) + (
        w("wastewater") if project.wastewater_connected else 0
    )
    if project.stormwater:
        fixed += w("stormwater_unit" if project.building_type == "Apartment" else "stormwater_house")
    return dict(
        electricity_rate=aer[project.zone + "_usage"]["value"],
        electricity_daily=aer[project.zone + "_supply"]["value"],
        water_rate=w("drought_usage" if project.drought_tariff else "drinking_usage"),
        water_fixed=fixed / 92 * 365,
    )
