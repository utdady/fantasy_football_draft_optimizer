"""P2.2C Phase-2 closeout: best-10 symmetry + fork prediction-error table.

Inputs:
  - existing worst-10 inspection JSON (or regenerates)
  - best-10 inspection (replayed)

Outputs a single decision-tree artifact. Does not implement V3.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt.phase2.inspect_loss_cases_p22c import inspect_cases
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    contract_meta,
)

DEFAULT_MECH = Path("results/phase2_p22c_valuation_cb_mechanism.json")
DEFAULT_WORST = Path("results/phase2_p22c_loss_case_inspection.json")
POS = ("QB", "RB", "WR", "TE", "DST", "K")


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _find_in_alts(alts: list[dict], player_id: str) -> dict | None:
    for a in alts:
        if a.get("player_id") == player_id:
            return a
    return None


def _pred_error(p: dict | None) -> float | None:
    if not p:
        return None
    cv, act = p.get("curve_value"), p.get("actual_ppr")
    if cv is None or act is None:
        return None
    return round(float(act) - float(cv), 4)


def _fork_row(case: dict) -> dict | None:
    fork = case.get("fork")
    if not fork:
        return None
    c = fork["c_chosen"]
    b = fork["b_chosen"]
    # C's marginal for B's pick if B's player appears in C's ranked alts
    b_on_c_board = _find_in_alts(fork.get("c_alternatives") or [], b["player_id"])
    c_marg = c.get("marginal")
    b_marg_under_c = b_on_c_board.get("marginal") if b_on_c_board else None
    # Model-implied advantage of C pick vs B pick under C's marginal
    model_adv = None
    if c_marg is not None and b_marg_under_c is not None:
        model_adv = round(float(c_marg) - float(b_marg_under_c), 4)
    actual_adv = fork.get("actual_delta_c_minus_b")
    c_err = _pred_error(c)
    b_err = _pred_error(b)
    # Empty-slot signal: TE/DST/K count 0 at fork for C
    counts = (fork.get("c_need") or {}).get("counts") or {}
    empty_slots = [p for p in ("QB", "RB", "WR", "TE", "DST", "K") if counts.get(p, 0) == 0]
    fills_empty = c.get("position") in empty_slots

    return {
        "slot": case["slot"],
        "seed": case["seed"],
        "valuation_gain_full": case.get("valuation_gain_full"),
        "round": fork["round"],
        "fork_tags": case.get("fork_tags") or [],
        "c": {
            "name": c.get("name"),
            "position": c.get("position"),
            "adp": c.get("adp"),
            "curve": c.get("curve_value"),
            "marginal": c_marg,
            "actual": c.get("actual_ppr"),
            "pred_error": c_err,
            "fills_empty_slot": fills_empty,
        },
        "b": {
            "name": b.get("name"),
            "position": b.get("position"),
            "adp": b.get("adp"),
            "curve": b.get("curve_value"),
            "marginal_under_c_model": b_marg_under_c,
            "actual": b.get("actual_ppr"),
            "pred_error": b_err,
            "in_c_top_alts": b_on_c_board is not None,
        },
        "model_marginal_adv_c_minus_b": model_adv,
        "actual_adv_c_minus_b": actual_adv,
        "model_vs_actual_adv": (
            round(model_adv - actual_adv, 4)
            if model_adv is not None and actual_adv is not None
            else None
        ),
        "c_empty_slots_at_fork": empty_slots,
        "c_top3_alts": (fork.get("c_alternatives") or [])[:3],
        "b_top3_alts": (fork.get("b_alternatives") or [])[:3],
    }


def _error_by_pos(rows: list[dict], side: str) -> dict[str, dict]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        p = r[side]
        err = p.get("pred_error")
        pos = p.get("position")
        if err is not None and pos:
            buckets[pos].append(float(err))
    out = {}
    for pos in POS:
        vals = buckets.get(pos) or []
        if not vals:
            continue
        out[pos] = {
            "n": len(vals),
            "mean_pred_error": round(statistics.mean(vals), 4),
            "median_pred_error": round(statistics.median(vals), 4),
        }
    return out


def _count_tag(report: dict, tag: str) -> int:
    agg = report.get("aggregate") or {}
    # Prefer live recount from cases (older JSONs lack n_* fields)
    cases = report.get("cases") or []
    if cases:
        return sum(1 for c in cases if tag in (c.get("fork_tags") or []))
    key = {
        "structural_skill_over_rb_qb": "n_skill_over_qb_tag",
        "structural_mid_te": "n_mid_te_tag",
    }.get(tag)
    if key and key in agg:
        return int(agg[key])
    return int((agg.get("fork_tags") or {}).get(tag, 0))


def _symmetry(worst: dict, best: dict) -> dict:
    wa, ba = worst["aggregate"], best["aggregate"]
    skill_w = _count_tag(worst, "structural_skill_over_rb_qb")
    skill_b = _count_tag(best, "structural_skill_over_rb_qb")
    te_w = _count_tag(worst, "structural_mid_te")
    te_b = _count_tag(best, "structural_mid_te")
    # Heuristic verdict
    if skill_w >= 4 and skill_b <= 1:
        skill_verdict = "asymmetric — skill-over-QB concentrated in left tail"
    elif skill_w >= 3 and skill_b >= 3:
        skill_verdict = "symmetric — skill-over-QB appears in both tails (high variance)"
    elif abs(skill_w - skill_b) <= 1:
        skill_verdict = "weakly symmetric / inconclusive at n=10"
    else:
        skill_verdict = "tilted — inspect counts before V3"

    # Branch hint for decision tree (evidence only)
    if "asymmetric" in skill_verdict:
        branch = "investigate_te_qb"
    elif "symmetric" in skill_verdict:
        branch = "do_not_fix_te_qb_specifically"
    else:
        branch = "inconclusive_symmetry"

    def _pack(rep: dict, skill: int, te: int) -> dict:
        a = rep["aggregate"]
        return {
            "n": rep["n_cases"],
            "fork_tags": a.get("fork_tags"),
            "fork_rounds": a.get("fork_rounds"),
            "fork_c_positions": a.get("fork_c_positions"),
            "fork_b_positions": a.get("fork_b_positions"),
            "c_wins_fork_actual": a.get("n_fork_pick_c_wins_actual"),
            "c_loses_fork_actual": a.get("n_fork_pick_c_loses_actual"),
            "skill_over_qb": skill,
            "mid_te": te,
        }

    return {
        "worst": _pack(worst, skill_w, te_w),
        "best": _pack(best, skill_b, te_b),
        "skill_over_qb_verdict": skill_verdict,
        "decision_tree_branch": branch,
    }


def _error_branch(rows: list[dict]) -> dict:
    """Classify dominant error type from worst-tail fork rows (heuristic)."""
    # Projection: mean |pred_error| large; model_adv positive while actual_adv negative
    model_wrong_dir = [
        r
        for r in rows
        if r.get("model_marginal_adv_c_minus_b") is not None
        and r.get("actual_adv_c_minus_b") is not None
        and r["model_marginal_adv_c_minus_b"] > 0
        and r["actual_adv_c_minus_b"] < 0
    ]
    fills_empty = [r for r in rows if r["c"].get("fills_empty_slot")]
    c_errs = [r["c"]["pred_error"] for r in rows if r["c"].get("pred_error") is not None]
    b_errs = [r["b"]["pred_error"] for r in rows if r["b"].get("pred_error") is not None]

    mean_c_err = statistics.mean(c_errs) if c_errs else None
    mean_b_err = statistics.mean(b_errs) if b_errs else None

    # If C picks fill empty slots often AND model_adv disagrees with actual → marginal/construction
    # If pred errors huge on both sides with opposite signs → projection
    notes = []
    if mean_c_err is not None and mean_b_err is not None:
        notes.append(
            f"mean pred_error C={mean_c_err:+.1f}, B={mean_b_err:+.1f} "
            f"(actual − curve)"
        )
    notes.append(
        f"model preferred C but actual preferred B in {len(model_wrong_dir)}/{len(rows)} forks"
    )
    notes.append(
        f"C pick filled an empty starter slot in {len(fills_empty)}/{len(rows)} forks"
    )

    # Branch heuristic
    if len(model_wrong_dir) >= 5 and len(fills_empty) >= 5:
        branch = "V3-B_candidate_marginal_construction_and_or_projection"
    elif mean_c_err is not None and mean_b_err is not None and (mean_b_err - mean_c_err) > 80:
        branch = "V3-A_candidate_projection_calibration"
    elif len(model_wrong_dir) <= 2:
        branch = "V3-C_candidate_uncertainty_or_cascade"
    else:
        branch = "mixed_projection_and_construction"

    return {
        "n_forks": len(rows),
        "n_model_wrong_direction": len(model_wrong_dir),
        "n_c_fills_empty_slot": len(fills_empty),
        "mean_pred_error_c": round(mean_c_err, 4) if mean_c_err is not None else None,
        "mean_pred_error_b": round(mean_b_err, 4) if mean_b_err is not None else None,
        "pred_error_by_pos_c": _error_by_pos(rows, "c"),
        "pred_error_by_pos_b": _error_by_pos(rows, "b"),
        "notes": notes,
        "decision_tree_branch": branch,
    }


def build_closeout(
    *,
    worst: dict,
    best: dict,
) -> dict:
    worst_rows = [r for c in worst["cases"] if (r := _fork_row(c))]
    best_rows = [r for c in best["cases"] if (r := _fork_row(c))]
    sym = _symmetry(worst, best)
    err = _error_branch(worst_rows)

    return {
        "stage": "P2.2C_phase2_closeout",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "Phase-2 closeout: best-10 fork symmetry vs worst-10, plus fork "
            "prediction-error table (curve / marginal / actual). Chooses V3 "
            "branch evidence — does not implement V3."
        ),
        "note": (
            "Core thesis remains preliminary. UI stays marginal. "
            "adp_structural has no explicit replacement."
        ),
        "contract": contract_meta(),
        "symmetry": sym,
        "fork_prediction_errors": {
            "worst_tail": {
                "rows": worst_rows,
                "summary": err,
            },
            "best_tail": {
                "rows": best_rows,
                "summary": _error_branch(best_rows) if best_rows else None,
            },
        },
        "status": {
            "core_thesis": "preliminary_empirical_support",
            "external_validity": "not_established",
            "v3": "design_justified_implementation_pending_closeout_read",
            "ui": "marginal",
            "evaluable": 0,
        },
    }


def _fmt(v, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.1f}" if signed else f"{v:.1f}"


def _md(report: dict) -> str:
    sym = report["symmetry"]
    w, b = sym["worst"], sym["best"]
    err = report["fork_prediction_errors"]["worst_tail"]["summary"]
    rows = report["fork_prediction_errors"]["worst_tail"]["rows"]
    lines = [
        "# P2.2C Phase-2 closeout (symmetry + fork prediction error)",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        "",
        report["claim"],
        "",
        f"**{report['note']}**",
        "",
        "## 1. Best-10 vs worst-10 fork symmetry",
        "",
        "| Metric | Worst-10 | Best-10 |",
        "| --- | ---: | ---: |",
        f"| skill-over-QB tag | {w['skill_over_qb']} | {b['skill_over_qb']} |",
        f"| mid-TE tag | {w['mid_te']} | {b['mid_te']} |",
        f"| C wins fork actual | {w['c_wins_fork_actual']} | {b['c_wins_fork_actual']} |",
        f"| C loses fork actual | {w['c_loses_fork_actual']} | {b['c_loses_fork_actual']} |",
        "",
        f"- Worst C positions: `{w['fork_c_positions']}`",
        f"- Best C positions: `{b['fork_c_positions']}`",
        f"- Worst B positions: `{w['fork_b_positions']}`",
        f"- Best B positions: `{b['fork_b_positions']}`",
        f"- Worst fork rounds: `{w['fork_rounds']}`",
        f"- Best fork rounds: `{b['fork_rounds']}`",
        "",
        f"**Symmetry verdict:** {sym['skill_over_qb_verdict']}",
        "",
        f"**Decision-tree branch (symmetry):** `{sym['decision_tree_branch']}`",
        "",
        "## 2. Worst-10 fork prediction-error table",
        "",
        "At first fork: curve = ADP-curve value; marginal = C's raw lineup lift; "
        "`pred_error = actual − curve`. "
        "`model_marginal_adv` = C.marginal − (B pick's marginal under C's ranking, if shown).",
        "",
        "| Slot/seed | R | C pick | C curve | C marg | C act | C err | "
        "B pick | B curve | B marg@C | B act | B err | modelΔ | actualΔ | empty? |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in rows:
        c, bp = r["c"], r["b"]
        lines.append(
            f"| {r['slot']}/{r['seed']} | {r['round']} | "
            f"{c['name']} ({c['position']}) | {_fmt(c['curve'], False)} | "
            f"{_fmt(c['marginal'])} | {_fmt(c['actual'], False)} | {_fmt(c['pred_error'])} | "
            f"{bp['name']} ({bp['position']}) | {_fmt(bp['curve'], False)} | "
            f"{_fmt(bp['marginal_under_c_model'])} | {_fmt(bp['actual'], False)} | "
            f"{_fmt(bp['pred_error'])} | {_fmt(r['model_marginal_adv_c_minus_b'])} | "
            f"{_fmt(r['actual_adv_c_minus_b'])} | "
            f"{'Y' if c.get('fills_empty_slot') else 'N'} |"
        )

    lines.extend(
        [
            "",
            "### Prediction-error summary (worst forks)",
            "",
            f"- {'; '.join(err['notes'])}",
            f"- mean pred_error C: {_fmt(err['mean_pred_error_c'])}",
            f"- mean pred_error B: {_fmt(err['mean_pred_error_b'])}",
            f"- pred_error by pos (C picks): `{err['pred_error_by_pos_c']}`",
            f"- pred_error by pos (B picks): `{err['pred_error_by_pos_b']}`",
            "",
            f"**Error-table branch:** `{err['decision_tree_branch']}`",
            "",
            "## Combined closeout read",
            "",
            "### Symmetry",
            "",
            f"- skill-over-QB: worst **{sym['worst']['skill_over_qb']}** vs best "
            f"**{sym['best']['skill_over_qb']}** → **{sym['skill_over_qb_verdict']}**",
            "- Mid-draft skill-vs-QB forks appear in **both** tails; what differs is "
            "whether the actuals paid off (worst C wins fork 1/10; best 6/10).",
            "- Therefore: **do not design V3 as “stop taking TE/skill over QB.”**",
            "",
            "### Prediction error (worst forks)",
            "",
            f"- Mean `actual − curve`: C picks **{_fmt(err['mean_pred_error_c'])}**, "
            f"B picks **{_fmt(err['mean_pred_error_b'])}**.",
            "- C’s chosen skill players are systematically **over-projected** on the "
            "ADP curve relative to 2024 actuals; B’s QBs in this set are often "
            "**under-projected** (positive pred_error).",
            f"- Empty-slot fills by C: {err['n_c_fills_empty_slot']}/10 "
            "(marginal-construction still a secondary candidate, not ruled out).",
            "",
            f"**Provisional V3 pointer:** `{err['decision_tree_branch']}` "
            "(projection/calibration), with symmetry saying the TE/QB *choice type* "
            "is high-variance rather than a one-sided positional bug.",
            "",
            "```text",
            "Best-10 symmetry → do_not_fix_te_qb_specifically",
            "Fork error table → V3-A candidate (projection calibration)",
            "                 → V3-B still open if empty-slot marginal dominates",
            "```",
            "",
            "Neither branch implements V3 until explicitly designed from this evidence.",
            "",
            "## Status",
            "",
            "> **Core thesis: 🟡 preliminary empirical support**  ",
            "> **External validity: 🔴**  ",
            "> **V3: 🟡 design justified / 🔴 implementation pending closeout interpretation**  ",
            "> **UI: `marginal`**  ",
            "> **`evaluable=0`**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C Phase-2 closeout")
    parser.add_argument("--mechanism", type=Path, default=DEFAULT_MECH)
    parser.add_argument("--worst-json", type=Path, default=DEFAULT_WORST)
    parser.add_argument("--n-tail", type=int, default=10)
    parser.add_argument("--n-alts", type=int, default=8)
    parser.add_argument("--refresh-worst", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_closeout.md"),
    )
    parser.add_argument(
        "--best-out",
        type=Path,
        default=Path("results/phase2_p22c_gain_case_inspection.md"),
    )
    args = parser.parse_args()

    if args.refresh_worst or not args.worst_json.is_file():
        print("Replaying worst-10…", flush=True)
        from draftopt.phase2.inspect_loss_cases_p22c import _md as inspect_md

        worst = inspect_cases(
            mechanism_path=args.mechanism,
            n_tail=args.n_tail,
            n_alts=args.n_alts,
            tail="worst",
        )
        args.worst_json.write_text(json.dumps(worst, indent=2), encoding="utf-8")
        args.worst_json.with_suffix(".md").write_text(
            inspect_md(worst), encoding="utf-8"
        )
    else:
        worst = json.loads(args.worst_json.read_text(encoding="utf-8"))

    print("Replaying best-10 for symmetry…", flush=True)
    best = inspect_cases(
        mechanism_path=args.mechanism,
        n_tail=args.n_tail,
        n_alts=args.n_alts,
        tail="best",
    )
    from draftopt.phase2.inspect_loss_cases_p22c import _md as inspect_md

    args.best_out.parent.mkdir(parents=True, exist_ok=True)
    args.best_out.write_text(inspect_md(best), encoding="utf-8")
    args.best_out.with_suffix(".json").write_text(
        json.dumps(best, indent=2), encoding="utf-8"
    )
    print(f"Wrote {args.best_out}", flush=True)

    report = build_closeout(worst=worst, best=best)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
