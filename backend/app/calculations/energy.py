"""Indicative end-use model; multiplicative effects prevent double counting."""
import json
from backend.app.research.sources import DATA


def model(p, selected):
    a = json.loads((DATA / "regions/sydney_nsw/assumptions.json").read_text())
    weights = a["end_use_baseline_kwh"]
    names = ("heating_cooling", "hot_water", "lighting", "appliances")
    baseline = {k: p.energy_kwh * weights[k] / sum(weights[n] for n in names) for k in names}
    end = baseline.copy()
    settings = a["energy_model"]
    envelope = 1
    for key, factor in settings["envelope_factors"].items():
        if key in selected:
            envelope *= factor
    end["heating_cooling"] *= envelope
    gas = p.gas_mj * envelope
    if "hvac" in selected:
        end["heating_cooling"] *= a["efficiency"]["hvac_eer_baseline"] / a["efficiency"]["hvac_eer_upgrade"]
    if "hot_water" in selected:
        end["hot_water"] /= a["efficiency"]["hot_water_cop_upgrade"]
    if "lighting" in selected and p.preset == "legacy_6star":
        end["lighting"] *= a["efficiency"]["led_lighting_factor"]
    if "smart_controls" in selected:
        end["appliances"] *= settings["controls_appliance_factor"]
    load = sum(end.values())
    generation = p.quantity_overrides.get("solar_kw", p.solar_kw) * a["solar"]["yield_kwh_per_kw_year"] if "solar_pv" in selected else 0
    share = a["solar"]["self_consumption_load_shifted" if "smart_controls" in selected else "self_consumption_unmanaged"]
    self_use = min(load, generation * share)
    exports = max(0, generation - self_use)
    water = p.water_kl * (settings["fixture_water_factor"] if "water_fixtures" in selected else 1)
    rain_offset = 0
    if "rainwater" in selected:
        from backend.app.calculations.takeoff import takeoff
        from backend.app.calculations.lcc import area_m2
        catchment = takeoff(area_m2(p.area, p.area_unit), p.floors, p.bathrooms, p.solar_kw, p.tank_kl, p.quantity_overrides)["quantities"]["catchment_area_m2"]
        rain_offset = min(water * settings["max_non_potable_share"],
                          catchment * settings["rainfall_m_per_year"] * settings["rainwater_capture_factor"],
                          a["water"]["rainwater_offset_kl_per_year_5kl_tank"] * p.quantity_overrides.get("tank_kl", p.tank_kl) / 5)
    return dict(baseline_end_uses=baseline, sustainable_end_uses=end, grid_kwh=max(0, load - self_use),
                gas_mj=gas, generation_kwh=generation, self_use_kwh=self_use, export_kwh=exports,
                water_kl=max(0, water - rain_offset), rainwater_offset_kl=rain_offset,
                assumptions_status="indicative", gas_model="Gas allocated to space heating; no fuel-switch claim. Enter all-electric bills for a fully electric baseline.")
