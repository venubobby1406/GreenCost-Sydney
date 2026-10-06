from dataclasses import replace
from backend.app.calculations.lcc import (
    Scenario,
    Component,
    Assumptions,
    area_m2,
    maintenance_cost,
    indexed_cost,
    compare,
    sensitivity,
)
from backend.app.research.sources import load_sources


def scenarios(p, rates):
    area = area_m2(p.area, p.area_unit)
    capital = p.conventional_cost if p.conventional_cost is not None else (p.cost_per_m2 or 0) * area
    if p.cost_mode == "detailed":
        capital = sum(m.quantity * m.unit_cost for m in p.materials) + p.other_construction
    elif p.historical_index:
        index = next(s for s in load_sources() if s["id"] == "abs_ppi_2026")["values"]["building_construction"]["value"]
        capital = indexed_cost(capital, p.historical_index, index)
    sustainable_capital = p.sustainable_cost if p.sustainable_cost is not None else capital * (1 + p.premium)
    maintenance = maintenance_cost(capital, p.maintenance_annual, p.maintenance_fraction)
    if p.cost_mode == "detailed":
        maintenance += sum(m.maintenance for m in p.materials)

    def components(which):
        explicit = tuple(
            Component(r.name, r.interval, r.cost, r.escalation) for r in p.replacements if r.scenario in ("both", which)
        )
        materials = tuple(
            Component(
                m.name, m.replacement_interval or m.service_life, m.quantity * m.unit_cost, p.maintenance_escalation
            )
            for m in p.materials
            if (m.replacement_interval or m.service_life) and p.cost_mode == "detailed"
        )
        return explicit + materials

    c = Scenario(
        capital,
        p.energy_kwh,
        p.water_kl,
        maintenance,
        **rates,
        replacements=components("conventional"),
        other=p.other_annual,
        disposal=p.disposal_conventional,
        residual=p.residual_conventional,
    )
    s = Scenario(
        sustainable_capital,
        p.energy_kwh * (1 - p.energy_reduction),
        p.water_kl * (1 - p.water_reduction),
        maintenance * (1 - p.maintenance_reduction),
        **rates,
        replacements=components("sustainable"),
        other=p.other_annual,
        disposal=p.disposal_sustainable,
        residual=p.residual_sustainable,
    )
    a = Assumptions(**{k: getattr(p, k) for k in Assumptions.__dataclass_fields__})
    if p.mode == "literature" and p.preset != "legacy_6star":
        fixed = p.gas_daily * 365 if p.gas_mj else 0
        c = replace(c, gas_annual=p.gas_mj * p.gas_rate + fixed)
        s = replace(s, gas_annual=p.gas_mj * (1 - p.energy_reduction) * p.gas_rate + fixed)
    if p.preset == "legacy_6star" and p.mode == "literature":
        from backend.app.calculations.legacy import year1_inputs, REPL_CONV, REPL_SUST
        y1c, y1s = year1_inputs(area, p.solar_kw, "rainwater" in p.features, capital, sustainable_capital)
        def legacy(base, y1, replacement):
            return replace(base, energy_override=y1["energy"] / (1 + a.energy_escalation),
                           water_kl=0, water_fixed=y1["water"] / (1 + a.water_escalation),
                           maintenance=y1["maint"] / (1 + a.maintenance_escalation),
                           replacements=tuple(Component("Legacy component", year, cost, 0, False) for year, cost in replacement.items()))
        c, s = legacy(c, y1c, REPL_CONV), legacy(s, y1s, REPL_SUST)
    elif p.mode == "itemised":
        from backend.app.services.catalogue import measure_costs
        from backend.app.calculations.energy import model
        measures, _ = measure_costs(p)
        selected = [m["id"] for m in measures if not m["code_required"]]
        energy = model(p, selected)
        baseline_replacements, sustainable_replacements = [], []
        for m in measures:
            if m["code_required"]:
                continue
            for scenario, target in (("baseline", baseline_replacements), ("upgrade", sustainable_replacements)):
                target.extend(Component(m["name"], r["year"], r["default"] * m["scale"], p.maintenance_escalation)
                              for r in m["replacements"][scenario])
        gas_fixed = p.gas_daily * 365 if p.gas_mj else 0
        c = replace(c, gas_annual=p.gas_mj * p.gas_rate + gas_fixed, replacements=c.replacements + tuple(baseline_replacements))
        s = replace(s, capital=capital + sum(m["premium"] for m in measures), energy_kwh=energy["grid_kwh"],
                    water_kl=energy["water_kl"], maintenance=maintenance,
                    gas_annual=energy["gas_mj"] * p.gas_rate + gas_fixed,
                    solar_credit=energy["export_kwh"] * p.feed_in_rate,
                    replacements=components("sustainable") + tuple(sustainable_replacements))
    return c, s, a


def assumptions(p, rates, c, s):
    rows = []

    def add(name, value, unit, source):
        rows.append(dict(name=name, value=value, unit=unit, source=source))

    user = "DEMO assumption — replace before project use" if p.input_quality == "demo" else "User / project input"
    research = "Project_Proposal_EPP.pdf p.5; EPP_LS.pdf pp.2–3 — fallback, not a performance guarantee"
    add("Area", area_m2(p.area, p.area_unit), "m²", user)
    add(
        "Conventional capital",
        c.capital,
        "AUD",
        user + ("; national ABS index ratio applied" if p.historical_index else ""),
    )
    add(
        "Sustainable capital",
        s.capital,
        "AUD",
        "Sum of selected installed upgrade differences (indicative unless quoted)" if p.mode == "itemised" else user if p.sustainable_cost is not None else "User-selected package premium applied to conventional capital",
    )
    for name, key in [("Annual electricity", "energy_kwh"), ("Annual water", "water_kl")]:
        add(name, getattr(p, key), "kWh/year" if key == "energy_kwh" else "kL/year", user)
    for key in (() if p.mode == "itemised" else ("energy_reduction", "water_reduction", "maintenance_reduction")):
        add(
            key.replace("_", " ").capitalize(),
            getattr(p, key) * 100,
            "%",
            research if p.performance_source == "research" else user,
        )
    for key in (
        "discount",
        "energy_escalation",
        "water_escalation",
        "maintenance_escalation",
        "other_escalation",
        "terminal_escalation",
    ):
        add(
            key.replace("_", " ").capitalize(),
            getattr(p, key) * 100,
            "%",
            user + "; editable financial assumption",
        )
    for key, value in rates.items():
        source = (
            ("aer_2026_27" if key.startswith("electricity") else "sydney_water_2026_27")
            if p.tariff_mode == "official"
            else "User tariff: " + p.tariff_note
        )
        if p.rates_snapshot is not None:
            source = "Captured input snapshot; verify the stated tariff source: " + source
        add(
            key.replace("_", " ").capitalize(),
            value,
            {
                "electricity_rate": "AUD/kWh",
                "electricity_daily": "AUD/day",
                "water_rate": "AUD/kL",
                "water_fixed": "AUD/year",
            }[key],
            source,
        )
    add(
        "Conventional annual maintenance",
        c.maintenance,
        "AUD/year",
        user + "; material maintenance added in detailed mode",
    )
    for r in p.replacements:
        add(f"Replacement: {r.name} ({r.scenario}), every {r.interval} years", r.cost, "AUD base cost", user)
    for key in (
        "other_annual",
        "disposal_conventional",
        "disposal_sustainable",
        "residual_conventional",
        "residual_sustainable",
    ):
        add(key.replace("_", " ").capitalize(), getattr(p, key), "AUD base cost", user)
    if p.mode == "itemised":
        from backend.app.services.catalogue import measure_costs
        from backend.app.calculations.energy import model
        measures, geometry = measure_costs(p)
        for m in measures:
            add("Upgrade: " + m["name"], m["premium"], "AUD installed difference", m["badge"] + "; " + m["source"])
        for name, value in geometry["quantities"].items():
            add("Takeoff: " + name, value, "see quantity name", "Your quantity" if name in p.quantity_overrides else "Indicative rectangular-plan assumption")
        energy = model(p, [m["id"] for m in measures if not m["code_required"]])
        for name in ("grid_kwh", "gas_mj", "generation_kwh", "self_use_kwh", "export_kwh", "water_kl", "rainwater_offset_kl"):
            add("Modelled: " + name, energy[name], "see quantity name / year", "Computed using indicative end-use assumptions")
    if p.gas_mj:
        for name in ("gas_mj", "gas_rate", "gas_daily"):
            add(name, getattr(p, name), "MJ/year" if name == "gas_mj" else "AUD/MJ" if name == "gas_rate" else "AUD/day", "User gas bill: " + p.gas_note)
    add("Solar export credit", p.feed_in_rate, "AUD/kWh", "User / indicative export tariff; verify retail plan")
    return rows


def compute_periods(c, s, a):
    return {str(n): compare(c, s, replace(a, years=n)) for n in (30, 40, 50)}


def compute_sensitivity(c, s, a):
    return sensitivity(c, s, a)


def research_outputs(p, rates, periods):
    from backend.app.services.catalogue import measure_costs
    from backend.app.calculations.energy import model
    from backend.app.calculations.lcc import compare
    output = dict(assumption_version=p.assumption_version, price_snapshot_date=p.price_date.isoformat())
    if p.budget_range:
        output["budget_scenarios"] = {}
        for label, cost in (("Low", p.budget_range[0]), ("Midpoint", sum(p.budget_range) / 2), ("High", p.budget_range[1])):
            variant = p.model_copy(update={"conventional_cost": cost, "budget_range": None})
            results = compute_periods(*scenarios(variant, rates))
            output["budget_scenarios"][label] = {n: {"conventional": r["conventional"]["total_lcc"], "sustainable": r["sustainable"]["total_lcc"], "savings_aud": r["savings_aud"]} for n, r in results.items()}
    if p.mode == "itemised":
        measures, geometry = measure_costs(p)
        selected = [m["id"] for m in measures if not m["code_required"]]
        output.update(measures=measures, takeoff=geometry, energy=model(p, selected))
        # Marginal contributions in catalogue order reconcile exactly for each horizon.
        contributions = {str(n): [] for n in (30, 40, 50)}
        initial = compute_periods(*scenarios(p.model_copy(update={"selected_measures": []}), rates))
        previous = {n: r["savings_aud"] for n, r in initial.items()}
        for n, value in previous.items():
            if abs(value) > 1e-9:
                contributions[n].append(dict(id="other_inputs", name="Other scenario inputs / terminal values",
                                             marginal_savings=value, standalone_savings=value, interaction_adjustment=0))
        prefix = []
        for measure in measures:
            prefix.append(measure["id"])
            variant = p.model_copy(update={"selected_measures": prefix})
            combined = compute_periods(*scenarios(variant, rates))
            standalone = compute_periods(*scenarios(p.model_copy(update={"selected_measures": [measure["id"]]}), rates))
            for n, rows in contributions.items():
                value = combined[n]["savings_aud"] - previous[n]
                rows.append(dict(id=measure["id"], name=measure["name"], marginal_savings=value,
                                 standalone_savings=standalone[n]["savings_aud"] - initial[n]["savings_aud"],
                                 interaction_adjustment=value - (standalone[n]["savings_aud"] - initial[n]["savings_aud"])))
                previous[n] = combined[n]["savings_aud"]
        output["measure_contributions"] = contributions
        output["price_sensitivity"] = {}
        for level in ("low", "median", "high"):
            computed = compute_periods(*scenarios(p.model_copy(update={"price_scenario": level}), rates))
            output["price_sensitivity"][level] = {n: dict(savings_aud=r["savings_aud"], break_even_year=r["break_even_year"]) for n, r in computed.items()}
    else:
        output["literature_scenarios"] = {}
        for label, premium, energy, water, maintenance in (("Low", .15, .2, .3, .1), ("Mid", .1, .3, .4, .2), ("High", .05, .4, .5, .25)):
            variant = p.model_copy(update=dict(preset="code_minimum_7star", sustainable_cost=None, premium=premium,
                                              energy_reduction=energy, water_reduction=water, maintenance_reduction=maintenance))
            c, s, a = scenarios(variant, rates)
            output["literature_scenarios"][label] = {str(n): compare(c, s, replace(a, years=n)) for n in (30, 40, 50)}
    return output
