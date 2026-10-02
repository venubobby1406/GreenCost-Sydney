"""Auditable nominal cash flows, discounted to year zero. No AI dependencies."""

from dataclasses import dataclass, field, replace
from math import isfinite


def area_m2(value: float, unit: str = "m²") -> float:
    if unit not in ("m²", "ft²") or not isfinite(value) or value <= 0:
        raise ValueError("Supply a positive area in m² or ft²")
    return value * (0.092903 if unit == "ft²" else 1)


def discount_factor(rate: float, year: int) -> float:
    if not isfinite(rate) or rate <= -1 or year < 0:
        raise ValueError("Invalid discount rate or year")
    return (1 + rate) ** -year


def present_value(amount: float, rate: float, year: int) -> float:
    return amount * discount_factor(rate, year)


def escalate(amount: float, rate: float, year: int) -> float:
    return amount * (1 + rate) ** year


def energy_cost(kwh: float, usage_rate: float, daily_supply: float) -> float:
    return kwh * usage_rate + 365 * daily_supply


def water_cost(kl: float, usage_rate: float, fixed_annual: float) -> float:
    return kl * usage_rate + fixed_annual


def maintenance_cost(capital: float, annual: float | None, fraction: float) -> float:
    return annual if annual is not None else capital * fraction


def indexed_cost(historical_cost: float, historical_index: float, current_index: float) -> float:
    if historical_index <= 0 or current_index <= 0 or historical_cost < 0:
        raise ValueError("Positive matching-series indices and a nonnegative cost required")
    return historical_cost * current_index / historical_index


@dataclass(frozen=True)
class Component:
    name: str
    interval: int
    cost: float
    escalation: float = 0.025


@dataclass(frozen=True)
class Scenario:
    capital: float
    energy_kwh: float
    water_kl: float
    maintenance: float
    electricity_rate: float
    electricity_daily: float
    water_rate: float
    water_fixed: float
    replacements: tuple[Component, ...] = field(default_factory=tuple)
    other: float = 0
    disposal: float = 0
    residual: float = 0


@dataclass(frozen=True)
class Assumptions:
    years: int = 40
    discount: float = 0.05
    energy_escalation: float = 0.03
    water_escalation: float = 0.025
    maintenance_escalation: float = 0.025
    other_escalation: float = 0.025
    terminal_escalation: float = 0.025


def calculate(s: Scenario, a: Assumptions) -> dict:
    """Year t uses base prices * (1+g)^t; capital at t=0, expenses at year end.

    Fixed utility charges escalate with their respective utility rate. No replacement
    at the terminal year: an asset retired then does not need a new component.
    Disposal/residual are user-provided year-zero equivalents, escalated to N.
    """
    if a.years < 1 or a.years > 100 or not 0 <= a.discount <= 1:
        raise ValueError("Invalid study horizon or discount rate")
    totals = dict(
        capital=s.capital,
        energy=0.0,
        water=0.0,
        maintenance=0.0,
        replacement=0.0,
        other=0.0,
        disposal=0.0,
        residual=0.0,
    )
    rows = [
        dict(
            year=0,
            nominal_total=s.capital,
            pv_total=s.capital,
            cumulative_pv=s.capital,
            cumulative_nominal=s.capital,
            operating=0.0,
            capital=s.capital,
            energy=0.0,
            water=0.0,
            maintenance=0.0,
            replacement=0.0,
            other=0.0,
            disposal=0.0,
            residual=0.0,
            events=[],
        )
    ]
    for t in range(1, a.years + 1):
        events = [c for c in s.replacements if c.interval > 0 and t % c.interval == 0 and t < a.years]
        costs = dict(
            energy=escalate(energy_cost(s.energy_kwh, s.electricity_rate, s.electricity_daily), a.energy_escalation, t),
            water=escalate(water_cost(s.water_kl, s.water_rate, s.water_fixed), a.water_escalation, t),
            maintenance=escalate(s.maintenance, a.maintenance_escalation, t),
            replacement=sum(escalate(c.cost, c.escalation, t) for c in events),
            other=escalate(s.other, a.other_escalation, t),
            disposal=escalate(s.disposal, a.terminal_escalation, t) if t == a.years else 0.0,
            residual=-escalate(s.residual, a.terminal_escalation, t) if t == a.years else 0.0,
        )
        pv = {k: present_value(v, a.discount, t) for k, v in costs.items()}
        for k, v in pv.items():
            totals[k] += v
        total = sum(costs.values())
        rows.append(
            dict(
                year=t,
                capital=0.0,
                **costs,
                pv_total=sum(pv.values()),
                nominal_total=total,
                cumulative_pv=rows[-1]["cumulative_pv"] + sum(pv.values()),
                cumulative_nominal=rows[-1]["cumulative_nominal"] + total,
                operating=sum(costs[k] for k in ("energy", "water", "maintenance", "other")),
                events=[c.name for c in events],
            )
        )
    return dict(total_lcc=sum(totals.values()), components=totals, cashflows=rows)


def compare(conventional: Scenario, sustainable: Scenario, assumptions: Assumptions) -> dict:
    c, s = calculate(conventional, assumptions), calculate(sustainable, assumptions)
    saving = c["total_lcc"] - s["total_lcc"]
    break_even = next(
        (a["year"] for a, b in zip(c["cashflows"], s["cashflows"]) if b["cumulative_pv"] <= a["cumulative_pv"]), None
    )
    # Report subsequent reversals: first crossover does not promise permanent savings.
    reversals = [
        a["year"]
        for a, b in zip(c["cashflows"], s["cashflows"])
        if break_even is not None and a["year"] > break_even and b["cumulative_pv"] > a["cumulative_pv"]
    ]
    return dict(
        years=assumptions.years,
        conventional=c,
        sustainable=s,
        savings_aud=saving,
        savings_percent=saving / c["total_lcc"] * 100 if c["total_lcc"] else None,
        break_even_year=break_even,
        reversal_years=reversals,
        capital_difference=sustainable.capital - conventional.capital,
        component_savings={k: c["components"][k] - s["components"][k] for k in c["components"]},
    )


def sensitivity(c: Scenario, s: Scenario, a: Assumptions) -> list[dict]:
    cells = []
    for years in (30, 40, 50):
        for discount in (0.04, 0.05, 0.06, 0.07):
            for energy in (0.02, 0.03, 0.04, 0.05):
                result = compare(c, s, replace(a, years=years, discount=discount, energy_escalation=energy))
                cells.append(
                    dict(
                        years=years,
                        discount=discount,
                        energy_escalation=energy,
                        savings_aud=result["savings_aud"],
                        savings_percent=result["savings_percent"],
                        break_even_year=result["break_even_year"],
                    )
                )
    return cells
