"""P2.2C actual-PPR Δ: adp_baseline vs adp_structural under ppr_eval_v1_2024.

Same draft environment / seeds / roster rules. Scores user starters with
realized 2024 PPR (missing ≠ zero — fail closed). Does not set evaluable=1.

Claim scope: historical replay under a modeled opponent policy — not a
reconstruction of any real 2024 fantasy league.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots
from draftopt.config import EVAL_DB_PATH, get_roster_preset
from draftopt.lineup import lineup_ev
from draftopt.phase2 import connect_eval
from draftopt.phase2.coverage_p22c import _run_one_with_id
from draftopt.phase2.materialize_p22c import P22C_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    N_ROUNDS,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.smoke_p22c import STRATEGIES

OBSERVED = frozenset({"observed_zero", "observed_points"})


class MissingOutcomeError(RuntimeError):
    """Raised when a drafted player lacks an observed outcome (never coalesce to 0)."""


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_outcomes(eval_conn, *, season: int, contract_id: str, source: str) -> dict:
    status = {
        r["player_id"]: dict(r)
        for r in eval_conn.execute(
            """
            SELECT player_id, outcome_state, actual_ppr_points, notes
            FROM eval_outcome_status
            WHERE season = ? AND contract_id = ? AND source = ?
            """,
            (season, contract_id, source),
        ).fetchall()
    }
    points = {
        r["player_id"]: float(r["actual_ppr_points"])
        for r in eval_conn.execute(
            """
            SELECT player_id, actual_ppr_points, outcome_state
            FROM eval_outcomes
            WHERE season = ? AND source = ?
            """,
            (season, source),
        ).fetchall()
    }
    return {"status": status, "points": points}


def _score_user_roster(
    conn,
    draft_id: str,
    user_slot: int,
    *,
    outcomes: dict,
    roster_slots: dict[str, int],
) -> dict:
    rows = conn.execute(
        """
        SELECT pk.round, pk.overall, p.player_id, p.name, p.position
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        ORDER BY pk.overall
        """,
        (draft_id, user_slot),
    ).fetchall()
    status = outcomes["status"]
    points = outcomes["points"]
    roster: list[dict] = []
    pick_log: list[dict] = []
    for row in rows:
        pid = row["player_id"]
        st = status.get(pid)
        if st is None or st["outcome_state"] not in OBSERVED:
            state = (st or {}).get("outcome_state") or "absent_status"
            raise MissingOutcomeError(
                f"player {pid} ({row['name']}) outcome_state={state}; "
                "refusing COALESCE to 0"
            )
        if pid not in points:
            raise MissingOutcomeError(
                f"player {pid} observed in status but missing from eval_outcomes"
            )
        pts = float(points[pid])
        # Defense: status may say observed_zero with 0.0 — points table must agree
        roster.append(
            {
                "player_id": pid,
                "name": row["name"],
                "position": row["position"],
                "season_points": pts,
                "draft_round": int(row["round"]),
                "overall": int(row["overall"]),
            }
        )
        pick_log.append(
            {
                "round": int(row["round"]),
                "overall": int(row["overall"]),
                "player_id": pid,
                "name": row["name"],
                "position": (row["position"] or "?").upper(),
                "actual_ppr": pts,
            }
        )

    lined = lineup_ev(roster, roster_slots)
    starter_ids = {
        p["player_id"]
        for slot_players in lined.starters.values()
        for p in slot_players
    }
    by_pos: dict[str, float] = defaultdict(float)
    by_round_band: dict[str, float] = defaultdict(float)
    for p in roster:
        if p["player_id"] not in starter_ids:
            continue
        pos = (p["position"] or "?").upper()
        by_pos[pos] += float(p["season_points"])
        rnd = int(p["draft_round"])
        if rnd <= 5:
            band = "r1-5"
        elif rnd <= 10:
            band = "r6-10"
        else:
            band = "r11-15"
        by_round_band[band] += float(p["season_points"])

    return {
        "starter_actual_ppr": round(lined.total, 4),
        "roster_actual_ppr": round(sum(float(p["season_points"]) for p in roster), 4),
        "bench_actual_ppr": round(
            sum(
                float(p["season_points"])
                for p in roster
                if p["player_id"] not in starter_ids
            ),
            4,
        ),
        "starter_by_pos": dict(by_pos),
        "starter_by_round_band": dict(by_round_band),
        "n_starters": len(starter_ids),
        "picks": pick_log,
    }


def run_delta(
    *,
    draft_db: Path | None = None,
    eval_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 5,
    seed0: int = 42,
) -> dict:
    draft_path = draft_db or P22C_DB_PATH
    if not draft_path.is_file():
        raise FileNotFoundError(f"missing draft db {draft_path}; materialize_p22c first")

    eval_conn = connect_eval(eval_db or EVAL_DB_PATH)
    snap = eval_conn.execute(
        "SELECT evaluable FROM eval_snapshots WHERE snapshot_id = ?",
        (DECISION_SNAPSHOT_ID,),
    ).fetchone()
    if snap is None:
        raise RuntimeError(f"missing snapshot {DECISION_SNAPSHOT_ID}")
    if int(snap["evaluable"] or 0) != 0:
        raise RuntimeError("refusing Δ while evaluable=1 (unexpected)")

    # Require prior outcome coverage green (no missing in status for pool)
    miss = eval_conn.execute(
        """
        SELECT COUNT(*) AS n FROM eval_outcome_status
        WHERE season = ? AND contract_id = ? AND source = ?
          AND outcome_state IN ('missing_identity', 'missing_weeks')
        """,
        (OUTCOME_SEASON, CONTRACT_ID, OUTCOME_SOURCE),
    ).fetchone()["n"]
    if int(miss) > 0:
        raise RuntimeError(
            f"outcome coverage not green: {miss} missing_* rows; "
            "run outcome_coverage_p22c"
        )

    outcomes = _load_outcomes(
        eval_conn,
        season=OUTCOME_SEASON,
        contract_id=CONTRACT_ID,
        source=OUTCOME_SOURCE,
    )
    eval_conn.close()

    roster = get_roster_preset(ROSTER_PRESET)
    roster_slots = roster["slots"]
    slots = slots or list(range(1, N_TEAMS + 1))

    conn = live_db.connect(draft_path)
    live_db.init(conn)

    runs: list[dict] = []
    for slot in slots:
        if not 1 <= slot <= N_TEAMS:
            raise ValueError(f"slot {slot} out of 1..{N_TEAMS}")
        for strategy in STRATEGIES:
            for i in range(n_sims):
                seed = seed0 + i
                draft_id, _picks = _run_one_with_id(
                    conn,
                    strategy_name=strategy,
                    user_slot=slot,
                    seed=seed,
                )
                scored = _score_user_roster(
                    conn,
                    draft_id,
                    slot,
                    outcomes=outcomes,
                    roster_slots=roster_slots,
                )
                runs.append(
                    {
                        "strategy": strategy,
                        "slot": slot,
                        "seed": seed,
                        **scored,
                    }
                )
    conn.close()

    # Pairwise Δ on (slot, seed)
    paired: list[dict] = []
    by_key: dict[tuple[int, int], dict[str, dict]] = {}
    for r in runs:
        by_key.setdefault((r["slot"], r["seed"]), {})[r["strategy"]] = r
    for (slot, seed), strat_map in sorted(by_key.items()):
        if set(STRATEGIES) - set(strat_map):
            continue
        b = strat_map["adp_baseline"]
        s = strat_map["adp_structural"]
        d = s["starter_actual_ppr"] - b["starter_actual_ppr"]
        paired.append(
            {
                "slot": slot,
                "seed": seed,
                "baseline_starter": b["starter_actual_ppr"],
                "structural_starter": s["starter_actual_ppr"],
                "delta_starter": round(d, 4),
                "baseline_roster": b["roster_actual_ppr"],
                "structural_roster": s["roster_actual_ppr"],
                "delta_roster": round(
                    s["roster_actual_ppr"] - b["roster_actual_ppr"], 4
                ),
            }
        )

    deltas = [p["delta_starter"] for p in paired]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)

    by_slot: dict[int, list[float]] = defaultdict(list)
    for p in paired:
        by_slot[p["slot"]].append(p["delta_starter"])

    slot_summary = []
    for slot in sorted(by_slot):
        vals = by_slot[slot]
        slot_summary.append(
            {
                "slot": slot,
                "n": len(vals),
                "mean_delta": round(statistics.mean(vals), 4),
                "median_delta": round(statistics.median(vals), 4),
                "win_rate": round(sum(1 for v in vals if v > 0) / len(vals), 4),
            }
        )

    # Mean starter points by pos / round band (structural − baseline), averaged over pairs
    pos_keys = ("QB", "RB", "WR", "TE", "DST")
    band_keys = ("r1-5", "r6-10", "r11-15")
    pos_deltas: dict[str, list[float]] = defaultdict(list)
    band_deltas: dict[str, list[float]] = defaultdict(list)
    for (slot, seed), strat_map in by_key.items():
        if set(STRATEGIES) - set(strat_map):
            continue
        b, s = strat_map["adp_baseline"], strat_map["adp_structural"]
        for pos in pos_keys:
            pos_deltas[pos].append(
                float(s["starter_by_pos"].get(pos, 0.0))
                - float(b["starter_by_pos"].get(pos, 0.0))
            )
        for band in band_keys:
            band_deltas[band].append(
                float(s["starter_by_round_band"].get(band, 0.0))
                - float(b["starter_by_round_band"].get(band, 0.0))
            )

    def _mean_map(d: dict[str, list[float]]) -> dict[str, float]:
        return {k: round(statistics.mean(v), 4) if v else 0.0 for k, v in d.items()}

    summary = {
        "n_pairs": len(paired),
        "mean_delta_starter": round(statistics.mean(deltas), 4) if deltas else None,
        "median_delta_starter": round(statistics.median(deltas), 4) if deltas else None,
        "stdev_delta_starter": (
            round(statistics.stdev(deltas), 4) if len(deltas) > 1 else None
        ),
        "win_rate_structural": round(wins / len(deltas), 4) if deltas else None,
        "n_wins": wins,
        "n_losses": losses,
        "n_ties": ties,
        "mean_delta_by_pos": _mean_map(pos_deltas),
        "mean_delta_by_round_band": _mean_map(band_deltas),
        "by_slot": slot_summary,
    }

    return {
        "stage": "P2.2C_actual_ppr_delta",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "On the 2024 FFC 12-team preseason snapshot, under the specified "
            "simulated draft environment (noisy_adp opponents), ADP-structural "
            "produced the reported difference in realized starter PPR vs ADP "
            "baseline. This is not a reconstruction of a real 2024 fantasy league."
        ),
        "contract": contract_meta(),
        "strategies": list(STRATEGIES),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_teams": N_TEAMS,
        "n_rounds": N_ROUNDS,
        "roster_preset": ROSTER_PRESET,
        "opponent_policy": "noisy_adp",
        "missing_policy": "fail_closed_no_coalesce",
        "summary": summary,
        "pairs": paired,
        # Full pick logs are large; keep per-run starter totals only in runs_lite
        "runs_lite": [
            {
                "strategy": r["strategy"],
                "slot": r["slot"],
                "seed": r["seed"],
                "starter_actual_ppr": r["starter_actual_ppr"],
                "roster_actual_ppr": r["roster_actual_ppr"],
                "bench_actual_ppr": r["bench_actual_ppr"],
            }
            for r in runs
        ],
        "next": (
            "Inspect Δ. n=1 season / modeled opponents. Do not promote evaluable "
            "or start V3 from this alone. Optional: mapping-sensitivity rematch."
        ),
    }


def _md(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# P2.2C actual-PPR Δ (adp_structural − adp_baseline)",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- slots: {report['slots']} · n_sims: {report['n_sims']} · seed0: {report['seed0']}",
        f"- pairs: {s['n_pairs']}",
        "",
        f"**Claim scope:** {report['claim']}",
        "",
        "## Headline",
        "",
        f"| Metric | Value |",
        f"| --- | ---: |",
        f"| Mean Δ starter PPR | {s['mean_delta_starter']} |",
        f"| Median Δ starter PPR | {s['median_delta_starter']} |",
        f"| Stdev Δ | {s['stdev_delta_starter']} |",
        f"| Structural win rate | {s['win_rate_structural']} ({s['n_wins']}-{s['n_losses']}-{s['n_ties']}) |",
        "",
        "## By draft slot (mean Δ)",
        "",
        "| Slot | n | mean Δ | median Δ | win rate |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in s["by_slot"]:
        lines.append(
            f"| {row['slot']} | {row['n']} | {row['mean_delta']:+.2f} | "
            f"{row['median_delta']:+.2f} | {row['win_rate']:.0%} |"
        )
    lines.extend(
        [
            "",
            "## Mean Δ starter points by position (structural − baseline)",
            "",
            "| Pos | mean Δ |",
            "| --- | ---: |",
        ]
    )
    for pos, v in s["mean_delta_by_pos"].items():
        lines.append(f"| {pos} | {v:+.2f} |")
    lines.extend(
        [
            "",
            "## Mean Δ by draft-round band of starters",
            "",
            "| Band | mean Δ |",
            "| --- | ---: |",
        ]
    )
    for band, v in s["mean_delta_by_round_band"].items():
        lines.append(f"| {band} | {v:+.2f} |")
    lines.extend(["", f"**Next:** {report['next']}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P2.2C actual-PPR delta (baseline vs structural)"
    )
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_actual_ppr_delta.md"),
    )
    args = parser.parse_args()
    report = run_delta(
        draft_db=args.draft_db,
        eval_db=args.eval_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
