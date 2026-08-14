"""
Opponent-policy stress: V2-alpha vs raw under different CPU behaviors.

V2 lookahead stays frozen (ADP-greedy). Only the *actual* draft opponents change.
"""

from __future__ import annotations

import argparse
import json
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


def run_one_v2_tracked(
    conn,
    *,
    user_slot: int,
    roster_preset: str,
    seed: int,
    opponent_policy: str,
    n_teams: int = 10,
    max_track_rounds: int = 6,
) -> dict:
    """
    Single V2 draft that records whether expected future q survived until next pick.
    """
    strategy = get_strategy("marginal_v2")
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name="Bot-v2-track",
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
                # Resolve q player_id from name among remaining (best-effort).
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


def run_stress_grid(
    *,
    slots: list[int] | None = None,
    n: int = 20,
    seed: int = 0,
    policies: list[str] | None = None,
    preset: str = "league_default",
    conn=None,
    db_path=None,
    max_loss_diagnostics: int = 3,
) -> dict:
    slots = slots or [1, 5, 10]
    policies = policies or list(CPU_POLICIES)
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
        for policy in policies:
            for slot in slots:
                print(
                    f"... stress cpu={policy} slot={slot} n={n}",
                    flush=True,
                )
                # Single paired pass (no triple re-run) — collect results ourselves.
                cell = _run_stress_cell_efficient(
                    conn,
                    slot=slot,
                    n=n,
                    seed=seed,
                    opponent_policy=policy,
                    preset=preset,
                    max_loss_diagnostics=max_loss_diagnostics,
                )
                cells.append(cell)
                print(
                    f"    v2-raw={cell['v2_vs_raw'].get('mean_delta', 0):+.1f} "
                    f"win={cell['v2_vs_raw'].get('win_rate', 0):.0%}",
                    flush=True,
                )
        return {
            "n": n,
            "slots": slots,
            "seed": seed,
            "preset": preset,
            "policies": policies,
            "v2_lookahead": "adp_greedy (frozen)",
            "cells": cells,
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
    max_loss_diagnostics: int,
) -> dict:
    by = {"marginal": [], "marginal_v2": []}
    loss_seeds: list[tuple[int, int, SimResult, SimResult]] = []
    for i in range(n):
        if n >= 10 and (i == 0 or (i + 1) % max(1, n // 5) == 0 or i + 1 == n):
            print(f"    sim {i + 1}/{n}", flush=True)
        sim_seed = seed + i * 1009
        raw = run_one(
            conn,
            strategy_name="marginal",
            user_slot=slot,
            roster_preset=preset,
            seed=sim_seed,
            opponent_policy=opponent_policy,
        )
        v2 = run_one(
            conn,
            strategy_name="marginal_v2",
            user_slot=slot,
            roster_preset=preset,
            seed=sim_seed,
            opponent_policy=opponent_policy,
        )
        by["marginal"].append(raw)
        by["marginal_v2"].append(v2)
        if v2.starter_pts + 1e-6 < raw.starter_pts:
            loss_seeds.append((i, sim_seed, raw, v2))

    pair = _pairwise(by, "marginal_v2", "marginal")
    losses = []
    for i, sim_seed, raw, v2 in loss_seeds[:max_loss_diagnostics]:
        tracked = run_one_v2_tracked(
            conn,
            user_slot=slot,
            roster_preset=preset,
            seed=sim_seed,
            opponent_policy=opponent_policy,
        )
        failed_q = [
            e for e in tracked.get("q_events") or [] if e.get("q_survived") is False
        ]
        losses.append(
            {
                "sim": i,
                "seed": sim_seed,
                "raw_pts": round(raw.starter_pts, 2),
                "v2_pts": round(v2.starter_pts, 2),
                "delta": round(v2.starter_pts - raw.starter_pts, 2),
                "raw_r1": raw.picks[0] if raw.picks else None,
                "v2_r1": v2.picks[0] if v2.picks else None,
                "q_failures": failed_q[:4],
                "q_events_early": (tracked.get("q_events") or [])[:4],
            }
        )

    return {
        "slot": slot,
        "n": n,
        "seed": seed,
        "opponent_policy": opponent_policy,
        "summaries": {
            "marginal": summarize("marginal", by["marginal"]),
            "marginal_v2": summarize("marginal_v2", by["marginal_v2"]),
        },
        "v2_vs_raw": pair,
        "n_losses": len(loss_seeds),
        "loss_diagnostics": losses,
        "note": (
            "V2 lookahead frozen (ADP-greedy). Opponent policy applies to actual "
            "CPU picks only."
        ),
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# V2-alpha opponent-policy stress",
        "",
        "## Setup",
        "",
        f"- n_sims per cell: **{report['n']}**",
        f"- slots: `{report['slots']}`",
        f"- seed: `{report['seed']}`",
        f"- strategies: `marginal` vs `marginal_v2` (paired)",
        f"- V2 lookahead: **{report['v2_lookahead']}** (frozen)",
        f"- opponent policies: `{', '.join(report['policies'])}`",
        "",
        "## Matrix (V2 − raw)",
        "",
        "| opponent | slot | raw mean | v2 mean | v2−raw | v2>raw | n_losses |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cell in report["cells"]:
        c = cell["v2_vs_raw"]
        s = cell["summaries"]
        lines.append(
            f"| {cell['opponent_policy']} | {cell['slot']} | "
            f"{s['marginal']['mean_starter_pts']:.1f} | "
            f"{s['marginal_v2']['mean_starter_pts']:.1f} | "
            f"{c.get('mean_delta', 0):+.1f} | {c.get('win_rate', 0):.0%} | "
            f"{cell.get('n_losses', 0)} |"
        )
    lines.extend(["", "## Loss diagnostics (sample)", ""])
    for cell in report["cells"]:
        if not cell.get("loss_diagnostics"):
            continue
        lines.append(
            f"### {cell['opponent_policy']} · slot {cell['slot']} "
            f"({cell.get('n_losses', 0)} losses)"
        )
        lines.append("")
        for loss in cell["loss_diagnostics"]:
            lines.append(
                f"- sim {loss['sim']} seed={loss['seed']}: "
                f"Δ={loss['delta']:+.1f} "
                f"(raw {loss['raw_pts']:.1f} vs v2 {loss['v2_pts']:.1f})"
            )
            r1r = loss.get("raw_r1") or {}
            r1v = loss.get("v2_r1") or {}
            lines.append(
                f"  - R1 raw={r1r.get('name')} ({r1r.get('position')}); "
                f"v2={r1v.get('name')} ({r1v.get('position')})"
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
            "- If V2 stays ahead under proj_greedy / vor opponents, the opportunity "
            "idea generalizes beyond ADP-like CPUs.",
            "- If the edge collapses only for some policies, V2-β should mix futures "
            "rather than only sample more ADP paths.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V2-alpha opponent-policy stress")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--slots", type=str, default="1,5,10")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--policies",
        type=str,
        default="noisy_adp,adp_greedy,proj_greedy,vor",
    )
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/stress_v2alpha_opponent_policies.md",
    )
    args = parser.parse_args()
    slots = [int(x.strip()) for x in args.slots.split(",") if x.strip()]
    policies = [p.strip() for p in args.policies.split(",") if p.strip()]
    report = run_stress_grid(
        slots=slots,
        n=args.n,
        seed=args.seed,
        policies=policies,
        preset=args.preset,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
