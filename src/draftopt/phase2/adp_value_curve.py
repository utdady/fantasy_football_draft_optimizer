"""Frozen ADP → structural value curve for P2.2C (immutable constants).

Chosen BEFORE any actual-PPR scoring. Do not retune after seeing outcomes.
See results/PHASE2_P22C_ADP_STRUCTURAL.md.
"""

from __future__ import annotations

# --- IMMUTABLE for P2.2C 2024 FFC 12-team experiment ---
# Linear invert of ADP into a monotone season-value proxy.
# Not a claim about true fantasy projection quality.
CURVE_ID = "adp_linear_v1_2024_ffc12"
V_MAX = 350.0
# ADP at / beyond this maps to floor value (deep pool).
ADP_REF = 180.0
# Minimum value so numerics never go non-positive.
V_FLOOR = 1.0


def adp_to_value(adp: float | None) -> float | None:
    """Map ADP to structural value; None if ADP missing."""
    if adp is None:
        return None
    a = float(adp)
    if a <= 1.0:
        return float(V_MAX)
    if a >= ADP_REF:
        return float(V_FLOOR)
    # v = V_MAX * (ADP_REF - adp) / (ADP_REF - 1)
    v = V_MAX * (ADP_REF - a) / (ADP_REF - 1.0)
    return float(max(V_FLOOR, min(V_MAX, v)))


def curve_meta() -> dict:
    return {
        "curve_id": CURVE_ID,
        "formula": "v = clamp(V_FLOOR, V_MAX * (ADP_REF - adp) / (ADP_REF - 1), V_MAX)",
        "V_MAX": V_MAX,
        "ADP_REF": ADP_REF,
        "V_FLOOR": V_FLOOR,
        "frozen": True,
        "note": "Do not change after outcome evaluation begins.",
    }
