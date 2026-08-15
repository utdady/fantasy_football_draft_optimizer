"""P2.2C Δ mechanism audit: same 60 pairs, alternate attribution (no new seeds).

1) Attribution ladder: full / ex-DST / ex-DST+TE
2) DST pick audit (identity, round, actual PPR, concentration)
3) Δ distribution percentiles

Replays the same seed0/slots/n_sims as delta_p22c (deterministic RNG) and
persists pick-level data. Does not change strategies or evaluable.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots
from draftopt.config import EVAL_DB_PATH, get_roster_preset
from draftopt.phase2 import connect_eval
from draftopt.phase2.coverage_p22c import _run_one_with_id
from draftopt.phase2.delta_p22c import (
    STRATEGIES,
    _load_outcomes,
    _score_user_roster,
)
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


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _percentile(sorted_vals: list[float], p: float) -> float:
    """Linear interpolation percentile; p in [0, 100]."""
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    x = (p / 100.0) * (len(sorted_vals) - 1)
    lo = int(x)
    hi = min(lo + 1, len(sorted_vals) - 1)
    w = x - lo
    return float(sorted_vals[lo] * (1 - w) + sorted_vals[hi] * w)


def _dist_summary(vals: list[float]) -> dict:
    s = sorted(vals)
    return {
        "n": len(s),
        "mean": round(statistics.mean(s), 4) if s else None,
        "median": round(statistics.median(s), 4) if s else None,
        "stdev": round(statistics.stdev(s), 4) if len(s) > 1 else None,
        "min": round(s[0], 4) if s else None,
        "p10": round(_percentile(s, 10), 4) if s else None,
        "p25": round(_percentile(s, 25), 4) if s else None,
        "p75": round(_percentile(s, 75), 4) if s else None,
        "p90": round(_percentile(s, 90), 4) if s else None,
        "max": round(s[-1], 4) if s else None,
        "n_positive": sum(1 for v in s if v > 0),
        "n_negative": sum(1 for v in s if v < 0),
        "n_zero": sum(1 for v in s if v == 0),
        "win_rate": round(sum(1 for v in s if v > 0) / len(s), 4) if s else None,
    }


def _attributed_starter(run: dict, exclude: frozenset[str]) -> float:
    """Same starters; drop named positions' starter points (attribution only)."""
    total = float(run["starter_actual_ppr"])
    for pos in exclude:
        total -= float(run["starter_by_pos"].get(pos, 0.0))
    return round(total, 4)


def _dst_pick(run: dict) -> dict | None:
    dsts = [p for p in run["picks"] if p["position"] == "DST"]
    if not dsts:
        return None
    # Prefer starter DST if multiple (shouldn't happen under league_default)
    return max(dsts, key=lambda p: float(p["actual_ppr"]))


def run_diagnose(
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

    contracts = {
        "full": frozenset(),
        "ex_dst": frozenset({"DST"}),
        "ex_dst_te": frozenset({"DST", "TE"}),
    }

    pairs: list[dict] = []
    dst_rows: list[dict] = []
    for slot in slots:
        for i in range(n_sims):
            seed = seed0 + i
            b = runs[(slot, seed, "adp_baseline")]
            s = runs[(slot, seed, "adp_structural")]
            metrics: dict[str, dict] = {}
            for name, excl in contracts.items():
                sb = _attributed_starter(b, excl)
                ss = _attributed_starter(s, excl)
                metrics[name] = {
                    "baseline": sb,
                    "structural": ss,
                    "delta": round(ss - sb, 4),
                }
            bd, sd = _dst_pick(b), _dst_pick(s)
            dst_delta = None
            if bd and sd:
                dst_delta = round(float(sd["actual_ppr"]) - float(bd["actual_ppr"]), 4)
                dst_rows.append(
                    {
                        "slot": slot,
                        "seed": seed,
                        "baseline_dst": bd["name"],
                        "baseline_id": bd["player_id"],
                        "baseline_round": bd["round"],
                        "baseline_overall": bd["overall"],
                        "baseline_ppr": bd["actual_ppr"],
                        "structural_dst": sd["name"],
                        "structural_id": sd["player_id"],
                        "structural_round": sd["round"],
                        "structural_overall": sd["overall"],
                        "structural_ppr": sd["actual_ppr"],
                        "delta_dst_ppr": dst_delta,
                    }
                )
            pairs.append(
                {
                    "slot": slot,
                    "seed": seed,
                    "metrics": metrics,
                    "baseline_starter_by_pos": b["starter_by_pos"],
                    "structural_starter_by_pos": s["starter_by_pos"],
                    "baseline_picks": b["picks"],
                    "structural_picks": s["picks"],
                    "dst": {
                        "baseline": bd,
                        "structural": sd,
                        "delta_ppr": dst_delta,
                    },
                }
            )

    ladder = {}
    for name in contracts:
        deltas = [p["metrics"][name]["delta"] for p in pairs]
        ladder[name] = _dist_summary(deltas)

    # DST concentration: among pairs where structural DST PPR > baseline
    win_dst = [r for r in dst_rows if (r["delta_dst_ppr"] or 0) > 0]
    gain_by_struct: Counter[str] = Counter()
    gain_amt: dict[str, float] = defaultdict(float)
    for r in win_dst:
        gain_by_struct[r["structural_dst"]] += 1
        gain_amt[r["structural_dst"]] += float(r["delta_dst_ppr"])

    top_gainers = sorted(gain_amt.items(), key=lambda t: -t[1])
    total_pos_dst_delta = sum(v for v in gain_amt.values())
    top3_share = (
        round(sum(v for _, v in top_gainers[:3]) / total_pos_dst_delta, 4)
        if total_pos_dst_delta > 0
        else None
    )

    dst_deltas = [float(r["delta_dst_ppr"]) for r in dst_rows if r["delta_dst_ppr"] is not None]
    unique_struct = sorted({r["structural_dst"] for r in dst_rows})
    unique_base = sorted({r["baseline_dst"] for r in dst_rows})

    n_pairs = len(pairs)
    b_fill = sum(
        1
        for p in pairs
        if any(x["position"] == "DST" for x in p["baseline_picks"])
    )
    s_fill = sum(
        1
        for p in pairs
        if any(x["position"] == "DST" for x in p["structural_picks"])
    )
    dst_fill_finding = (
        f"ADP baseline drafted DST in only {b_fill}/{n_pairs} pairs; "
        f"structural in {s_fill}/{n_pairs}. Most of the DST starter Δ is empty-slot "
        f"fill when baseline skips DST, not identity skill on dual-DST drafts "
        f"(n={len(dst_rows)})."
    )

    # Histogram bins for full Δ
    import math

    full_deltas = [p["metrics"]["full"]["delta"] for p in pairs]
    bin_width = 50.0
    hist: dict[str, int] = defaultdict(int)
    for d in full_deltas:
        lo = int(math.floor(d / bin_width) * bin_width)
        label = f"[{lo},{lo + int(bin_width)})"
        hist[label] += 1

    # Slot means for full vs ex_dst
    by_slot: dict[int, dict] = {}
    for slot in slots:
        full_s = [p["metrics"]["full"]["delta"] for p in pairs if p["slot"] == slot]
        ex_s = [p["metrics"]["ex_dst"]["delta"] for p in pairs if p["slot"] == slot]
        by_slot[slot] = {
            "full_mean": round(statistics.mean(full_s), 4),
            "ex_dst_mean": round(statistics.mean(ex_s), 4),
            "full_win_rate": round(sum(1 for v in full_s if v > 0) / len(full_s), 4),
            "ex_dst_win_rate": round(sum(1 for v in ex_s if v > 0) / len(ex_s), 4),
        }

    interpretation = []
    if b_fill < n_pairs * 0.9 and s_fill >= n_pairs * 0.9:
        interpretation.append("dst_delta_mostly_slot_fill_not_identity")
    ex = ladder["ex_dst"]["mean"]
    if ex is not None:
        if ex >= 40:
            interpretation.append(
                "ex_dst_still_strongly_positive — skill-position construction signal plausible"
            )
        elif ex >= 10:
            interpretation.append(
                "ex_dst_moderately_positive — partial non-DST signal"
            )
        elif ex > -10:
            interpretation.append(
                "ex_dst_near_zero — DST largely carried the headline"
            )
        else:
            interpretation.append(
                "ex_dst_negative — structural advantage primarily DST-driven"
            )

    return {
        "stage": "P2.2C_delta_mechanism_audit",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "note": (
            "Same deterministic seed0/slots/n_sims as phase2_p22c_actual_ppr_delta. "
            "Attribution drops starter points by position without re-drafting. "
            "Not V3. Not UI. n=1 season / modeled opponents."
        ),
        "contract": contract_meta(),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_pairs": len(pairs),
        "attribution_ladder": ladder,
        "interpretation_flags": interpretation,
        "dst_audit": {
            "n_pairs_with_dst": len(dst_rows),
            "baseline_drafted_dst": b_fill,
            "structural_drafted_dst": s_fill,
            "baseline_dst_fill_rate": round(b_fill / n_pairs, 4) if n_pairs else None,
            "structural_dst_fill_rate": round(s_fill / n_pairs, 4) if n_pairs else None,
            "finding": dst_fill_finding,
            "delta_dist": _dist_summary(dst_deltas),
            "unique_baseline_dst": unique_base,
            "unique_structural_dst": unique_struct,
            "n_unique_baseline": len(unique_base),
            "n_unique_structural": len(unique_struct),
            "structural_win_count": sum(1 for d in dst_deltas if d > 0),
            "baseline_win_count": sum(1 for d in dst_deltas if d < 0),
            "dst_tie_count": sum(1 for d in dst_deltas if d == 0),
            "top_structural_gain_dst": [
                {"name": n, "sum_delta": round(v, 4), "n_pairs": gain_by_struct[n]}
                for n, v in top_gainers[:8]
            ],
            "top3_positive_delta_share": top3_share,
            "rows": dst_rows,
        },
        "full_delta_distribution": _dist_summary(full_deltas),
        "full_delta_histogram_bin50": dict(sorted(hist.items(), key=lambda t: int(t[0].split(",")[0][1:]))),
        "by_slot": by_slot,
        "pairs": pairs,
    }


def _md(report: dict) -> str:
    ladder = report["attribution_ladder"]
    lines = [
        "# P2.2C Δ mechanism audit",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']} (slots {report['slots']}, n_sims={report['n_sims']}, seed0={report['seed0']})",
        "",
        report["note"],
        "",
        f"Flags: {', '.join(report['interpretation_flags']) or 'none'}",
        "",
        "## 1. Attribution ladder (structural − baseline)",
        "",
        "| Metric | Mean Δ | Median Δ | Win rate | p10 | p90 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "full": "Full starter PPR",
        "ex_dst": "Ex-DST",
        "ex_dst_te": "Ex-DST + TE",
    }
    for key, label in labels.items():
        d = ladder[key]
        lines.append(
            f"| {label} | {d['mean']:+.2f} | {d['median']:+.2f} | "
            f"{d['win_rate']:.0%} | {d['p10']:+.1f} | {d['p90']:+.1f} |"
        )

    da = report["dst_audit"]
    dd = da["delta_dist"]
    lines.extend(
        [
            "",
            "## 2. DST audit",
            "",
        ]
    )
    if da.get("finding"):
        lines.append(f"- **DST fill rate:** baseline {da.get('baseline_drafted_dst')}/{report['n_pairs']} "
                     f"({(da.get('baseline_dst_fill_rate') or 0):.0%}); "
                     f"structural {da.get('structural_drafted_dst')}/{report['n_pairs']} "
                     f"({(da.get('structural_dst_fill_rate') or 0):.0%})")
        lines.append(f"- **Finding:** {da['finding']}")
    lines.extend(
        [
            f"- unique baseline DSTs: {da['n_unique_baseline']} — {', '.join(da['unique_baseline_dst'])}",
            f"- unique structural DSTs: {da['n_unique_structural']} — {', '.join(da['unique_structural_dst'])}",
            f"- DST Δ mean/median (dual-DST pairs only, n={da['n_pairs_with_dst']}): "
            f"{dd['mean']:+.2f} / {dd['median']:+.2f}",
            f"- structural DST wins (dual only): {da['structural_win_count']}/{da['n_pairs_with_dst']} "
            f"(baseline wins {da['baseline_win_count']}, ties {da['dst_tie_count']})",
            f"- top-3 defenses' share of positive DST Δ sum: {da['top3_positive_delta_share']}",
            "",
            "### Top structural DST contributors (sum of positive Δ when structural DST scored more)",
            "",
            "| DST | sum Δ | n pairs |",
            "| --- | ---: | ---: |",
        ]
    )
    for row in da["top_structural_gain_dst"]:
        lines.append(f"| {row['name']} | {row['sum_delta']:+.1f} | {row['n_pairs']} |")

    lines.extend(
        [
            "",
            "### Per-pair DST (sample head; full table in JSON)",
            "",
            "| slot | seed | baseline | rnd | PPR | structural | rnd | PPR | Δ |",
            "| ---: | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for r in da["rows"][:24]:
        lines.append(
            f"| {r['slot']} | {r['seed']} | {r['baseline_dst']} | {r['baseline_round']} | "
            f"{r['baseline_ppr']:.1f} | {r['structural_dst']} | {r['structural_round']} | "
            f"{r['structural_ppr']:.1f} | {r['delta_dst_ppr']:+.1f} |"
        )
    if len(da["rows"]) > 24:
        lines.append(f"| … | ({len(da['rows']) - 24} more in JSON) | | | | | | | |")

    fd = report["full_delta_distribution"]
    lines.extend(
        [
            "",
            "## 3. Full Δ distribution",
            "",
            f"| min | p10 | p25 | median | p75 | p90 | max |",
            f"| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| {fd['min']:+.1f} | {fd['p10']:+.1f} | {fd['p25']:+.1f} | "
            f"{fd['median']:+.1f} | {fd['p75']:+.1f} | {fd['p90']:+.1f} | {fd['max']:+.1f} |",
            "",
            f"mean {fd['mean']:+.2f} · stdev {fd['stdev']:.2f} · "
            f"wins {fd['n_positive']}/{fd['n']} ({fd['win_rate']:.0%})",
            "",
            "### Histogram (bin width 50)",
            "",
            "| Bin | count |",
            "| --- | ---: |",
        ]
    )
    for lab, n in report["full_delta_histogram_bin50"].items():
        lines.append(f"| `{lab}` | {n} |")

    lines.extend(
        [
            "",
            "## Mean Δ by slot: full vs ex-DST",
            "",
            "| Slot | full mean | ex-DST mean | full WR | ex-DST WR |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for slot, row in report["by_slot"].items():
        lines.append(
            f"| {slot} | {row['full_mean']:+.1f} | {row['ex_dst_mean']:+.1f} | "
            f"{row['full_win_rate']:.0%} | {row['ex_dst_win_rate']:.0%} |"
        )

    lines.extend(
        [
            "",
            "## Status",
            "",
            "- Phase 2: 🟡 signal detected, mechanism under audit",
            "- V3: 🔴 blocked",
            "- UI: `marginal`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C delta mechanism audit")
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_delta_mechanism_audit.md"),
    )
    args = parser.parse_args()
    report = run_diagnose(
        draft_db=args.draft_db,
        eval_db=args.eval_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    # Full pairs JSON can be large; write alongside
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
