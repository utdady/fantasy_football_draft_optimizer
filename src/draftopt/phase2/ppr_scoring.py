"""Auditable ESPN-style PPR fantasy points from box-score counting stats.

We compute points ourselves (do not treat nflverse fantasy_points_ppr as ground
truth). Optionally compare to nflverse's column as a diagnostic.
"""

from __future__ import annotations

from typing import Any, Mapping


def _f(row: Mapping[str, Any], key: str) -> float:
    val = row.get(key)
    if val is None:
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def week_ppr_points(row: Mapping[str, Any]) -> float:
    """
    Skill-position + kicker PPR (ESPN-like defaults).

    Passing: 0.04/yd, 4/TD, -2/INT, 2/2pt
    Rushing: 0.1/yd, 6/TD, 2/2pt
    Receiving: 1/rec, 0.1/yd, 6/TD, 2/2pt
    Fumbles lost: -2
    Special teams TD (player): 6
    Kicking: FG 0-39 = 3, 40-49 = 4, 50+ = 5; XP = 1; missed FG = 0
    """
    pts = 0.0
    pts += 0.04 * _f(row, "passing_yards")
    pts += 4.0 * _f(row, "passing_tds")
    pts += -2.0 * _f(row, "passing_interceptions")
    pts += 2.0 * _f(row, "passing_2pt_conversions")

    pts += 0.1 * _f(row, "rushing_yards")
    pts += 6.0 * _f(row, "rushing_tds")
    pts += 2.0 * _f(row, "rushing_2pt_conversions")

    pts += 1.0 * _f(row, "receptions")
    pts += 0.1 * _f(row, "receiving_yards")
    pts += 6.0 * _f(row, "receiving_tds")
    pts += 2.0 * _f(row, "receiving_2pt_conversions")

    pts += -2.0 * _f(row, "sack_fumbles_lost")
    pts += -2.0 * _f(row, "rushing_fumbles_lost")
    pts += -2.0 * _f(row, "receiving_fumbles_lost")
    # Prefer total if present and component cols absent noise — still add ST TD.
    pts += 6.0 * _f(row, "special_teams_tds")

    pts += 3.0 * _f(row, "fg_made_0_19")
    pts += 3.0 * _f(row, "fg_made_20_29")
    pts += 3.0 * _f(row, "fg_made_30_39")
    pts += 4.0 * _f(row, "fg_made_40_49")
    pts += 5.0 * _f(row, "fg_made_50_59")
    pts += 5.0 * _f(row, "fg_made_60_")
    pts += 1.0 * _f(row, "pat_made") if "pat_made" in row else 1.0 * _f(row, "xp_made")

    return round(pts, 4)


def season_ppr_from_weeks(week_points: list[float]) -> float:
    return round(sum(week_points), 4)
