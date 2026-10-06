"""Budget allocations are editable allowances, not a quantity survey or market quote."""
from backend.app.calculations.takeoff import takeoff

# Delegated design assumptions. Material shares exclude labour, fees and contingency.
# These are deliberately labelled placeholders and never sold as Sydney benchmarks.
ELEMENTS = [
    ("concrete", "Concrete & foundations", "m³", "footprint_m2", .15, .08),
    ("timber", "Structural timber", "m³", "conditioned_area_m2", .08, .06),
    ("roofing", "Roof covering", "m²", "roof_area_m2", 1, .05),
    ("windows", "Windows & external glazing", "m²", "glazing_area_m2", 1, .06),
    ("insulation", "Wall insulation", "m²", "net_wall_area_m2", 1, .025),
    ("finishes", "Internal finishes & fittings", "allowance", "units", 1, .125),
]


def estimate_plan(request):
    low = request.budget_low
    high = request.budget_high if request.budget_high is not None else low
    midpoint = (low + high) / 2
    q = takeoff(request.area, request.floors, request.bathrooms)["quantities"]
    rows = []
    allocated = 0
    for key, name, unit, driver, factor, share in ELEMENTS:
        quantity = round(max(q[driver] * factor, .01), 3)
        total = round(midpoint * share, 2)
        allocated += total
        rows.append(dict(id=key, name=name, quantity=quantity, unit=unit,
                         unit_cost=total / quantity, total=total,
                         low=round(low * share, 2), high=round(high * share, 2),
                         status="Estimate", source="Editable budget allocation; placeholder, not supplier pricing",
                         service_life=None, replacement_interval=None, maintenance=0))
    other = round(midpoint - allocated, 2)
    return dict(budget_low=low, budget_high=high, midpoint=midpoint, rows=rows,
                other_construction=other,
                remaining=[dict(name="Labour & installation", amount=round(midpoint * .25, 2)),
                           dict(name="Services, site work, fees & contingency", amount=round(other - midpoint * .25, 2))],
                assumptions="Illustrative allocation only. Concrete volume assumes 0.15 m³ per footprint m²; timber assumes 0.08 m³ per floor m². Other quantities use the existing rectangular-plan takeoff. Drawings and quotes take priority. Land and finance excluded. No allowance establishes structural adequacy.")
