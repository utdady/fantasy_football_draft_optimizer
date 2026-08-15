"""P2.2C Branch B ladder: B vs D on frozen V3-A values DB.

Primary contrast: B−D. Same 60 (slot, seed). Pick-change count is first-class.
Requires Gates P∧N. Do not retune or invent B.1.1 after seeing results.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots
from draftopt.config import EVAL_DB_PATH, get_roster_preset
from draftopt.phase2 import connect_eval
from draftopt.phase2.coverage_p22c import _run_one_with_id
from draftopt.phase2.onestep_continuation import CONSTRUCTION_ID
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

STRATEGIES = ("adp_v3a", "adp_v3bb")
CONTRACTS = {
    "full": frozenset(),
    "ex_dst": frozenset({"DST"}),
    "ex_dst_te": frozenset({"DST", "TE"}),
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick_ids(picks: list[dict]) -> list[str]:
    return [str(p.get("player_id")) for p in picks]


def _first_divergence(d_picks: list[dict], a_picks: list[dict]) -> dict | None:
    n = min(len(d_picks), len(a_picks))
    for i in range(n):
        if str(d_picks[i].get("player_id")) != str(a_picks[i].get("player_id")):
            return {
                "pick_index": i,
                "round": d_picks[i].get("round") or a_picks[i].get("round"),
                "d_name": d_picks[i].get("name"),
                "d_pos": d_picks[i].get("position"),
                "b_name": a_picks[i].get("name"),
                "b_pos": a_picks[i].get("position"),
            }
    return None


def _n_changed_picks(d_picks: list[dict], a_picks: list[dict]) -> int:
    d_ids = _pick_ids(d_picks)
    a_ids = _pick_ids(a_picks)
    n = min(len(d_ids), len(a_ids))
    return sum(1 for i in range(n) if d_ids[i] != a_ids[i]) + abs(
        len(d_ids) - len(a_ids)
    )


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
            d_picks = by_s["adp_v3a"]["picks"]
            a_picks = by_s["adp_v3bb"]["picks"]
            n_changed = _n_changed_picks(d_picks, a_picks)
            diverged = n_changed > 0
            metrics: dict[str, dict] = {}
            for cname, excl in CONTRACTS.items():
                scores = {s: _attributed_starter(by_s[s], excl) for s in STRATEGIES}
                metrics[cname] = {
                    "adp_v3a": scores["adp_v3a"],
                    "adp_v3bb": scores["adp_v3bb"],
                    "construction_gain_b_minus_d": round(
                        scores["adp_v3bb"] - scores["adp_v3a"], 4
                    ),
                }
            pairs.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "metrics": metrics,
                    "n_changed_picks": n_changed,
                    "board_diverged": diverged,
                    "first_divergence": _first_divergence(d_picks, a_picks),
                    "picks": {s: by_s[s]["picks"] for s in STRATEGIES},
                    "starter_by_pos": {
                        s: by_s[s]["starter_by_pos"] for s in STRATEGIES
                    },
                }
            )

    ladder: dict[str, dict] = {}
    for cname in CONTRACTS:
        ad = [p["metrics"][cname]["construction_gain_b_minus_d"] for p in pairs]
        abs_rows = {}
        for s in STRATEGIES:
            vals = [p["metrics"][cname][s] for p in pairs]
            abs_rows[s] = {
                "mean_starter": round(statistics.mean(vals), 4),
                "median_starter": round(statistics.median(vals), 4),
            }
        ladder[cname] = {
            "by_strategy": abs_rows,
            "b_minus_d": _dist_summary(ad),
        }

    n_boards_changed = sum(1 for p in pairs if p["board_diverged"])
    total_changed_picks = sum(p["n_changed_picks"] for p in pairs)
    first_rounds = [
        p["first_divergence"]["round"]
        for p in pairs
        if p["first_divergence"] and p["first_divergence"].get("round") is not None
    ]
    first_round_hist = dict(sorted(Counter(first_rounds).items()))
    d_to_b_pos = Counter()
    for p in pairs:
        fd = p["first_divergence"]
        if not fd:
            continue
        d_to_b_pos[f"{fd.get('d_pos')}→{fd.get('b_pos')}"] += 1

    pick_change = {
        "n_boards": len(pairs),
        "n_boards_with_pick_change": n_boards_changed,
        "n_boards_identical": len(pairs) - n_boards_changed,
        "total_changed_picks": total_changed_picks,
        "mean_changed_picks_per_board": round(
            total_changed_picks / len(pairs), 4
        )
        if pairs
        else None,
        "first_divergence_round_hist": first_round_hist,
        "first_divergence_d_to_b_pos": dict(d_to_b_pos),
    }

    bd_full = ladder["full"]["b_minus_d"]
    mean_bd = bd_full["mean"]
    med_bd = bd_full["median"]
    wr_bd = bd_full["win_rate"]
    p10_bd = bd_full["p10"]
    flags: list[str] = []

    if n_boards_changed == 0:
        flags.append(
            "b_policy_inert — 0/60 pick changes; reject this operationalization; "
            "do not auto-lengthen horizon"
        )
    elif mean_bd is not None and mean_bd <= 0:
        flags.append(
            "b_active_but_b_minus_d_nonpositive — falsified; freeze; no tune; "
            "mandatory light where/why still useful"
        )
    elif (
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
            "b_minus_d_supportive_provisional — MANDATORY mechanism audit "
            "(where/what/concentration/sanity) before any OC claim; no horizon↑"
        )
    elif mean_bd is not None and mean_bd > 0 and (p10_bd is None or p10_bd < -100):
        flags.append(
            "mean_up_tail_worse — tradeoff; freeze B; mandatory audit; no B.1.1 / λ"
        )
    else:
        flags.append(
            "b_minus_d_mixed — mandatory where/why if any pick changes; do not retune"
        )

    return {
        "stage": "P2.2C_v3bb_ladder",
        "created_at": _utcnow(),
        "curve_id": CURVE_ID,
        "construction_id": CONSTRUCTION_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "Branch B: identical frozen V3-A values; "
            "M_B = M_D(p|R) + C(R∪{p}) "
            f"({CONSTRUCTION_ID}). Primary contrast B−D. Gates P∧N required."
        ),
        "note": (
            "Do not invent B.1.1 or lengthen horizon. "
            "Divergence is evidence the mechanism is active, not that it is correct. "
            "Positive B−D still requires mandatory where/why audit."
        ),
        "contract": contract_meta(),
        "strategies": list(STRATEGIES),
        "v3a_draft_db": str(v3a_path),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_pairs": len(pairs),
        "pick_change": pick_change,
        "interpretation_flags": flags,
        "ladder": ladder,
        "pairs": pairs,
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    pc = report["pick_change"]
    lines = [
        "# P2.2C Branch B ladder (B−D)",
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
        "## Pick-change (first-class)",
        "",
        f"- boards with ≥1 changed pick: **{pc['n_boards_with_pick_change']}/"
        f"{pc['n_boards']}**",
        f"- boards identical to D: {pc['n_boards_identical']}",
        f"- total changed picks: {pc['total_changed_picks']}",
        f"- mean changed picks/board: {pc['mean_changed_picks_per_board']}",
        f"- first divergence round hist: `{pc['first_divergence_round_hist']}`",
        f"- first divergence D→B pos: `{pc.get('first_divergence_d_to_b_pos')}`",
        "",
    ]
    for cname, title in (
        ("full", "Full starter PPR"),
        ("ex_dst", "Ex-DST"),
        ("ex_dst_te", "Ex-DST + TE"),
    ):
        block = report["ladder"][cname]
        bd = block["b_minus_d"]
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
                "### B−D",
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
            "| Outcome | Next |",
            "| --- | --- |",
            "| 0/60 pick changes | Policy-inert; reject operationalization |",
            "| Pick changes but B−D ≤ 0 | Active but falsified; freeze; no tune |",
            "| Pick changes + B−D > 0 | Mandatory where/why audit before OC claim |",
            "",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C Branch B B−D ladder")
    parser.add_argument("--v3a-draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3bb_ladder.md"),
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
