"""P2.2C V3-B.1 ladder: B.1 vs D on frozen V3-A values DB.

Primary contrast: B.1−D (cross-position construction only). Same 60 (slot, seed).
Do not retune the map or invent B.1.1 after seeing results.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots
from draftopt.config import EVAL_DB_PATH, get_roster_preset
from draftopt.phase2 import connect_eval
from draftopt.phase2.coverage_p22c import _run_one_with_id
from draftopt.phase2.crosspos_empty_need import CONSTRUCTION_ID
from draftopt.phase2.delta_p22c import _load_outcomes, _score_user_roster
from draftopt.phase2.diagnose_delta_p22c import _attributed_starter, _dist_summary
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.v3a_calibration import CURVE_ID

STRATEGIES = ("adp_v3a", "adp_v3b1")
CONTRACTS = {
    "full": frozenset(),
    "ex_dst": frozenset({"DST"}),
    "ex_dst_te": frozenset({"DST", "TE"}),
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_ladder(
    *,
    v3a_draft_db: Path | None = None,
    eval_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 5,
    seed0: int = 42,
) -> dict:
    v3a_path = v3a_draft_db or P22C_V3A_DB_PATH
    if not v3a_path.is_file():
        raise FileNotFoundError(f"missing {v3a_path}")

    eval_conn = connect_eval(eval_db or EVAL_DB_PATH)
    outcomes = _load_outcomes(
        eval_conn,
        season=OUTCOME_SEASON,
        contract_id=CONTRACT_ID,
        source=OUTCOME_SOURCE,
    )
    eval_conn.close()

    roster_slots = get_roster_preset(ROSTER_PRESET)["slots"]
    slots = slots or list(range(1, N_TEAMS + 1))

    conn = live_db.connect(v3a_path)
    live_db.init(conn)

    runs: dict[tuple[int, int, str], dict] = {}
    for slot in slots:
        for strategy in STRATEGIES:
            for i in range(n_sims):
                seed = seed0 + i
                draft_id, _ = _run_one_with_id(
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
                runs[(slot, seed, strategy)] = {
                    "strategy": strategy,
                    "slot": slot,
                    "seed": seed,
                    **scored,
                }
    conn.close()

    pairs: list[dict] = []
    for slot in slots:
        for i in range(n_sims):
            seed = seed0 + i
            by_s = {s: runs[(slot, seed, s)] for s in STRATEGIES}
            metrics: dict[str, dict] = {}
            for cname, excl in CONTRACTS.items():
                scores = {s: _attributed_starter(by_s[s], excl) for s in STRATEGIES}
                metrics[cname] = {
                    "adp_v3a": scores["adp_v3a"],
                    "adp_v3b1": scores["adp_v3b1"],
                    "construction_gain_b1_minus_d": round(
                        scores["adp_v3b1"] - scores["adp_v3a"], 4
                    ),
                }
            pairs.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "metrics": metrics,
                    "picks": {s: by_s[s]["picks"] for s in STRATEGIES},
                    "starter_by_pos": {
                        s: by_s[s]["starter_by_pos"] for s in STRATEGIES
                    },
                }
            )

    ladder: dict[str, dict] = {}
    for cname in CONTRACTS:
        bd = [p["metrics"][cname]["construction_gain_b1_minus_d"] for p in pairs]
        abs_rows = {}
        for s in STRATEGIES:
            vals = [p["metrics"][cname][s] for p in pairs]
            abs_rows[s] = {
                "mean_starter": round(statistics.mean(vals), 4),
                "median_starter": round(statistics.median(vals), 4),
            }
        dist = _dist_summary(bd)
        ladder[cname] = {
            "by_strategy": abs_rows,
            "b1_minus_d": dist,
        }

    bd_full = ladder["full"]["b1_minus_d"]
    flags: list[str] = []
    mean_bd = bd_full["mean"]
    med_bd = bd_full["median"]
    wr_bd = bd_full["win_rate"]
    p10_bd = bd_full["p10"]
    n_zero = bd_full.get("n_zero") or 0
    n_pairs = bd_full.get("n") or 0
    if (
        mean_bd is not None
        and mean_bd > 0
        and med_bd is not None
        and med_bd > 0
        and wr_bd is not None
        and wr_bd > 0.5
        and p10_bd is not None
        and p10_bd > -50
    ):
        flags.append(
            "b1_minus_d_supportive — mean/median/WR up and p10 not severely negative"
        )
    elif mean_bd is not None and mean_bd > 0 and (p10_bd is None or p10_bd < -100):
        flags.append(
            "mean_up_tail_worse — tradeoff failure; do not invent B.1.1 / λ"
        )
    elif n_pairs > 0 and n_zero == n_pairs and abs(mean_bd or 0.0) < 1e-9:
        flags.append(
            "b1_minus_d_identical — scores change but picks match D on all boards; "
            "proxy inert (do not invent B.1.1)"
        )
    elif (
        mean_bd is not None
        and abs(mean_bd) < 15
        and wr_bd is not None
        and 0.4 <= wr_bd <= 0.6
    ):
        flags.append("b1_minus_d_near_zero — cross-pos proxy insufficient")
    elif mean_bd is not None and mean_bd <= 0:
        flags.append(
            "b1_minus_d_nonpositive — cross-pos construction hypothesis fails cleanly"
        )
    else:
        flags.append("b1_minus_d_mixed — inspect distribution; do not retune map")

    return {
        "stage": "P2.2C_v3b1_ladder",
        "created_at": _utcnow(),
        "curve_id": CURVE_ID,
        "construction_id": CONSTRUCTION_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "V3-B.1: identical frozen V3-A values; B.1 = D + M_B1 = M_D − a* "
            f"({CONSTRUCTION_ID}). Primary contrast B.1−D. No map retune."
        ),
        "note": (
            "Do not invent B.1.1 after seeing these numbers. "
            "Success requires mean, median, WR, and p10 — not mean alone."
        ),
        "contract": contract_meta(),
        "strategies": list(STRATEGIES),
        "v3a_draft_db": str(v3a_path),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_pairs": len(pairs),
        "interpretation_flags": flags,
        "ladder": ladder,
        "pairs": pairs,
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    lines = [
        "# P2.2C V3-B.1 ladder (B.1−D)",
        "",
        f"- curve: `{report['curve_id']}` (frozen)",
        f"- construction: `{report['construction_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']}",
        "",
        report["claim"],
        "",
        f"**{report['note']}**",
        "",
        f"Flags: {', '.join(report['interpretation_flags'])}",
        "",
    ]
    for cname, title in (
        ("full", "Full starter PPR"),
        ("ex_dst", "Ex-DST"),
        ("ex_dst_te", "Ex-DST + TE"),
    ):
        block = report["ladder"][cname]
        bd = block["b1_minus_d"]
        lines.extend(
            [
                f"## {title}",
                "",
                "| Strategy | mean starter | median starter |",
                "| --- | ---: | ---: |",
            ]
        )
        for s in STRATEGIES:
            row = block["by_strategy"][s]
            lines.append(
                f"| `{s}` | {row['mean_starter']:.2f} | {row['median_starter']:.2f} |"
            )
        lines.extend(
            [
                "",
                "### B.1−D",
                "",
                "| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {_fmt(bd['mean'])} | {_fmt(bd['median'])} | {bd['win_rate']:.0%} | "
                f"{_fmt(bd['p10'])} | {_fmt(bd['p25'])} | {_fmt(bd['p75'])} | "
                f"{_fmt(bd['p90'])} | {_fmt(bd['min'])} | {_fmt(bd['max'])} | "
                f"{bd['n_negative']}/{bd['n']} |",
                "",
            ]
        )
    lines.extend(
        [
            "## Decision rule (frozen)",
            "",
            "| Outcome | Meaning |",
            "| --- | --- |",
            "| B.1−D ↑ mean/median/WR and p10 OK | Cross-pos OC construction supported (n=1) |",
            "| Mean ↑, p10 worse | Tradeoff failure — do not invent B.1.1 |",
            "| B.1−D ≈ 0 | Cross-pos proxy insufficient |",
            "| B.1−D ≤ 0 | Hypothesis fails cleanly |",
            "",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C V3-B.1 B.1−D ladder")
    parser.add_argument("--v3a-draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3b1_ladder.md"),
    )
    args = parser.parse_args()
    report = run_ladder(
        v3a_draft_db=args.v3a_draft_db,
        eval_db=args.eval_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
