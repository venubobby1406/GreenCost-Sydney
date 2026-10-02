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
        user if p.sustainable_cost is not None else "User-selected package premium applied to conventional capital",
    )
    for name, key in [("Annual electricity", "energy_kwh"), ("Annual water", "water_kl")]:
        add(name, getattr(p, key), "kWh/year" if key == "energy_kwh" else "kL/year", user)
    for key in ("energy_reduction", "water_reduction", "maintenance_reduction"):
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
    return rows


def compute_periods(c, s, a):
    return {str(n): compare(c, s, replace(a, years=n)) for n in (30, 40, 50)}


def compute_sensitivity(c, s, a):
    return sensitivity(c, s, a)
