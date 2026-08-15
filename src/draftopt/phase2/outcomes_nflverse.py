"""Ingest nflverse weekly player stats → weekly + season actual PPR."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from draftopt.phase2.ppr_scoring import week_ppr_points


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_weekly_rows(season: int) -> list[dict[str, Any]]:
    try:
        import nflreadpy as nfl
    except ImportError as e:
        raise RuntimeError(
            "nflreadpy is required for outcome ingest. "
            "pip install 'draftopt[eval]' or pip install nflreadpy"
        ) from e

    df = nfl.load_player_stats(season, summary_level="week")
    # Regular season only for redraft season totals (common league default).
    if hasattr(df, "filter"):
        import polars as pl

        df = df.filter(pl.col("season_type") == "REG")
        records = df.to_dicts()
    else:
        records = [r for r in df.to_dict("records") if r.get("season_type") == "REG"]
    return records


def ingest_season_outcomes(
    conn: sqlite3.Connection,
    *,
    season: int,
    source: str = "nflverse_computed",
    gsis_to_player_id: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Store weekly PPR and season aggregates.

    player_id: prefer mapped canonical id via gsis; else gsis:{gsis_id}.
    """
    pulled_at = _utcnow()
    weekly = load_weekly_rows(season)
    gsis_to_player_id = gsis_to_player_id or {}

    week_rows: list[tuple] = []
    season_acc: dict[str, dict[str, Any]] = {}

    for raw in weekly:
        gsis = raw.get("player_id")  # nflverse weekly uses GSIS in player_id
        if not gsis:
            continue
        gsis = str(gsis)
        pid = gsis_to_player_id.get(gsis) or f"gsis:{gsis}"
        pts = week_ppr_points(raw)
        week = int(raw.get("week") or 0)
        st = str(raw.get("season_type") or "REG")
        week_rows.append(
            (
                season,
                week,
                st,
                pid,
                gsis,
                raw.get("position"),
                raw.get("recent_team") or raw.get("team"),
                pts,
                source,
                pulled_at,
            )
        )
        acc = season_acc.setdefault(
            pid,
            {"points": 0.0, "games": 0, "gsis_id": gsis},
        )
        acc["points"] += pts
        if pts != 0.0 or (raw.get("completions") or raw.get("carries") or raw.get("receptions") or raw.get("fg_att")):
            acc["games"] += 1

    conn.execute(
        "DELETE FROM eval_outcomes_weekly WHERE season = ? AND source = ?",
        (season, source),
    )
    conn.execute(
        "DELETE FROM eval_outcomes WHERE season = ? AND source = ?",
        (season, source),
    )
    conn.executemany(
        """
        INSERT INTO eval_outcomes_weekly (
            season, week, season_type, player_id, gsis_id, position, team,
            actual_ppr_points, source, pulled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        week_rows,
    )
    conn.executemany(
        """
        INSERT INTO eval_outcomes (
            season, player_id, actual_ppr_points, games_played, source, pulled_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (season, pid, round(acc["points"], 4), acc["games"], source, pulled_at)
            for pid, acc in season_acc.items()
        ],
    )
    conn.commit()
    return {
        "season": season,
        "source": source,
        "n_weekly_rows": len(week_rows),
        "n_players": len(season_acc),
        "pulled_at": pulled_at,
    }
