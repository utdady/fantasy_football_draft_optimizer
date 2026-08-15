"""V3-B.1 cross-position alternative: best remaining empty-need other position.

Frozen by results/V3B_CROSS_POSITION_OPERATIONALIZATION.md
(construction_id crosspos_empty_need_nextbest_v1).

N(R) = positions with live starter/FLEX capacity (same FLEX accounting as
adp_feasible). a* = max calibrated value among remaining q with
pos(q) in N(R) and pos(q) != pos(p). Not same-position replacement (B.0).
"""

from __future__ import annotations

from typing import Any

CONSTRUCTION_ID = "crosspos_empty_need_nextbest_v1"

_FIXED = ("QB", "RB", "WR", "TE", "DST", "K")
_FLEX_ELIGIBLE = frozenset({"RB", "WR", "TE"})


def empty_capacity_positions(
    counts: dict[str, int],
    slots: dict[str, int],
) -> frozenset[str]:
    """
    Empty-capacity position set N(R).

    1. Fixed positions with def(x) > 0.
    2. If FLEX capacity remains after extras→FLEX fill, add {RB, WR, TE}.
    """
    n: set[str] = set()
    for pos in _FIXED:
        need = max(0, int(slots.get(pos) or 0) - int(counts.get(pos, 0)))
        if need > 0:
            n.add(pos)

    rb_extra = max(0, int(counts.get("RB", 0)) - int(slots.get("RB") or 0))
    wr_extra = max(0, int(counts.get("WR", 0)) - int(slots.get("WR") or 0))
    te_extra = max(0, int(counts.get("TE", 0)) - int(slots.get("TE") or 0))
    flex_cap = int(slots.get("FLEX") or 0)
    flex_filled = min(flex_cap, rb_extra + wr_extra + te_extra)
    flex_need = max(0, flex_cap - flex_filled)
    if flex_need > 0:
        n.update(_FLEX_ELIGIBLE)
    return frozenset(n)


def crosspos_empty_need_nextbest(
    *,
    player_id: str,
    position: str | None,
    remaining: list[dict[str, Any]],
    counts: dict[str, int],
    slots: dict[str, int],
    value_key: str = "calibrated_value",
) -> dict[str, Any]:
    """
    a* = max calibrated value among remaining players in N(R) at a different
    position than the candidate. If none: value=0 and cross_alt_missing=True.

    Does not read outcomes. Does not use same-position replacement.
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
        val = row.get(value_key)
        if val is None:
            continue
        others.append(row)

    if not others:
        return {
            "cross_alt": 0.0,
            "cross_alt_missing": True,
            "cross_alt_player_id": None,
            "cross_alt_name": None,
            "cross_alt_position": None,
            "empty_capacity_positions": sorted(need_set),
            "construction_id": CONSTRUCTION_ID,
        }

    best = max(others, key=lambda r: float(r[value_key]))
    return {
        "cross_alt": float(best[value_key]),
        "cross_alt_missing": False,
        "cross_alt_player_id": str(best.get("player_id")),
        "cross_alt_name": best.get("name"),
        "cross_alt_position": (best.get("position") or "").upper(),
        "empty_capacity_positions": sorted(need_set),
        "construction_id": CONSTRUCTION_ID,
    }
