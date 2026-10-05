"""Rectangular house quantities. All geometric coefficients are indicative."""
import json
import math
from backend.app.research.sources import DATA


def takeoff(area, storeys, bathrooms, solar_kw=6.6, tank_kl=5, overrides=None):
    settings = json.loads((DATA / "regions/sydney_nsw/takeoff_assumptions.json").read_text())
    p = settings["plan"]
    footprint = area / storeys
    width = math.sqrt(footprint / p["aspect_ratio"])
    perimeter = 2 * width * (1 + p["aspect_ratio"])
    q = dict(footprint_m2=footprint, perimeter_m=perimeter, glazing_area_m2=area * p["glazing_share_of_gfa"],
             roof_area_m2=footprint * p["roof_area_factor"], ceiling_area_m2=footprint,
             catchment_area_m2=footprint * p["rainwater_catchment_factor"], conditioned_area_m2=area,
             hvac_capacity_kw=area * p["hvac_load_w_per_m2"] / 1000,
             solar_kw=solar_kw, tank_kl=tank_kl, units=1, light_points=math.ceil(area / p["light_point_area_m2"]),
             showers=bathrooms, toilets=bathrooms, taps=bathrooms * 2 + 2)
    allowed = set(q) | {"gross_wall_area_m2", "net_wall_area_m2", "envelope_area_m2", "shaded_glazing_area_m2"}
    if set(overrides or {}) - allowed:
        raise ValueError("Unknown quantity override")
    q.update(overrides or {})
    q["gross_wall_area_m2"] = (overrides or {}).get("gross_wall_area_m2", q["perimeter_m"] * p["wall_height_m"] * storeys)
    q["net_wall_area_m2"] = (overrides or {}).get("net_wall_area_m2", max(0, q["gross_wall_area_m2"] - q["glazing_area_m2"] - p["door_area_m2"]))
    q["envelope_area_m2"] = (overrides or {}).get("envelope_area_m2", q["gross_wall_area_m2"] + q["ceiling_area_m2"])
    q["shaded_glazing_area_m2"] = (overrides or {}).get("shaded_glazing_area_m2", q["glazing_area_m2"] * p["shaded_glazing_share"])
    q["solar_panel_area_m2"] = q["solar_kw"] * p["solar_panel_area_m2_per_kw"]
    q["max_solar_kw"] = min(13.2, q["roof_area_m2"] * p["usable_solar_roof_share"] / p["solar_panel_area_m2_per_kw"])
    return dict(quantities=q, overrides=list(overrides or {}), status="indicative", formulas=settings)
