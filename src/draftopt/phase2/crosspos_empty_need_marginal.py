"""V3-B Branch A: cross-pos alternative by max M_D (not calibrated v).

Frozen by results/V3B_A_OPERATIONALIZATION.md
(construction_id crosspos_empty_need_marginal_v1).

Same N(R) / A(p) eligibility as B.1. q* = argmax M_D on A(p).
"""

from __future__ import annotations

from typing import Any

from draftopt.phase2.crosspos_empty_need import empty_capacity_positions

CONSTRUCTION_ID = "crosspos_empty_need_marginal_v1"


def _d_sort_key(row: dict[str, Any]) -> tuple:
    """Same descending preference as D / MarginalValueStrategy recommend."""
    return (
        -(float(row["marginal_d"]) if row.get("marginal_d") is not None else 0.0),
        row.get("adp_espn") is None,
        row.get("adp_espn") if row.get("adp_espn") is not None else 9999,
        row.get("ecr_fp_ppr") is None,
        row.get("ecr_fp_ppr") if row.get("ecr_fp_ppr") is not None else 9999,
        row.get("name") or "",
    )


def crosspos_empty_need_marginal(
    *,
    player_id: str,
    position: str | None,
    remaining: list[dict[str, Any]],
    counts: dict[str, int],
    slots: dict[str, int],
    marginal_key: str = "marginal_d",
) -> dict[str, Any]:
    """
    q* = argmax M_D among remaining players in N(R) at a different position.
    Returns M_D(q*) as cross_alt_marginal. Missing → 0 + cross_alt_missing=True.

    Does not read outcomes. Does not select by calibrated v.
    """
    pid = str(player_id)
    pos = (position or "").upper()
    need_set = empty_capacity_positions(counts, slots)

    others: list[dict[str, Any]] = []
    for row in remaining:
        if str(row.get("player_id")) == pid:
            continue
        qpos = (row.get("position") or "").upper()
        if qpos not in need_set:
            continue
        if qpos == pos:
            continue
        md = row.get(marginal_key)
        if md is None:
            continue
        others.append(row)

    if not others:
        return {
            "cross_alt_marginal": 0.0,
            "cross_alt_missing": True,
            "cross_alt_player_id": None,
            "cross_alt_name": None,
            "cross_alt_position": None,
            "empty_capacity_positions": sorted(need_set),
            "construction_id": CONSTRUCTION_ID,
        }

    best = min(others, key=_d_sort_key)
    return {
        "cross_alt_marginal": float(best[marginal_key]),
        "cross_alt_missing": False,
        "cross_alt_player_id": str(best.get("player_id")),
        "cross_alt_name": best.get("name"),
        "cross_alt_position": (best.get("position") or "").upper(),
        "empty_capacity_positions": sorted(need_set),
        "construction_id": CONSTRUCTION_ID,
    }
