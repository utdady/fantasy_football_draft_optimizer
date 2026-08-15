"""P2.2C: ADP → ADP-feasible → structural ladder under ppr_eval_v1_2024.

Causal split:
  feasibility gain = adp_feasible − adp_baseline
  valuation gain   = adp_structural − adp_feasible   ← load-bearing

Same seeds/slots/opponents/outcomes as prior Δ. evaluable stays 0. Not V3.
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
from draftopt.phase2.delta_p22c import _load_outcomes, _score_user_roster
from draftopt.phase2.diagnose_delta_p22c import _attributed_starter, _dist_summary
from draftopt.phase2.materialize_p22c import P22C_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
STRATEGIES = ("adp_baseline", "adp_feasible", "adp_structural")
CONTRACTS = {
    "full": frozenset(),
    "ex_dst": frozenset({"DST"}),
    "ex_dst_te": frozenset({"DST", "TE"}),
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dst_fill(run: dict) -> bool:
    return any(p["position"] == "DST" for p in run["picks"])


def run_ladder(
    *,
    draft_db: Path | None = None,
    eval_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 5,
    seed0: int = 42,
) -> dict:
    draft_path = draft_db or P22C_DB_PATH
    if not draft_path.is_file():
        raise FileNotFoundError(f"missing {draft_path}")

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

    conn = live_db.connect(draft_path)
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
                scores = {
                    s: _attributed_starter(by_s[s], excl) for s in STRATEGIES
                }
                metrics[cname] = {
                    "adp_baseline": scores["adp_baseline"],
                    "adp_feasible": scores["adp_feasible"],
                    "adp_structural": scores["adp_structural"],
                    "feasibility_gain": round(
                        scores["adp_feasible"] - scores["adp_baseline"], 4
                    ),
                    "valuation_gain": round(
                        scores["adp_structural"] - scores["adp_feasible"], 4
                    ),
                    "total_vs_baseline": round(
                        scores["adp_structural"] - scores["adp_baseline"], 4
                    ),
                }
            pairs.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "metrics": metrics,
                    "dst_fill": {s: _dst_fill(by_s[s]) for s in STRATEGIES},
                    "picks": {s: by_s[s]["picks"] for s in STRATEGIES},
                    "starter_by_pos": {
                        s: by_s[s]["starter_by_pos"] for s in STRATEGIES
                    },
                }
            )

    ladder: dict[str, dict] = {}
    for cname in CONTRACTS:
        fg = [p["metrics"][cname]["feasibility_gain"] for p in pairs]
        vg = [p["metrics"][cname]["valuation_gain"] for p in pairs]
        tot = [p["metrics"][cname]["total_vs_baseline"] for p in pairs]
        # Absolute means vs baseline for each strategy
        abs_rows = {}
        for s in STRATEGIES:
            vals = [p["metrics"][cname][s] for p in pairs]
            # Δ vs baseline absolute starter points
            vs_base = [
                p["metrics"][cname][s] - p["metrics"][cname]["adp_baseline"]
                for p in pairs
            ]
            abs_rows[s] = {
                "mean_starter": round(statistics.mean(vals), 4),
                "mean_delta_vs_baseline": round(statistics.mean(vs_base), 4),
                "median_delta_vs_baseline": round(statistics.median(vs_base), 4),
                "win_rate_vs_baseline": round(
                    sum(1 for v in vs_base if v > 0) / len(vs_base), 4
                ),
            }
        ladder[cname] = {
            "by_strategy_vs_baseline": abs_rows,
            "feasibility_gain": _dist_summary(fg),
            "valuation_gain": _dist_summary(vg),
            "structural_vs_baseline": _dist_summary(tot),
        }

    fill = {
        s: sum(1 for p in pairs if p["dst_fill"][s]) / len(pairs) for s in STRATEGIES
    }

    # Decision flags on full-contract valuation gain
    vg_full = ladder["full"]["valuation_gain"]
    flags: list[str] = []
    mean_vg = vg_full["mean"]
    med_vg = vg_full["median"]
    wr_vg = vg_full["win_rate"]
    if mean_vg is not None and abs(mean_vg) < 15 and wr_vg is not None and 0.4 <= wr_vg <= 0.6:
        flags.append("valuation_gain_near_zero — structural ≈ feasible on full metric")
    elif mean_vg is not None and mean_vg >= 40 and wr_vg is not None and wr_vg >= 0.6:
        flags.append("valuation_gain_strong — structural >> feasible on full metric")
    elif mean_vg is not None and mean_vg >= 15:
        flags.append("valuation_gain_moderate")
    else:
        flags.append("valuation_gain_weak_or_negative")

    vg_ex = ladder["ex_dst"]["valuation_gain"]["mean"]
    if vg_ex is not None and vg_ex < 15:
        flags.append("ex_dst_valuation_gain_small — little edge beyond feasibility+DST fill")

    return {
        "stage": "P2.2C_adp_feasible_ladder",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "Decomposition of structural vs pure ADP into feasibility gain "
            "(adp_feasible − adp_baseline) and valuation gain "
            "(adp_structural − adp_feasible) under ppr_eval_v1_2024. "
            "Modeled opponents; n=1 season; not a real-league reconstruction."
        ),
        "note": (
            "Load-bearing comparison is valuation_gain (C−B), not total_vs_baseline (C−A). "
            "V3 still blocked. UI stays marginal."
        ),
        "contract": contract_meta(),
        "strategies": list(STRATEGIES),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_pairs": len(pairs),
        "dst_fill_rate": fill,
        "interpretation_flags": flags,
        "ladder": ladder,
        "pairs": pairs,
    }


def _md(report: dict) -> str:
    lines = [
        "# P2.2C ADP → ADP-feasible → structural ladder",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
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
        "## DST fill rates",
        "",
        "| Strategy | DST fill rate |",
        "| --- | ---: |",
    ]
    for s, rate in report["dst_fill_rate"].items():
        lines.append(f"| `{s}` | {rate:.0%} |")

    for cname, title in (
        ("full", "Full starter PPR"),
        ("ex_dst", "Ex-DST"),
        ("ex_dst_te", "Ex-DST + TE"),
    ):
        block = report["ladder"][cname]
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "### Mean Δ vs `adp_baseline`",
                "",
                "| Strategy | mean Δ vs baseline | median Δ | win rate |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for s in STRATEGIES:
            row = block["by_strategy_vs_baseline"][s]
            lines.append(
                f"| `{s}` | {row['mean_delta_vs_baseline']:+.2f} | "
                f"{row['median_delta_vs_baseline']:+.2f} | "
                f"{row['win_rate_vs_baseline']:.0%} |"
            )
        fg, vg = block["feasibility_gain"], block["valuation_gain"]
        lines.extend(
            [
                "",
                "### Causal split",
                "",
                "| Gain | Mean | Median | Win rate | p10 | p90 |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
                f"| Feasibility (B−A) | {fg['mean']:+.2f} | {fg['median']:+.2f} | "
                f"{fg['win_rate']:.0%} | {fg['p10']:+.1f} | {fg['p90']:+.1f} |",
                f"| **Valuation (C−B)** | **{vg['mean']:+.2f}** | **{vg['median']:+.2f}** | "
                f"**{vg['win_rate']:.0%}** | {vg['p10']:+.1f} | {vg['p90']:+.1f} |",
            ]
        )

    lines.extend(
        [
            "",
            "## Status",
            "",
            "- Phase 2: ladder artifact written; interpret valuation_gain (C−B) before V3",
            "- V3: 🔴 blocked until C−B is replicated / bounded beyond n=1",
            "- UI: `marginal`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C ADP-feasible ladder")
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_adp_feasible_ladder.md"),
    )
    args = parser.parse_args()
    report = run_ladder(
        draft_db=args.draft_db,
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
