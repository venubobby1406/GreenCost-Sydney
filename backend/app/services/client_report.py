"""Client-facing report content derived exclusively from calculated financial facts."""
from backend.app.services.explanation import money

LABELS = {"capital": "Initial building cost", "energy": "Electricity and gas", "water": "Water and service charges", "maintenance": "Routine maintenance", "replacement": "Equipment replacements", "other": "Other running costs", "disposal": "End-of-period removal", "residual": "Recovered-material credit"}


def report_content(result, years):
    p = result["project"]
    r = result["periods"][str(years)]
    c, s = r["conventional"], r["sustainable"]
    saving = r["savings_aud"]
    extra = r["capital_difference"]
    verdict = (f"The sustainable design costs {money(abs(saving))} less over {years} years." if saving > .005 else f"The sustainable design costs {money(abs(saving))} more over {years} years." if saving < -.005 else "Both designs have the same modelled total cost.")
    upfront = f"It needs {money(extra)} more at the start." if extra > .005 else f"It costs {money(abs(extra))} less at the start." if extra < -.005 else "Both designs have the same initial building cost."
    if r["break_even_year"] is None:
        recovery = f"The sustainable design does not become cheaper within the {years}-year study."
    elif extra <= 0:
        recovery = f"The sustainable design first costs no more than the conventional design in year {r['break_even_year']}; there is no extra initial investment to recover."
    else:
        recovery = f"The extra initial investment is first recovered in year {r['break_even_year']}, after allowing for the timing of future costs."
    if r.get("reversal_years"):
        recovery += " The cost advantage later reverses in year(s) " + ", ".join(map(str, r["reversal_years"])) + "; the first recovery is not a lasting advantage."
    drivers = sorted(((k, v) for k, v in r["component_savings"].items() if k != "capital" and abs(v) > .005), key=lambda item: abs(item[1]), reverse=True)
    findings = [upfront, recovery]
    if drivers:
        k, v = drivers[0]
        findings.append(f"The largest ongoing cost difference is {LABELS.get(k,k).lower()}: the sustainable design costs {money(abs(v))} {'less' if v > 0 else 'more'} over this period.")
    else:
        findings.append("No ongoing cost difference is modelled for this selection.")
    maint = r["component_savings"].get("maintenance", 0)
    findings.append("Routine maintenance costs are the same in both designs. No maintenance saving is assumed for this selection; equipment replacements are counted separately." if abs(maint) < .005 else f"Routine maintenance is modelled at {money(abs(maint))} {'less' if maint > 0 else 'more'} for the sustainable design over the study.")
    area = p["area"] * (.092903 if p["area_unit"] == "ft²" else 1)
    water = f"{p['water_kl'] * 1000:,.0f} L ({p['water_kl'] / 1000:g} million litres)"
    inputs = [["Building scope", p["building_type"] + " | postcode " + p["postcode"]], ["Total floor area", f"{area:,.1f} m2"], ["Number of floors", str(p["floors"])], ["Number of occupants", str(p["occupants"]) + (" (planning estimate)" if p.get("occupant_mode") == "estimate" else " (entered count)")], ["Annual grid electricity", f"{p['energy_kwh']:,.0f} kWh"], ["Annual water", water], ["Discount rate", f"{p['discount']:.1%} - future costs are converted to today's equivalent"], ["Annual electricity price growth", f"{p['energy_escalation']:.1%}"], ["Annual water / maintenance price growth", f"{p['water_escalation']:.1%} / {p['maintenance_escalation']:.1%}"], ["Price reference date", str(result.get("price_snapshot_date") or p["price_date"])]]
    if p.get("building_type") == "Apartment Building":
        inputs.insert(2, ["Entered area per floor" if p.get("area_basis") == "per_floor" else "Entered combined building area", f"{p.get('entered_area') or p['area']:,.1f} {p['area_unit']}"])
    cells = [v["savings_aud"] for v in result.get("sensitivity", []) if v["years"] == years]
    robustness = (f"Across the tested discount rates and electricity-price growth assumptions, sustainable total cost ranges from {money(abs(min(cells)))} {'less' if min(cells)>=0 else 'more'} to {money(abs(max(cells)))} {'less' if max(cells)>=0 else 'more'}. " + ("The sustainable design remains cheaper in all tested cases." if min(cells)>0 else "The sustainable design remains more expensive in all tested cases." if max(cells)<0 else "The preferred design changes in some tested cases; the conclusion depends on the assumptions.")) if cells else "Sensitivity results were not captured."
    next_steps = ["Ask your builder for conventional and upgraded installed quotes covering the same scope, including labour, GST and applicable rebates.", "Replace practice consumption with measured annual bills or a documented building design estimate. Check fixed charges across all included meters.", "Confirm upgrade performance, equipment life and replacement costs. Review roof suitability and the actual rainwater demand before purchase.", "Review the discount rate, price growth and end-of-period plan. Use the cash-flow CSV and saved project file for the full technical record."]
    warning = "EXAMPLE PROJECT: costs and usage are practice values. Replace them before presenting this as a project estimate." if p.get("input_quality") == "demo" else "Planning estimate: accuracy depends on the entered costs, usage and upgrade performance. Confirm project quotes before committing."
    from backend.app.services.catalogue import catalogue
    descriptions = {m["id"]:m.get("plain_description", "") for m in catalogue()}
    upgrades = []
    for m in result.get("measures", []):
        description = descriptions.get(m["id"], "Review this feature against your baseline specification.")
        if m["id"] == "rainwater":
            description = f"A {m['quantity']*1000:,.0f} L tank connected to suitable non-drinking uses to reduce mains water demand."
        elif m["id"] == "solar_pv":
            description = f"A {m['quantity']:g} kW system generates electricity for the building; unused generation can be exported."
        upgrades.append({**m, "description":description})
    name = p.get("name") or "Your project"
    scope = {"Residential House": "house", "Apartment Building": "apartment building", "Apartment": "apartment", "Commercial / Other": "commercial or other building"}.get(p["building_type"], p["building_type"].lower())
    narrative = [f"{name} is a {scope} in postcode {p['postcode']}, with a total floor area of {area:,.1f} m2. This report compares the conventional and sustainable designs for the same building over {years} years."]
    if upgrades:
        details = "; ".join(m["name"] + ": " + m["description"].rstrip(".") for m in upgrades[:4]) + "."
        if len(upgrades) > 4:
            details += f" The comparison also includes {len(upgrades)-4} other upgrades listed below."
        narrative.append("The selected sustainable features are " + details)
    else:
        narrative.append("The sustainable design uses the construction and running-cost assumptions entered for this project. No individually priced upgrades were selected.")
    narrative.append(f"The conventional design starts at {money(c['components']['capital'])}, while the sustainable design starts at {money(s['components']['capital'])}. Including running costs, maintenance, replacements and end-of-period costs, the {years}-year totals are {money(c['total_lcc'])} and {money(s['total_lcc'])}, respectively, in today's equivalent money. " + verdict)
    narrative.append(" ".join(findings[1:]))
    return dict(upgrades=upgrades, project=p, period=r, verdict=verdict, findings=findings, project_explanation=narrative, inputs=inputs, robustness=robustness, next_steps=next_steps, warning=warning)
