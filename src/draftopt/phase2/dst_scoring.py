"""Team-entity DST scoring for ppr_eval_v1_2024 (ESPN-like defaults)."""

from __future__ import annotations

from typing import Any, Mapping

from draftopt.phase2.scoring_contract import (
    DST_BLOCK,
    DST_FR,
    DST_INT,
    DST_PA_TIERS,
    DST_SACK,
    DST_SAFETY,
    DST_TD,
    DST_YA_TIERS,
)


def _f(row: Mapping[str, Any], key: str) -> float:
    val = row.get(key)
    if val is None:
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _tier_points(
    value: float,
    tiers: tuple[tuple[int | None, int | None, float], ...],
) -> float:
    v = float(value)
    for lo, hi, pts in tiers:
        if lo is not None and v < lo:
            continue
        if hi is not None and v > hi:
            continue
        return float(pts)
    return 0.0


def week_dst_points(
    *,
    points_allowed: float,
    yards_allowed: float,
    def_row: Mapping[str, Any],
) -> float:
    """
    ESPN-like D/ST week score from team defense counting stats + PA/YA.

    def_row: nflverse team_stats week row for the defense team.
    """
    pts = 0.0
    pts += DST_SACK * _f(def_row, "def_sacks")
    pts += DST_INT * _f(def_row, "def_interceptions")
    pts += DST_FR * _f(def_row, "fumble_recovery_opp")
    pts += DST_TD * (
        _f(def_row, "def_tds")
        + _f(def_row, "fumble_recovery_tds")
        + _f(def_row, "special_teams_tds")
    )
    pts += DST_SAFETY * _f(def_row, "def_safeties")
    pts += DST_BLOCK * (
        _f(def_row, "def_fg_blocks")
        + _f(def_row, "def_punt_blocks")
        + _f(def_row, "def_pat_blocks")
    )
    pts += _tier_points(points_allowed, DST_PA_TIERS)
    pts += _tier_points(yards_allowed, DST_YA_TIERS)
    return round(pts, 4)
