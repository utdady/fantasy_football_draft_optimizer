"""
Opponent-policy stress: V2-alpha / robust-min / mixture-β vs raw under CPUs.

Planner scenarios (ADP/proj/VOR futures) are used only inside recommend().
Actual draft opponents are independent via --policies (planner ≠ evaluator).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from draftopt import db
from draftopt.backtest import _pairwise, pick_rng, run_one, summarize
from draftopt.draft.cpu import CPU_POLICIES, cpu_pick
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import (
    create_draft,
    is_user_turn,
    record_user_pick,
    snapshot,
)
from draftopt.pool import remaining_ranked
from draftopt.strategies import get_strategy

DEFAULT_USER_STRATEGIES = (
    "marginal",
    "marginal_vor",
    "marginal_v2",
    "robust_min",
)

# Policies where CPU picks are fully deterministic given remaining pool.
DETERMINISTIC_POLICIES = frozenset({"adp_greedy", "proj_greedy", "vor"})


def run_one_v2_tracked(
    conn,
    *,
    user_slot: int,
    roster_preset: str,
    seed: int,
    opponent_policy: str,
    strategy_name: str = "marginal_v2",
    n_teams: int = 10,
    max_track_rounds: int = 6,
) -> dict:
    """Single draft that records whether expected future q survived until next pick."""
    strategy = get_strategy(strategy_name)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"Bot-{strategy_name}-track",
        roster_preset=roster_preset,
        n_teams=n_teams,
    )
    events: list[dict] = []
    pending: dict | None = None

    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        overall = int(draft_row["current_pick"])
        if is_user_turn(draft_row):
            if pending is not None:
                rem_ids = {p["player_id"] for p in remaining_ranked(conn, draft_id)}
                qid = pending.get("q_player_id")
                pending["q_survived"] = (qid in rem_ids) if qid else None
                pending["resolved_at_overall"] = overall
                events.append(pending)
                pending = None

            recs = strategy.recommend(conn, draft_id, n=1)
            if not recs:
                break
            rec = recs[0]
            rnd = int((overall - 1) // n_teams) + 1
            if rnd <= max_track_rounds:
                q_name = rec.get("q_player")
                q_id = None
                if q_name:
                    for p in remaining_ranked(conn, draft_id):
                        if p.get("name") == q_name and p["player_id"] != rec["player_id"]:
                            q_id = p["player_id"]
                            break
                pending = {
                    "overall": overall,
                    "round": rnd,
                    "took": rec.get("name"),
                    "took_pos": rec.get("position"),
                    "took_id": rec.get("player_id"),
                    "expected_q": q_name,
                    "expected_q_pos": rec.get("q_position"),
                    "q_player_id": q_id,
                    "picks_until_next": rec.get("picks_until_next"),
                    "ev_two_pick": rec.get("ev_two_pick"),
                    "ev_by_future": rec.get("ev_by_future"),
                    "ev_min": rec.get("ev_min"),
                    "scenario_spread": rec.get("scenario_spread"),
                    "worst_future": rec.get("worst_future"),
                }
            record_user_pick(conn, draft_id, rec["player_id"], made_by="strategy")
        else:
            cpu_pick(
                conn,
                draft_id,
                rng=pick_rng(seed, overall),
                policy=opponent_policy,
            )

    from draftopt.backtest import _starter_ranks, _user_pick_log

    grade = grade_draft(conn, draft_id)
    user = grade["user"]
    starter_map = _starter_ranks(conn, draft_id)
    starter_pts, starter_rank = starter_map[user_slot]
    return {
        "starter_pts": starter_pts,
        "starter_rank": starter_rank,
        "roster_proj": float(user["projected_points"]),
        "picks": _user_pick_log(conn, draft_id, user_slot),
        "q_events": events,
    }


def _r1_decision_snapshot(conn, *, slot: int, preset: str) -> dict:
    """
    Empty-board R1 recommendations for α and robust (planner diagnostics).

    At slot-1 overall #1 the remaining pool is identical across opponent policies.
    """
    draft_id = create_draft(
        conn, user_slot=slot, user_name="r1-snap", roster_preset=preset
    )
    out: dict[str, dict] = {}
    for name in ("marginal_v2", "robust_min", "marginal", "marginal_vor"):
        try:
            rec = get_strategy(name).recommend(conn, draft_id, n=1)[0]
        except Exception as exc:  # noqa: BLE001 — diagnostic only
            out[name] = {"error": str(exc)}
            continue
        out[name] = {
            "name": rec.get("name"),
            "position": rec.get("position"),
            "picks_until_next": rec.get("picks_until_next"),
            "ev_two_pick": rec.get("ev_two_pick"),
            "ev_min": rec.get("ev_min"),
            "ev_max": rec.get("ev_max"),
            "ev_by_future": rec.get("ev_by_future"),
            "scenario_spread": rec.get("scenario_spread"),
            "worst_future": rec.get("worst_future"),
            "q_player": rec.get("q_player"),
            "why": rec.get("why"),
        }
    alpha = out.get("marginal_v2") or {}
    robust = out.get("robust_min") or {}
    return {
        "by_strategy": out,
        "alpha_vs_robust_agree": alpha.get("name") == robust.get("name"),
        "note": (
            "R1 planner snapshot on empty board; independent of opponent policy "
            "at overall #1."
        ),
    }


def _r1_pick_counts(by: dict[str, list]) -> dict[str, dict]:
    """Aggregate actual R1 picks taken during sims."""
    out: dict[str, dict] = {}
    for name, rows in by.items():
        c = Counter()
        for r in rows:
            if r.picks:
                p0 = r.picks[0]
                key = f"{p0.get('name')} ({p0.get('position')})"
                c[key] += 1
        total = sum(c.values()) or 1
        out[name] = {
            "counts": dict(c.most_common()),
            "n": sum(c.values()),
            "top": c.most_common(1)[0][0] if c else None,
            "share_top": (c.most_common(1)[0][1] / total) if c else None,
        }
    return out


def run_stress_grid(
    *,
    slots: list[int] | None = None,
    n: int = 20,
    seed: int = 0,
    policies: list[str] | None = None,
    strategies: list[str] | None = None,
    preset: str = "league_default",
    conn=None,
    db_path=None,
    max_loss_diagnostics: int = 3,
) -> dict:
    slots = slots or [1, 5, 10]
    policies = policies or list(CPU_POLICIES)
    strategies = list(strategies or DEFAULT_USER_STRATEGIES)
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    cells = []
    try:
        r1_snap = None
        if 1 in slots:
            print("... R1 decision snapshot (empty board)", flush=True)
            r1_snap = _r1_decision_snapshot(conn, slot=1, preset=preset)

        for policy in policies:
            for slot in slots:
                print(
                    f"... stress cpu={policy} slot={slot} n={n} "
                    f"strats={','.join(strategies)}",
                    flush=True,
                )
                cell = _run_stress_cell_efficient(
                    conn,
                    slot=slot,
                    n=n,
                    seed=seed,
                    opponent_policy=policy,
                    preset=preset,
                    strategies=strategies,
                    max_loss_diagnostics=max_loss_diagnostics,
                )
                cells.append(cell)
                alpha = cell.get("v2_vs_raw") or {}
                robust = cell.get("robust_vs_raw") or {}
                print(
                    f"    α−raw={alpha.get('mean_delta', 0):+.1f} "
                    f"rob−raw={robust.get('mean_delta', 0):+.1f} "
                    f"rob−α={(cell.get('robust_vs_v2') or {}).get('mean_delta', 0):+.1f}",
                    flush=True,
                )
        return {
            "n": n,
            "slots": slots,
            "seed": seed,
            "preset": preset,
            "policies": policies,
            "strategies": strategies,
            "v2_alpha_lookahead": "adp_greedy (frozen)",
            "robust_min_lookahead": "min_f over adp_greedy+proj_greedy+vor",
            "planner_vs_evaluator": (
                "Recommend() may use scenario futures; actual CPU picks use "
                "--policies only."
            ),
            "r1_decision_snapshot": r1_snap,
            "cells": cells,
            "notes": [
                "Diagnostic lean — not a validation/promotion of robust_min.",
                "For deterministic opponent policies (adp_greedy, proj_greedy, vor), "
                "repeated sims with different seeds reprint the same trajectory; "
                "win rates are not independent-trial estimates.",
                "noisy_adp has real sample variance across seeds.",
                "UI default remains marginal.",
            ],
        }
    finally:
        if own:
            conn.close()


def _run_stress_cell_efficient(
    conn,
    *,
    slot: int,
    n: int,
    seed: int,
    opponent_policy: str,
    preset: str,
    strategies: list[str],
    max_loss_diagnostics: int,
) -> dict:
    by: dict[str, list] = {s: [] for s in strategies}
    if "robust_min" in strategies:
        loss_focus = "robust_min"
    elif "marginal_v2_beta" in strategies:
        loss_focus = "marginal_v2_beta"
    elif "marginal_v2" in strategies:
        loss_focus = "marginal_v2"
    else:
        loss_focus = strategies[-1]
    baseline = "marginal" if "marginal" in strategies else strategies[0]
    loss_seeds: list[tuple[int, int, object, object]] = []

    for i in range(n):
        if n >= 10 and (i == 0 or (i + 1) % max(1, n // 5) == 0 or i + 1 == n):
            print(f"    sim {i + 1}/{n}", flush=True)
        sim_seed = seed + i * 1009
        results = {}
        for name in strategies:
            results[name] = run_one(
                conn,
                strategy_name=name,
                user_slot=slot,
                roster_preset=preset,
                seed=sim_seed,
                opponent_policy=opponent_policy,
            )
            by[name].append(results[name])
        if baseline in results and loss_focus in results:
            focus = results[loss_focus]
            raw = results[baseline]
            if focus.starter_pts + 1e-6 < raw.starter_pts:
                loss_seeds.append((i, sim_seed, raw, focus))

    comparisons: dict[str, dict] = {}
    if "marginal" in by and "marginal_v2" in by:
        comparisons["v2_vs_raw"] = _pairwise(by, "marginal_v2", "marginal")
    if "marginal" in by and "robust_min" in by:
        comparisons["robust_vs_raw"] = _pairwise(by, "robust_min", "marginal")
    if "marginal_v2" in by and "robust_min" in by:
        comparisons["robust_vs_v2"] = _pairwise(by, "robust_min", "marginal_v2")
    if "marginal" in by and "marginal_vor" in by:
        comparisons["vor_vs_raw"] = _pairwise(by, "marginal_vor", "marginal")
    if "marginal" in by and "marginal_v2_beta" in by:
        comparisons["beta_vs_raw"] = _pairwise(by, "marginal_v2_beta", "marginal")
    if "marginal_v2" in by and "marginal_v2_beta" in by:
        comparisons["beta_vs_v2"] = _pairwise(by, "marginal_v2_beta", "marginal_v2")

    losses = []
    for i, sim_seed, raw, focus in loss_seeds[:max_loss_diagnostics]:
        tracked = run_one_v2_tracked(
            conn,
            user_slot=slot,
            roster_preset=preset,
            seed=sim_seed,
            opponent_policy=opponent_policy,
            strategy_name=loss_focus,
        )
        failed_q = [
            e for e in tracked.get("q_events") or [] if e.get("q_survived") is False
        ]
        alpha_row = None
        if "marginal_v2" in by and i < len(by["marginal_v2"]):
            ap = by["marginal_v2"][i].picks
            alpha_row = ap[0] if ap else None
        losses.append(
            {
                "sim": i,
                "seed": sim_seed,
                "focus_strategy": loss_focus,
                "raw_pts": round(raw.starter_pts, 2),
                "focus_pts": round(focus.starter_pts, 2),
                "delta": round(focus.starter_pts - raw.starter_pts, 2),
                "raw_r1": raw.picks[0] if raw.picks else None,
                "focus_r1": focus.picks[0] if focus.picks else None,
                "alpha_r1": alpha_row,
                "q_failures": failed_q[:4],
                "q_events_early": (tracked.get("q_events") or [])[:4],
            }
        )

    det = opponent_policy in DETERMINISTIC_POLICIES
    return {
        "slot": slot,
        "n": n,
        "seed": seed,
        "opponent_policy": opponent_policy,
        "deterministic_opponent": det,
        "summaries": {name: summarize(name, rows) for name, rows in by.items()},
        "v2_vs_raw": comparisons.get("v2_vs_raw"),
        "robust_vs_raw": comparisons.get("robust_vs_raw"),
        "robust_vs_v2": comparisons.get("robust_vs_v2"),
        "vor_vs_raw": comparisons.get("vor_vs_raw"),
        "beta_vs_raw": comparisons.get("beta_vs_raw"),
        "beta_vs_v2": comparisons.get("beta_vs_v2"),
        "comparisons": comparisons,
        "r1_pick_counts": _r1_pick_counts(by),
        "n_losses": len(loss_seeds),
        "loss_diagnostics": losses,
        "note": (
            "Planner scenarios ≠ evaluation opponent. "
            "Opponent policy applies to actual CPU picks only."
            + (
                " Opponent is deterministic: n>1 reprints one trajectory."
                if det
                else ""
            )
        ),
    }


def to_markdown(report: dict) -> str:
    strats = report.get("strategies") or []
    has_robust = "robust_min" in strats
    title = (
        "β2-robust-min opponent-policy lean"
        if has_robust
        else "V2 opponent-policy stress"
    )
    lines = [
        f"# {title}",
        "",
        "## Setup",
        "",
        f"- n_sims per cell: **{report['n']}**",
        f"- slots: `{report['slots']}`",
        f"- seed: `{report['seed']}`",
        f"- strategies: `{', '.join(strats)}` (paired seeds)",
        f"- V2-alpha lookahead: **{report.get('v2_alpha_lookahead', 'adp_greedy')}**",
        f"- robust_min lookahead: **{report.get('robust_min_lookahead', 'n/a')}**",
        f"- planner vs evaluator: {report.get('planner_vs_evaluator', '')}",
        f"- opponent policies: `{', '.join(report['policies'])}`",
        "",
    ]
    for note in report.get("notes") or []:
        lines.append(f"- note: {note}")

    snap = report.get("r1_decision_snapshot") or {}
    if snap:
        lines.extend(["", "## R1 decision snapshot (empty board)", ""])
        lines.append(f"_{snap.get('note')}_")
        lines.append("")
        lines.append(
            f"- α vs robust agree: **{snap.get('alpha_vs_robust_agree')}**"
        )
        lines.append("")
        lines.append(
            "| strategy | pick | pos | wait | ev / min | spread | worst | q |"
        )
        lines.append("| --- | --- | --- | ---: | ---: | ---: | --- | --- |")
        for name, row in (snap.get("by_strategy") or {}).items():
            if row.get("error"):
                lines.append(f"| {name} | error | — | — | — | — | — | — |")
                continue
            ev = row.get("ev_min") if row.get("ev_min") is not None else row.get(
                "ev_two_pick"
            )
            lines.append(
                f"| {name} | {row.get('name')} | {row.get('position')} | "
                f"{row.get('picks_until_next')} | {ev} | "
                f"{row.get('scenario_spread')} | {row.get('worst_future')} | "
                f"{row.get('q_player')} |"
            )
            if row.get("ev_by_future"):
                lines.append(f"|  | ev_by_future=`{row['ev_by_future']}` |  |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Matrix (headline deltas)",
            "",
            "| opponent | slot | det? | raw | vor | α | robust | α−raw | rob−raw | rob−α |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    def fmt(x):
        return f"{x:.1f}" if x is not None else "—"

    def fmt_d(c):
        if not c:
            return "—"
        return f"{c.get('mean_delta', 0):+.1f}"

    for cell in report["cells"]:
        s = cell["summaries"]
        raw_m = (s.get("marginal") or {}).get("mean_starter_pts")
        vor_m = (s.get("marginal_vor") or {}).get("mean_starter_pts")
        a_m = (s.get("marginal_v2") or {}).get("mean_starter_pts")
        r_m = (s.get("robust_min") or {}).get("mean_starter_pts")
        lines.append(
            f"| {cell['opponent_policy']} | {cell['slot']} | "
            f"{'yes' if cell.get('deterministic_opponent') else 'no'} | "
            f"{fmt(raw_m)} | {fmt(vor_m)} | {fmt(a_m)} | {fmt(r_m)} | "
            f"{fmt_d(cell.get('v2_vs_raw'))} | "
            f"{fmt_d(cell.get('robust_vs_raw'))} | "
            f"{fmt_d(cell.get('robust_vs_v2'))} |"
        )

    lines.extend(["", "## R1 pick behavior (actual sims)", ""])
    for cell in report["cells"]:
        lines.append(
            f"### {cell['opponent_policy']} · slot {cell['slot']}"
        )
        lines.append("")
        for name, info in (cell.get("r1_pick_counts") or {}).items():
            lines.append(
                f"- `{name}`: top={info.get('top')} "
                f"({(info.get('share_top') or 0):.0%}); counts={info.get('counts')}"
            )
        lines.append("")

    lines.extend(["", "## Loss diagnostics (focus vs raw)", ""])
    for cell in report["cells"]:
        if not cell.get("loss_diagnostics"):
            continue
        lines.append(
            f"### {cell['opponent_policy']} · slot {cell['slot']} "
            f"({cell.get('n_losses', 0)} losses; "
            f"{'deterministic' if cell.get('deterministic_opponent') else 'stochastic'})"
        )
        lines.append("")
        for loss in cell["loss_diagnostics"]:
            lines.append(
                f"- sim {loss['sim']} seed={loss['seed']}: "
                f"Δ={loss['delta']:+.1f} "
                f"(raw {loss['raw_pts']:.1f} vs {loss['focus_strategy']} "
                f"{loss['focus_pts']:.1f})"
            )
            r1r = loss.get("raw_r1") or {}
            r1f = loss.get("focus_r1") or {}
            lines.append(
                f"  - R1 raw={r1r.get('name')} ({r1r.get('position')}); "
                f"focus={r1f.get('name')} ({r1f.get('position')})"
            )
            fails = loss.get("q_failures") or []
            if fails:
                for e in fails:
                    lines.append(
                        f"  - q FAILED: took {e.get('took')} expecting "
                        f"{e.get('expected_q')} ({e.get('expected_q_pos')}) "
                        f"after wait {e.get('picks_until_next')}"
                    )
            else:
                lines.append("  - no early q-survival failures recorded")
        lines.append("")

    lines.extend(
        [
            "## Reading",
            "",
            "- 🟢 Best: robust slightly worse vs ADP-like, much better vs proj_greedy.",
            "- 🟡 Interesting: fixes proj but crushes ADP-like → minimax too sharp.",
            "- 🔴 Bad: still fails proj_greedy → need richer future-board model.",
            "- Deterministic CPUs: treat mean Δ as a single-trajectory gap, not a "
            "win-rate claim.",
            "- Do not promote robust_min to UI from this lean alone.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="V2 / robust-min opponent-policy stress (diagnostic lean)"
    )
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--slots", type=str, default="1")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--policies",
        type=str,
        default="noisy_adp,adp_greedy,proj_greedy,vor",
    )
    parser.add_argument(
        "--strategies",
        type=str,
        default=",".join(DEFAULT_USER_STRATEGIES),
    )
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/stress_robust_min_slot1.md",
    )
    args = parser.parse_args()
    slots = [int(x.strip()) for x in args.slots.split(",") if x.strip()]
    policies = [p.strip() for p in args.policies.split(",") if p.strip()]
    strategies = [s.strip() for s in args.strategies.split(",") if s.strip()]
    report = run_stress_grid(
        slots=slots,
        n=args.n,
        seed=args.seed,
        policies=policies,
        strategies=strategies,
        preset=args.preset,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
