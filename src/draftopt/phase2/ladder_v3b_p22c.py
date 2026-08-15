"""P2.2C V3-B ladder: E vs D on frozen V3-A values DB.

Primary contrast: E−D (construction only). Same 60 (slot, seed) pairs.
Do not retune the map or invent E.1 after seeing results.
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
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.replacement_nextbest import CONSTRUCTION_ID
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.v3a_calibration import CURVE_ID

STRATEGIES = ("adp_v3a", "adp_v3b")
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
                    "adp_v3b": scores["adp_v3b"],
                    "construction_gain_e_minus_d": round(
                        scores["adp_v3b"] - scores["adp_v3a"], 4
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
        ed = [p["metrics"][cname]["construction_gain_e_minus_d"] for p in pairs]
        abs_rows = {}
        for s in STRATEGIES:
            vals = [p["metrics"][cname][s] for p in pairs]
            abs_rows[s] = {
                "mean_starter": round(statistics.mean(vals), 4),
                "median_starter": round(statistics.median(vals), 4),
            }
        dist = _dist_summary(ed)
        ladder[cname] = {
            "by_strategy": abs_rows,
            "e_minus_d": dist,
        }

    ed_full = ladder["full"]["e_minus_d"]
    flags: list[str] = []
    mean_ed = ed_full["mean"]
    med_ed = ed_full["median"]
    wr_ed = ed_full["win_rate"]
    p10_ed = ed_full["p10"]
    # Compare to known D−C p10 from V3-A ladder context (~-268); require E−D p10
    # not catastrophically worse than 0 improvement — success needs all four.
    if (
        mean_ed is not None
        and mean_ed > 0
        and med_ed is not None
        and med_ed > 0
        and wr_ed is not None
        and wr_ed > 0.5
        and p10_ed is not None
        and p10_ed > -50
    ):
        flags.append(
            "e_minus_d_supportive — mean/median/WR up and p10 not severely negative"
        )
    elif mean_ed is not None and mean_ed > 0 and (p10_ed is None or p10_ed < -100):
        flags.append(
            "mean_up_tail_worse — tradeoff failure; do not invent E.1 / λ"
        )
    elif mean_ed is not None and abs(mean_ed) < 15 and wr_ed is not None and 0.4 <= wr_ed <= 0.6:
        flags.append("e_minus_d_near_zero — simple replacement insufficient")
    elif mean_ed is not None and mean_ed <= 0:
        flags.append("e_minus_d_nonpositive — construction hypothesis fails cleanly")
    else:
        flags.append("e_minus_d_mixed — inspect distribution; do not retune map")

    return {
        "stage": "P2.2C_v3b_ladder",
        "created_at": _utcnow(),
        "curve_id": CURVE_ID,
        "construction_id": CONSTRUCTION_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "V3-B.0: identical frozen V3-A values; E = D + M_E = M_D − r* "
            f"({CONSTRUCTION_ID}). Primary contrast E−D. No map retune."
        ),
        "note": (
            "Do not invent E.1 after seeing these numbers. "
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
        "# P2.2C V3-B ladder (E−D)",
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
        ed = block["e_minus_d"]
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
                "### E−D",
                "",
                "| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {_fmt(ed['mean'])} | {_fmt(ed['median'])} | {ed['win_rate']:.0%} | "
                f"{_fmt(ed['p10'])} | {_fmt(ed['p25'])} | {_fmt(ed['p75'])} | "
                f"{_fmt(ed['p90'])} | {_fmt(ed['min'])} | {_fmt(ed['max'])} | "
                f"{ed['n_negative']}/{ed['n']} |",
                "",
            ]
        )
    lines.extend(
        [
            "## Decision rule (frozen)",
            "",
            "| Outcome | Meaning |",
            "| --- | --- |",
            "| E−D ↑ mean/median/WR and p10 OK | Replacement-aware construction supported (n=1) |",
            "| Mean ↑, p10 worse | Tradeoff failure — do not invent E.1 |",
            "| E−D ≈ 0 | Simple replacement insufficient |",
            "| E−D ≤ 0 | Hypothesis fails cleanly |",
            "",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C V3-B E−D ladder")
    parser.add_argument("--v3a-draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3b_ladder.md"),
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
