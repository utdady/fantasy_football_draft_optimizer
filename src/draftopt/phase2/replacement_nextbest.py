"""V3-B.0 replacement estimate: best remaining other at position.

Frozen by results/V3B_CONSTRUCTION_DESIGN.md (construction_id replacement_nextbest_v1).
Decision-time pool + calibrated values only — not a forecast of future availability.
"""

from __future__ import annotations

from typing import Any

CONSTRUCTION_ID = "replacement_nextbest_v1"


def replacement_nextbest(
    *,
    player_id: str,
    position: str | None,
    remaining: list[dict[str, Any]],
    value_key: str = "calibrated_value",
) -> dict[str, Any]:
    """
    r* = max calibrated value among remaining players at the same position
    excluding the candidate. If none exist: value=0 and replacement_missing=True.

    `remaining` entries must include player_id, position, and value_key.
    Does not read outcomes.
    """
    pid = str(player_id)
    pos = (position or "").upper()
    others: list[dict[str, Any]] = []
    for row in remaining:
        if str(row.get("player_id")) == pid:
            continue
        if (row.get("position") or "").upper() != pos:
            continue
        val = row.get(value_key)
        if val is None:
            continue
        others.append(row)

    if not others:
        return {
            "replacement": 0.0,
            "replacement_missing": True,
            "replacement_player_id": None,
            "replacement_name": None,
            "construction_id": CONSTRUCTION_ID,
        }

    best = max(others, key=lambda r: float(r[value_key]))
    return {
        "replacement": float(best[value_key]),
        "replacement_missing": False,
        "replacement_player_id": str(best.get("player_id")),
        "replacement_name": best.get("name"),
        "construction_id": CONSTRUCTION_ID,
    }
