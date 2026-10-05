"""The supplied catalogue remains explicitly indicative until reviewed."""
import json
from backend.app.research.sources import DATA
from backend.app.calculations.takeoff import takeoff
from backend.app.calculations.lcc import area_m2

REGION = DATA / "regions/sydney_nsw"


def catalogue():
    return json.loads((REGION / "measures.json").read_text(encoding="utf-8"))["measures"]


def measure_costs(p):
    geometry = takeoff(area_m2(p.area, p.area_unit), p.floors, p.bathrooms, p.solar_kw, p.tank_kl, p.quantity_overrides)
    q = geometry["quantities"]
    if "solar_pv" in p.selected_measures and "solar_pv" not in p.code_required_measures and q["solar_kw"] > q["max_solar_kw"] + 1e-9:
        raise ValueError(f"Solar array exceeds indicative roof capacity of {q['max_solar_kw']:.2f} kW. Reduce size or override roof area.")
    records = []
    # Unprovided prices are conspicuous placeholders; no unverified rebate is applied.
    settings = json.loads((REGION / "assumptions.json").read_text(encoding="utf-8"))
    missing = settings["missing_upgrade_premiums"]
    for m in catalogue():
        if m["id"] not in p.selected_measures:
            continue
        quantities = [(key, value) for key, value in m["reference_quantities_220m2"].items() if key in q and value]
        scale = sum(q[key] / value for key, value in quantities) / len(quantities) if quantities else 1
        if m["id"] == "rainwater":
            scale = q["tank_kl"] / 5
        baseline = m["default_premium_at_reference"]
        fallback = baseline if baseline is not None else missing[m["id"]]
        if fallback is None and m["id"] not in p.price_overrides and m["id"] not in p.code_required_measures:
            raise ValueError("Sustainable material alternatives require your own installed difference quote. No price or benefit is assumed.")
        indicative = (fallback or 0) * scale
        own = m["id"] in p.price_overrides
        required = m["id"] in p.code_required_measures
        value = 0 if required else p.price_overrides.get(m["id"], indicative * settings["price_range_factors"][p.price_scenario])
        key, reference = quantities[0] if quantities else ("units", 1)
        quantity = q.get(key, 1)
        if m["id"] in ("insulation", "airtightness_shading"):
            key, quantity = "reference_package_ratio", scale
        records.append(dict(id=m["id"], name=m["name"], premium=value, low=value if own or required else indicative * settings["price_range_factors"]["low"],
                            high=value if own or required else indicative * settings["price_range_factors"]["high"], quantity=quantity, quantity_driver=key,
                            unit_price=value / quantity if quantity else 0, basis="installed upgrade difference, GST included",
                            includes_labour=True, includes_margin=True, gst_included=True, labour_added=0, margin_added=0,
                            gst_added=0, incentive=0, code_required=required, badge="Code required" if required else "Your price" if own else "Indicative",
                            source="Your installed upgrade quote" if own else "Supplied package / explicitly labelled placeholder",
                            price_date="2026-10-05", replacements=m["replacements"], scale=scale))
    return records, geometry
