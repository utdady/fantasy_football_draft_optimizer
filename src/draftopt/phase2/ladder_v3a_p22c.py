"""P2.2C V3-A ladder: A/B/C on structural DB, D on calibrated DB.

Same seeds/slots/opponents/outcomes. Load-bearing: D−B and D−C.
Do not retune the calibration map after seeing these numbers.
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
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)

BASE_STRATEGIES = ("adp_baseline", "adp_feasible", "adp_structural")
ALL_STRATEGIES = (*BASE_STRATEGIES, "adp_v3a")
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
    v3a_draft_db: Path | None = None,
    eval_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 5,
    seed0: int = 42,
) -> dict:
    draft_path = draft_db or P22C_DB_PATH
    v3a_path = v3a_draft_db or P22C_V3A_DB_PATH
    if not draft_path.is_file():
        raise FileNotFoundError(f"missing {draft_path}")
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

    conn = live_db.connect(draft_path)
    live_db.init(conn)
    v3a_conn = live_db.connect(v3a_path)
    live_db.init(v3a_conn)

    runs: dict[tuple[int, int, str], dict] = {}
    for slot in slots:
        for strategy in ALL_STRATEGIES:
            use_conn = v3a_conn if strategy == "adp_v3a" else conn
            for i in range(n_sims):
                seed = seed0 + i
                draft_id, _ = _run_one_with_id(
                    use_conn,
                    strategy_name=strategy,
                    user_slot=slot,
                    seed=seed,
                )
                scored = _score_user_roster(
                    use_conn,
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
    v3a_conn.close()

    pairs: list[dict] = []
    for slot in slots:
        for i in range(n_sims):
            seed = seed0 + i
            by_s = {s: runs[(slot, seed, s)] for s in ALL_STRATEGIES}
            metrics: dict[str, dict] = {}
            for cname, excl in CONTRACTS.items():
                scores = {
                    s: _attributed_starter(by_s[s], excl) for s in ALL_STRATEGIES
                }
                metrics[cname] = {
                    **{s: scores[s] for s in ALL_STRATEGIES},
                    "feasibility_gain": round(
                        scores["adp_feasible"] - scores["adp_baseline"], 4
                    ),
                    "valuation_gain_c_minus_b": round(
                        scores["adp_structural"] - scores["adp_feasible"], 4
                    ),
                    "calibration_gain_d_minus_b": round(
                        scores["adp_v3a"] - scores["adp_feasible"], 4
                    ),
                    "calibration_vs_structural_d_minus_c": round(
                        scores["adp_v3a"] - scores["adp_structural"], 4
                    ),
                    "total_d_vs_baseline": round(
                        scores["adp_v3a"] - scores["adp_baseline"], 4
                    ),
                }
            pairs.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "metrics": metrics,
                    "dst_fill": {s: _dst_fill(by_s[s]) for s in ALL_STRATEGIES},
                    "picks": {s: by_s[s]["picks"] for s in ALL_STRATEGIES},
                    "starter_by_pos": {
                        s: by_s[s]["starter_by_pos"] for s in ALL_STRATEGIES
                    },
                }
            )

    ladder: dict[str, dict] = {}
    for cname in CONTRACTS:
        d_minus_b = [p["metrics"][cname]["calibration_gain_d_minus_b"] for p in pairs]
        d_minus_c = [
            p["metrics"][cname]["calibration_vs_structural_d_minus_c"] for p in pairs
        ]
        c_minus_b = [p["metrics"][cname]["valuation_gain_c_minus_b"] for p in pairs]
        abs_rows = {}
        for s in ALL_STRATEGIES:
            vals = [p["metrics"][cname][s] for p in pairs]
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
            "valuation_gain_c_minus_b": _dist_summary(c_minus_b),
            "calibration_gain_d_minus_b": _dist_summary(d_minus_b),
            "calibration_vs_structural_d_minus_c": _dist_summary(d_minus_c),
            "left_tail_d_minus_c": {
                "p10": _dist_summary(d_minus_c)["p10"],
                "min": round(min(d_minus_c), 4) if d_minus_c else None,
                "n_negative": sum(1 for v in d_minus_c if v < 0),
                "n_pairs": len(d_minus_c),
            },
        }

    fill = {
        s: sum(1 for p in pairs if p["dst_fill"][s]) / len(pairs)
        for s in ALL_STRATEGIES
    }

    dmc = ladder["full"]["calibration_vs_structural_d_minus_c"]
    cmb = ladder["full"]["valuation_gain_c_minus_b"]
    flags: list[str] = []
    mean_dc = dmc["mean"]
    wr_dc = dmc["win_rate"]
    p10_dc = dmc.get("p10")
    p10_cb = cmb.get("p10")
    left_worse = (
        p10_dc is not None
        and p10_cb is not None
        and p10_dc < p10_cb - 20
    )
    if mean_dc is not None and mean_dc > 0 and left_worse:
        flags.append(
            "mean_up_left_tail_worse — tradeoff failure mode "
            "(do not treat as clean V3-A support)"
        )
    elif mean_dc is not None and mean_dc > 0 and wr_dc is not None and wr_dc >= 0.55:
        flags.append("d_minus_c_positive — calibration hypothesis supported (n=1 season)")
    elif mean_dc is not None and mean_dc <= 0:
        flags.append("d_minus_c_nonpositive — V3-A fails cleanly on this board")
    else:
        flags.append("d_minus_c_mixed")

    return {
        "stage": "P2.2C_v3a_ladder",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "v3a_snapshot_id": "2024-preseason-2024-09-01-ffc12-v3a",
        "curve_id": "adp_emp_pos_v1_train_2021_2023",
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "Same-board A/B/C/D under ppr_eval_v1_2024. D uses calibrated "
            "values (train 2021–2023 map); construction identical to structural. "
            "Load-bearing: D−B and D−C. Do not retune map from these results."
        ),
        "note": (
            "A/B/C run on draftopt_p22c.db; D on draftopt_p22c_v3a.db "
            "(identical ADP, different season_points). UI stays marginal."
        ),
        "contract": contract_meta(),
        "strategies": list(ALL_STRATEGIES),
        "draft_db": str(draft_path),
        "v3a_draft_db": str(v3a_path),
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
        "# P2.2C V3-A ladder (A/B/C/D)",
        "",
        f"- structural snapshot: `{report['snapshot_id']}`",
        f"- v3a snapshot: `{report['v3a_snapshot_id']}`",
        f"- curve: `{report['curve_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']}",
        "",
        report["claim"],
        "",
        report["note"],
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
        for s in ALL_STRATEGIES:
            row = block["by_strategy_vs_baseline"][s]
            lines.append(
                f"| `{s}` | {row['mean_delta_vs_baseline']:+.2f} | "
                f"{row['median_delta_vs_baseline']:+.2f} | "
                f"{row['win_rate_vs_baseline']:.0%} |"
            )
        cb = block["valuation_gain_c_minus_b"]
        db = block["calibration_gain_d_minus_b"]
        dc = block["calibration_vs_structural_d_minus_c"]
        tail = block["left_tail_d_minus_c"]
        lines.extend(
            [
                "",
                "### Causal / calibration deltas",
                "",
                "| Contrast | Mean | Median | Win rate | p10 | p90 |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
                f"| C−B (structural valuation) | {cb['mean']:+.2f} | {cb['median']:+.2f} | "
                f"{cb['win_rate']:.0%} | {cb['p10']:+.1f} | {cb['p90']:+.1f} |",
                f"| **D−B (calibration vs feasible)** | **{db['mean']:+.2f}** | "
                f"**{db['median']:+.2f}** | **{db['win_rate']:.0%}** | "
                f"{db['p10']:+.1f} | {db['p90']:+.1f} |",
                f"| **D−C (calibration vs structural)** | **{dc['mean']:+.2f}** | "
                f"**{dc['median']:+.2f}** | **{dc['win_rate']:.0%}** | "
                f"{dc['p10']:+.1f} | {dc['p90']:+.1f} |",
                "",
                f"Left tail D−C: min={tail['min']}, p10={tail['p10']}, "
                f"negative={tail['n_negative']}/{tail['n_pairs']}",
            ]
        )

    lines.extend(
        [
            "",
            "## Decision rule (do not retune map)",
            "",
            "| Outcome | Meaning |",
            "| --- | --- |",
            "| D−C > 0 and left tail improves | Calibration hypothesis supported (n=1) |",
            "| D−C ≤ 0 | V3-A fails cleanly → revisit construction |",
            "| Only one pocket | Localized hypothesis only |",
            "| Mean ↑, left tail worse | Tradeoff failure mode |",
            "",
            "- UI: `marginal`",
            "- evaluable: 0",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C V3-A A/B/C/D ladder")
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--v3a-draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_ladder.md"),
    )
    args = parser.parse_args()
    report = run_ladder(
        draft_db=args.draft_db,
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
