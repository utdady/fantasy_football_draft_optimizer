"""P2.2C smoke: materialize → leakage → labeled ADP-curve replay (no actual PPR).

Scores starter points with the ADP-derived curve values only. That is a
decision-world sanity check, not empirical validity. Actual nflverse PPR
comparison is a later step and must stay gated behind evaluable=1.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots, run_one
from draftopt.phase2 import connect_eval, validate_snapshot_table
from draftopt.phase2.adp_value_curve import CURVE_ID, curve_meta
from draftopt.phase2.materialize_p22c import (
    P22C_DB_PATH,
    SNAPSHOT_ID,
    materialize,
)

STRATEGIES = ("adp_baseline", "adp_structural")
N_TEAMS = 12
# FFC 2024 meta.rounds=15; league_default without K has ~190 draftable vs 12*16=192.
N_ROUNDS = 15
DEFAULT_ROSTER = "league_default"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_smoke(
    *,
    raw_json: Path | None = None,
    eval_db: Path | None = None,
    draft_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 1,
    seed0: int = 42,
    rematerialize: bool = True,
) -> dict:
    draft_path = draft_db or P22C_DB_PATH
    mat: dict | None = None
    if rematerialize or not draft_path.is_file():
        mat = materialize(raw_json=raw_json, eval_path=eval_db, draft_db=draft_path)
    else:
        mat = {
            "snapshot_id": SNAPSHOT_ID,
            "draft_db": str(draft_path),
            "skipped_materialize": True,
        }

    from draftopt.config import EVAL_DB_PATH

    eval_path = eval_db or EVAL_DB_PATH
    eval_conn = connect_eval(eval_path)
    findings = validate_snapshot_table(eval_conn, SNAPSHOT_ID)
    snap = eval_conn.execute(
        """
        SELECT snapshot_id, snapshot_date, evaluable, pipeline_proof,
               validation_status, validation_reason
        FROM eval_snapshots WHERE snapshot_id = ?
        """,
        (SNAPSHOT_ID,),
    ).fetchone()
    eval_conn.close()
    if findings:
        raise RuntimeError(
            f"leakage findings: {[f.__dict__ for f in findings[:5]]}"
        )
    if snap is None:
        raise RuntimeError(f"missing snapshot {SNAPSHOT_ID}")
    if int(snap["evaluable"] or 0) != 0:
        raise RuntimeError("P2.2C smoke refuses evaluable=1 (outcomes not gated here)")

    slots = slots or [1]
    conn = live_db.connect(draft_path)
    live_db.init(conn)

    rows: list[dict] = []
    for slot in slots:
        if not 1 <= slot <= N_TEAMS:
            raise ValueError(f"slot {slot} out of 1..{N_TEAMS}")
        for strategy in STRATEGIES:
            for i in range(n_sims):
                seed = seed0 + i
                result = run_one(
                    conn,
                    strategy_name=strategy,
                    user_slot=slot,
                    roster_preset=DEFAULT_ROSTER,
                    seed=seed,
                    n_rounds=N_ROUNDS,
                    n_teams=N_TEAMS,
                    opponent_policy="noisy_adp",
                )
                rows.append(
                    {
                        "strategy": strategy,
                        "slot": slot,
                        "seed": seed,
                        "curve_starter_pts": result.starter_pts,
                        "roster_curve_pts": result.roster_proj,
                        "starter_rank": result.starter_rank,
                        "n_user_picks": len(result.picks),
                        "first_pick": result.picks[0]["name"] if result.picks else None,
                    }
                )
    conn.close()

    # Pairwise Δ on shared (slot, seed) — still ADP-curve points, not actual PPR.
    deltas: list[dict] = []
    by_key: dict[tuple[int, int], dict[str, float]] = {}
    for r in rows:
        key = (r["slot"], r["seed"])
        by_key.setdefault(key, {})[r["strategy"]] = r["curve_starter_pts"]
    for (slot, seed), pts in sorted(by_key.items()):
        if set(STRATEGIES) <= set(pts):
            d = pts["adp_structural"] - pts["adp_baseline"]
            deltas.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "delta_curve_starter": d,
                    "baseline": pts["adp_baseline"],
                    "structural": pts["adp_structural"],
                }
            )

    report = {
        "stage": "P2.2C_smoke",
        "created_at": _utcnow(),
        "snapshot_id": SNAPSHOT_ID,
        "evaluable": 0,
        "decision_market": "FFC",
        "league_size": N_TEAMS,
        "value_signal": CURVE_ID,
        "scoring_note": (
            "curve_starter_pts use ADP-derived values aliased as ESPN projections "
            "in draft_db. NOT actual 2024 PPR. NOT production marginal."
        ),
        "curve": curve_meta(),
        "leakage": "pass",
        "n_findings": 0,
        "snapshot_meta": dict(snap),
        "materialize": mat,
        "n_teams": N_TEAMS,
        "n_rounds": N_ROUNDS,
        "roster_preset": DEFAULT_ROSTER,
        "strategies": list(STRATEGIES),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "runs": rows,
        "deltas_curve_only": deltas,
        "next_gate": (
            "Attach nflverse 2024 PPR outcomes and score Δ on actual points; "
            "keep evaluable=0 until coverage gates pass."
        ),
    }
    return report


def _md(report: dict) -> str:
    lines = [
        "# P2.2C smoke (decision world)",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- leakage: **{report['leakage']}**",
        f"- decision_market: {report['decision_market']} · league_size: {report['league_size']}",
        f"- value_signal: `{report['value_signal']}`",
        "",
        f"**{report['scoring_note']}**",
        "",
        "## Runs",
        "",
        "| strategy | slot | seed | curve starter | rank | first pick |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in report["runs"]:
        lines.append(
            f"| `{r['strategy']}` | {r['slot']} | {r['seed']} | "
            f"{r['curve_starter_pts']:.1f} | {r['starter_rank']} | {r['first_pick']} |"
        )
    lines.extend(["", "## Δ curve starter (structural − baseline)", ""])
    if not report["deltas_curve_only"]:
        lines.append("_none_")
    else:
        lines.append("| slot | seed | Δ | baseline | structural |")
        lines.append("| ---: | ---: | ---: | ---: | ---: |")
        for d in report["deltas_curve_only"]:
            lines.append(
                f"| {d['slot']} | {d['seed']} | {d['delta_curve_starter']:+.1f} | "
                f"{d['baseline']:.1f} | {d['structural']:.1f} |"
            )
    lines.extend(["", f"Next: {report['next_gate']}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C ADP-structural smoke runner")
    parser.add_argument("--raw-json", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1")
    parser.add_argument("--n-sims", type=int, default=1)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--no-rematerialize",
        action="store_true",
        help="Reuse existing draft_db if present",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_smoke.md"),
    )
    args = parser.parse_args()
    report = run_smoke(
        raw_json=args.raw_json,
        eval_db=args.eval_db,
        draft_db=args.draft_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
        rematerialize=not args.no_rematerialize,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
