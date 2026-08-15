"""P2.2C: attach 2024 nflverse outcomes under ppr_eval_v1_2024 (no Δ).

Writes weekly + season rows only for observed_* states. Missing identities
never receive actual_ppr_points=0. Does not set evaluable=1.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from draftopt.config import EVAL_DB_PATH
from draftopt.phase2 import connect_eval
from draftopt.phase2.dst_scoring import week_dst_points
from draftopt.phase2.ppr_scoring import week_ppr_points
from draftopt.phase2.scoring_contract import (
    CANON_TO_NFLVERSE_TEAM,
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    NFLVERSE_TEAM_ALIASES,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    SEASON_TYPE,
    contract_meta,
)
from draftopt.phase2.schema import migrate_eval_schema


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_nfl():
    try:
        import nflreadpy as nfl
    except ImportError as e:
        raise RuntimeError(
            "nflreadpy is required. pip install 'draftopt[eval]' or pip install nflreadpy"
        ) from e
    return nfl


def _to_records(df) -> list[dict[str, Any]]:
    if hasattr(df, "filter"):
        return df.to_dicts()
    return df.to_dict("records")


def load_player_weeks(season: int) -> list[dict[str, Any]]:
    nfl = _require_nfl()
    df = nfl.load_player_stats(season, summary_level="week")
    if hasattr(df, "filter"):
        import polars as pl

        df = df.filter(pl.col("season_type") == SEASON_TYPE)
    else:
        df = [r for r in _to_records(df) if r.get("season_type") == SEASON_TYPE]
        return df
    return df.to_dicts()


def load_roster_gsis(season: int) -> set[str]:
    nfl = _require_nfl()
    df = nfl.load_rosters([season])
    rows = _to_records(df)
    out: set[str] = set()
    for r in rows:
        g = r.get("gsis_id")
        if g:
            out.add(str(g))
    return out


def load_team_weeks(season: int) -> list[dict[str, Any]]:
    nfl = _require_nfl()
    df = nfl.load_team_stats(season, summary_level="week")
    if hasattr(df, "filter"):
        import polars as pl

        df = df.filter(pl.col("season_type") == SEASON_TYPE)
        return df.to_dicts()
    return [r for r in _to_records(df) if r.get("season_type") == SEASON_TYPE]


def load_reg_scores(season: int) -> dict[tuple[str, int], float]:
    """Map (nflverse_team, week) → points scored by that team (REG)."""
    nfl = _require_nfl()
    df = nfl.load_schedules([season])
    if hasattr(df, "filter"):
        import polars as pl

        df = df.filter(pl.col("game_type") == SEASON_TYPE)
        rows = df.to_dicts()
    else:
        rows = [r for r in _to_records(df) if r.get("game_type") == SEASON_TYPE]
    out: dict[tuple[str, int], float] = {}
    for r in rows:
        week = int(r.get("week") or 0)
        ht, at = r.get("home_team"), r.get("away_team")
        hs, as_ = r.get("home_score"), r.get("away_score")
        if ht is None or at is None or hs is None or as_ is None:
            continue
        out[(str(ht), week)] = float(hs)
        out[(str(at), week)] = float(as_)
    return out


def _canon_team(nflverse_team: str) -> str:
    t = (nflverse_team or "").upper()
    return NFLVERSE_TEAM_ALIASES.get(t, t)


def _nflverse_team(canon: str) -> str:
    t = (canon or "").upper()
    return CANON_TO_NFLVERSE_TEAM.get(t, t)


def attach_outcomes(
    conn,
    *,
    snapshot_id: str = DECISION_SNAPSHOT_ID,
    season: int = OUTCOME_SEASON,
    contract_id: str = CONTRACT_ID,
    source: str = OUTCOME_SOURCE,
) -> dict[str, Any]:
    migrate_eval_schema(conn)
    pulled_at = _utcnow()

    snap = conn.execute(
        "SELECT snapshot_id, evaluable FROM eval_snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if snap is None:
        raise RuntimeError(f"missing snapshot {snapshot_id}; materialize_p22c first")
    if int(snap["evaluable"] or 0) != 0:
        raise RuntimeError("refusing to mutate outcomes while evaluable=1")

    players = [
        dict(r)
        for r in conn.execute(
            """
            SELECT player_id, name, position, team
            FROM eval_snapshot_players WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        ).fetchall()
    ]
    map_rows = {
        r["player_id"]: dict(r)
        for r in conn.execute(
            "SELECT player_id, gsis_id, method FROM eval_player_map WHERE source = 'ffc'"
        ).fetchall()
    }

    weekly_players = load_player_weeks(season)
    roster_gsis = load_roster_gsis(season)
    team_weeks = load_team_weeks(season)
    scores = load_reg_scores(season)

    # Index player weeks by GSIS
    by_gsis: dict[str, list[dict]] = defaultdict(list)
    for raw in weekly_players:
        gsis = raw.get("player_id")
        if not gsis:
            continue
        by_gsis[str(gsis)].append(raw)

    # Index team weeks by nflverse team + week
    team_by_tw: dict[tuple[str, int], dict] = {}
    for raw in team_weeks:
        team = str(raw.get("team") or "")
        week = int(raw.get("week") or 0)
        team_by_tw[(team, week)] = raw

    # Expected REG weeks per team from schedules
    weeks_by_team: dict[str, set[int]] = defaultdict(set)
    for (team, week), _ in scores.items():
        weeks_by_team[team].add(week)

    week_rows: list[tuple] = []
    season_rows: list[tuple] = []
    status_rows: list[tuple] = []

    n_obs_pts = n_obs_zero = n_miss_id = n_miss_weeks = 0

    for p in players:
        pid = p["player_id"]
        pos = (p.get("position") or "").upper()
        meta = map_rows.get(pid) or {}

        if pos == "DST" or pid.startswith("dst:"):
            canon = pid.split(":", 1)[-1] if pid.startswith("dst:") else (p.get("team") or "")
            canon = canon.upper()
            nv = _nflverse_team(canon)
            expected = weeks_by_team.get(nv) or set()
            if not expected:
                status_rows.append(
                    (
                        season,
                        pid,
                        contract_id,
                        "missing_identity",
                        None,
                        None,
                        source,
                        f"no REG schedule weeks for team {nv}",
                        pulled_at,
                    )
                )
                n_miss_id += 1
                continue
            week_pts: list[float] = []
            have_weeks: set[int] = set()
            for week in sorted(expected):
                def_row = team_by_tw.get((nv, week))
                opp_row = None
                if def_row:
                    opp = def_row.get("opponent_team")
                    if opp:
                        opp_row = team_by_tw.get((str(opp), week))
                if def_row is None or opp_row is None:
                    continue
                opp_team = str(def_row.get("opponent_team") or "")
                pa = scores.get((opp_team, week))
                if pa is None:
                    continue
                ya = float(opp_row.get("passing_yards") or 0) + float(
                    opp_row.get("rushing_yards") or 0
                )
                pts = week_dst_points(
                    points_allowed=float(pa),
                    yards_allowed=ya,
                    def_row=def_row,
                )
                have_weeks.add(week)
                week_pts.append(pts)
                week_rows.append(
                    (
                        season,
                        week,
                        SEASON_TYPE,
                        pid,
                        None,
                        "DST",
                        canon,
                        pts,
                        source,
                        pulled_at,
                    )
                )
            if not have_weeks:
                status_rows.append(
                    (
                        season,
                        pid,
                        contract_id,
                        "missing_identity",
                        None,
                        None,
                        source,
                        "no team_stats weeks joined",
                        pulled_at,
                    )
                )
                n_miss_id += 1
                continue
            if have_weeks != expected:
                missing = sorted(expected - have_weeks)
                status_rows.append(
                    (
                        season,
                        pid,
                        contract_id,
                        "missing_weeks",
                        None,
                        None,
                        source,
                        f"incomplete REG weeks: missing {missing[:8]}",
                        pulled_at,
                    )
                )
                n_miss_weeks += 1
                continue
            total = round(sum(week_pts), 4)
            state = "observed_zero" if total == 0.0 else "observed_points"
            season_rows.append(
                (season, pid, total, len(week_pts), source, pulled_at, contract_id, state)
            )
            status_rows.append(
                (
                    season,
                    pid,
                    contract_id,
                    state,
                    total,
                    len(week_pts),
                    source,
                    None,
                    pulled_at,
                )
            )
            if state == "observed_zero":
                n_obs_zero += 1
            else:
                n_obs_pts += 1
            continue

        # Offense / K
        gsis = meta.get("gsis_id")
        if not gsis and pid.startswith("gsis:"):
            gsis = pid.split(":", 1)[-1]
        if not gsis:
            status_rows.append(
                (
                    season,
                    pid,
                    contract_id,
                    "missing_identity",
                    None,
                    None,
                    source,
                    "no gsis_id on map",
                    pulled_at,
                )
            )
            n_miss_id += 1
            continue

        gsis = str(gsis)
        weeks = by_gsis.get(gsis) or []
        if weeks:
            total = 0.0
            games = 0
            for raw in weeks:
                pts = week_ppr_points(raw)
                week = int(raw.get("week") or 0)
                total += pts
                if pts != 0.0 or (
                    raw.get("completions")
                    or raw.get("carries")
                    or raw.get("receptions")
                    or raw.get("fg_att")
                    or raw.get("attempts")
                ):
                    games += 1
                week_rows.append(
                    (
                        season,
                        week,
                        SEASON_TYPE,
                        pid,
                        gsis,
                        raw.get("position") or pos,
                        raw.get("recent_team") or raw.get("team"),
                        pts,
                        source,
                        pulled_at,
                    )
                )
            total = round(total, 4)
            state = "observed_zero" if total == 0.0 else "observed_points"
            season_rows.append(
                (season, pid, total, games, source, pulled_at, contract_id, state)
            )
            status_rows.append(
                (
                    season,
                    pid,
                    contract_id,
                    state,
                    total,
                    games,
                    source,
                    None,
                    pulled_at,
                )
            )
            if state == "observed_zero":
                n_obs_zero += 1
            else:
                n_obs_pts += 1
        elif gsis in roster_gsis:
            # On season roster, never appeared in weekly stat lines → legitimate 0
            season_rows.append(
                (season, pid, 0.0, 0, source, pulled_at, contract_id, "observed_zero")
            )
            status_rows.append(
                (
                    season,
                    pid,
                    contract_id,
                    "observed_zero",
                    0.0,
                    0,
                    source,
                    "on_roster_no_weekly_stats",
                    pulled_at,
                )
            )
            n_obs_zero += 1
        else:
            status_rows.append(
                (
                    season,
                    pid,
                    contract_id,
                    "missing_identity",
                    None,
                    None,
                    source,
                    "gsis not in weekly stats or season roster",
                    pulled_at,
                )
            )
            n_miss_id += 1

    # Replace prior rows for this season/source (and status for contract)
    conn.execute(
        "DELETE FROM eval_outcomes_weekly WHERE season = ? AND source = ?",
        (season, source),
    )
    conn.execute(
        "DELETE FROM eval_outcomes WHERE season = ? AND source = ?",
        (season, source),
    )
    conn.execute(
        "DELETE FROM eval_outcome_status WHERE season = ? AND contract_id = ? AND source = ?",
        (season, contract_id, source),
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
            season, player_id, actual_ppr_points, games_played, source, pulled_at,
            contract_id, outcome_state
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        season_rows,
    )
    conn.executemany(
        """
        INSERT INTO eval_outcome_status (
            season, player_id, contract_id, outcome_state, actual_ppr_points,
            games_played, source, notes, pulled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        status_rows,
    )
    conn.commit()

    return {
        "snapshot_id": snapshot_id,
        "season": season,
        "contract_id": contract_id,
        "source": source,
        "pulled_at": pulled_at,
        "evaluable": 0,
        "n_pool": len(players),
        "n_weekly_rows": len(week_rows),
        "n_season_outcome_rows": len(season_rows),
        "n_status_rows": len(status_rows),
        "n_observed_points": n_obs_pts,
        "n_observed_zero": n_obs_zero,
        "n_missing_identity": n_miss_id,
        "n_missing_weeks": n_miss_weeks,
        "contract": contract_meta(),
        "note": (
            "Outcomes attached only. No strategy Δ. evaluable remains 0. "
            "missing_* never stored as 0 in eval_outcomes."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C attach nflverse outcomes")
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--snapshot-id", default=DECISION_SNAPSHOT_ID)
    parser.add_argument("--season", type=int, default=OUTCOME_SEASON)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_outcomes_attach.md"),
    )
    args = parser.parse_args()
    conn = connect_eval(args.eval_db or EVAL_DB_PATH)
    report = attach_outcomes(
        conn, snapshot_id=args.snapshot_id, season=args.season
    )
    conn.close()
    md = [
        "# P2.2C outcomes attach",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- season: {report['season']}",
        f"- evaluable: **{report['evaluable']}**",
        f"- pool: {report['n_pool']}",
        f"- weekly rows: {report['n_weekly_rows']}",
        f"- season outcome rows (observed only): {report['n_season_outcome_rows']}",
        f"- observed_points: {report['n_observed_points']}",
        f"- observed_zero: {report['n_observed_zero']}",
        f"- missing_identity: {report['n_missing_identity']}",
        f"- missing_weeks: {report['n_missing_weeks']}",
        "",
        report["note"],
        "",
        "Next: `python -m draftopt.phase2.outcome_coverage_p22c`",
        "",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n".join(md))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
