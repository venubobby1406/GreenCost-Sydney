"""Deterministic ISO 15686-5 style discounted cash flow engine (NumPy)."""
import numpy as np
from typing import Any, Dict, Optional

QUALITY_RATE = {"project_home": 2400.0, "custom_mid": 3200.0, "architectural": 4200.0}
REPL_CONV = {12: 1800.0, 15: 3500.0}
REPL_SUST = {10: 750.0, 12: 2200.0, 15: 3800.0}
SUPPLY_DAILY, WATER_FIXED, SOLAR_KW_REF = 1.50, 987.16, 6.6


def year1_inputs(gfa, solar_kw, tank, capex_conv, capex_sust,
                 import_rate=0.325, fit=0.05, water_rate=3.41):
    """Year-1 OpEx for both builds, calibrated to the spec at 220 m2 / 6.6 kW."""
    s = gfa / 220.0
    supply = SUPPLY_DAILY * 365
    conv_e = supply + 5200 * s * import_rate
    load = 7090 * s                       # sustainable-home load (1,450 import + 5,640 self-use at ref)
    k = solar_kw / SOLAR_KW_REF
    imp = max(0.0, load - 5640 * s * k)
    exp = 4200 * s * k
    sust_e = supply + imp * import_rate - exp * fit
    w_conv = 200 * water_rate + WATER_FIXED
    w_sust = (115 if tank else 200) * water_rate + WATER_FIXED
    return (
        {"energy": conv_e, "water": w_conv, "maint": capex_conv * 0.005},
        {"energy": sust_e, "water": w_sust, "maint": capex_sust * 0.0036},
    )


def calculate_discounted_lcc(capex_conv, capex_sust, year_1_conv, year_1_sust,
                             lifespan=40, r=0.05, e=0.03, i_w=0.02, i_m=0.015,
                             replacements_conv: Optional[Dict[int, float]] = None,
                             replacements_sust: Optional[Dict[int, float]] = None) -> Dict[str, Any]:
    t = np.arange(1, lifespan + 1)
    df = (1.0 + r) ** -t
    esc = {"energy": (1 + e) ** (t - 1), "water": (1 + i_w) ** (t - 1), "maint": (1 + i_m) ** (t - 1)}

    def build(y1, repl):
        parts = {k: y1[k] * esc[k] for k in ("energy", "water", "maint")}
        rep = np.zeros(lifespan)
        for yr, c in (repl or {}).items():
            if 1 <= yr <= lifespan:
                rep[yr - 1] += c
        parts["replacements"] = rep
        return parts, sum(parts.values())

    pc, tc = build(year_1_conv, replacements_conv)
    ps, ts = build(year_1_sust, replacements_sust)
    sav = tc - ts
    dsav = sav * df
    cum = np.cumsum(dsav)
    prem = capex_sust - capex_conv
    net_pos = cum - prem
    idx = np.where(net_pos >= 0)[0]
    be = int(idx[0] + 1) if idx.size else None

    lcc_c = float(capex_conv + np.sum(tc * df))
    lcc_s = float(capex_sust + np.sum(ts * df))
    crf = r * (1 + r) ** lifespan / ((1 + r) ** lifespan - 1)
    return {
        "initial_capex_conv": float(capex_conv), "initial_capex_sust": float(capex_sust),
        "initial_capex_premium": float(prem),
        "total_lcc_conv": lcc_c, "total_lcc_sust": lcc_s,
        "net_lifecycle_savings": lcc_c - lcc_s,
        "percentage_savings": (lcc_c - lcc_s) / lcc_c * 100.0,
        "break_even_year": be,
        "eauc_conv": lcc_c * crf, "eauc_sust": lcc_s * crf,
        "annual_schedules": [{
            "year": int(t[i]),
            "conv_energy": float(pc["energy"][i]), "conv_water": float(pc["water"][i]),
            "conv_maint": float(pc["maint"][i]), "conv_replacements": float(pc["replacements"][i]),
            "sust_energy": float(ps["energy"][i]), "sust_water": float(ps["water"][i]),
            "sust_maint": float(ps["maint"][i]), "sust_replacements": float(ps["replacements"][i]),
            "nominal_conv_opex": float(tc[i]), "nominal_sust_opex": float(ts[i]),
            "net_nominal_savings": float(sav[i]), "discount_factor": float(df[i]),
            "discounted_savings": float(dsav[i]),
            "cumulative_discounted_savings": float(cum[i]),
            "net_financial_position": float(net_pos[i]),
        } for i in range(lifespan)],
    }
