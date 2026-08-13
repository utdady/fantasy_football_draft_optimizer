"""Disagreement-only trace: raw marginal vs marginal_vor at early user picks.

Answers: what does VOR choose differently from raw, and at what snake wait distance?
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.snake import next_user_overall
from draftopt.draft.state import (
    create_draft,
    is_user_turn,
    record_user_pick,
    round_for_pick,
    snapshot,
)
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy
from draftopt.vor import replacement_baselines, vor_points


def _choice_fields(conn, draft_id: str, rec: dict) -> dict:
    """Normalize strategy recommendation into comparable fields."""
    pos = (rec.get("position") or "?").upper()
    proj = float(rec.get("proj_espn") if rec.get("proj_espn") is not None else rec.get("season_points") or 0.0)
    replacement = rec.get("replacement")
    vor = rec.get("vor_points")
    if replacement is None or vor is None:
        draft = conn.execute(
            "SELECT n_teams, roster_json FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        from draftopt.draft.state import draft_roster

        slots = (draft_roster(draft).get("slots") or {})
        baselines = replacement_baselines(
            conn, draft_id, n_teams=int(draft["n_teams"]), slots=slots
        )
        replacement = float(baselines.get(pos) or 0.0)
        vor = vor_points(proj, pos, baselines)
    return {
        "player_id": rec.get("player_id"),
        "player": rec.get("name"),
        "position": pos,
        "projection": round(proj, 2),
        "lineup_gain": round(float(rec.get("marginal") or 0.0), 2),
        "replacement_pts": round(float(replacement or 0.0), 2),
        "VOR": round(float(vor or 0.0), 2),
    }


def compare_at_turn(conn, draft_id: str, user_slot: int, n_teams: int) -> dict:
    """Evaluate both strategies on the current board; return comparison payload."""
    draft = conn.execute(
        "SELECT current_pick FROM drafts WHERE draft_id = ?", (draft_id,)
    ).fetchone()
    overall = int(draft["current_pick"])
    rnd = round_for_pick(overall, n_teams)
    nxt = next_user_overall(overall, user_slot, n_teams)
    picks_until_next = (nxt - overall - 1) if nxt is not None else None
    wait_distance = (nxt - overall) if nxt is not None else None

    raw = MarginalValueStrategy().recommend(conn, draft_id, n=1)
    vor = MarginalVorStrategy().recommend(conn, draft_id, n=1)
    if not raw or not vor:
        return {
            "overall_pick": overall,
            "round": rnd,
            "next_user_pick": nxt,
            "picks_until_next": picks_until_next,
            "wait_distance": wait_distance,
            "agree": True,
            "raw": None,
            "vor": None,
        }

    raw_c = _choice_fields(conn, draft_id, raw[0])
    vor_c = _choice_fields(conn, draft_id, vor[0])
    return {
        "user_pick_index": None,  # filled by caller
        "overall_pick": overall,
        "round": rnd,
        "next_user_pick": nxt,
        "picks_until_next": picks_until_next,
        "wait_distance": wait_distance,
        "agree": raw_c["player_id"] == vor_c["player_id"],
        "raw": raw_c,
        "vor": vor_c,
    }


def run_one_sim(
    conn,
    *,
    slot: int,
    seed: int,
    max_user_picks: int = 5,
    board_driver: str = "marginal",
    preset: str = "league_default",
) -> dict:
    """
    Short draft: at each of the first `max_user_picks` user turns, compare both
    strategies; advance using `board_driver` (`marginal` or `marginal_vor`).
    """
    if board_driver not in ("marginal", "marginal_vor"):
        raise ValueError("board_driver must be marginal or marginal_vor")

    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="divergence",
        roster_preset=preset,
    )
    driver = (
        MarginalValueStrategy() if board_driver == "marginal" else MarginalVorStrategy()
    )
    disagreements: list[dict] = []
    agreements = 0
    user_picks_seen = 0

    while user_picks_seen < max_user_picks:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        n_teams = int(draft_row["n_teams"])
        if is_user_turn(draft_row):
            user_picks_seen += 1
            cmp = compare_at_turn(conn, draft_id, slot, n_teams)
            cmp["user_pick_index"] = user_picks_seen
            if cmp["agree"]:
                agreements += 1
            else:
                disagreements.append(cmp)
            recs = driver.recommend(conn, draft_id, n=1)
            if not recs:
                break
            record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")
        else:
            overall = int(draft_row["current_pick"])
            cpu_pick(conn, draft_id, rng=pick_rng(seed, overall))

    return {
        "seed": seed,
        "slot": slot,
        "board_driver": board_driver,
        "user_picks_traced": user_picks_seen,
        "agreements": agreements,
        "disagreements": disagreements,
    }


def run_trace(
    *,
    slots: list[int] | None = None,
    n_sims: int = 5,
    max_user_picks: int = 5,
    seed: int = 0,
    board_drivers: tuple[str, ...] = ("marginal", "marginal_vor"),
    preset: str = "league_default",
    conn=None,
    db_path=None,
) -> dict:
    slots = slots or [1, 5, 10]
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    by_slot: dict[int, dict] = {}
    try:
        for slot in slots:
            sims = []
            for i in range(n_sims):
                sim_seed = seed + i * 1009
                for driver in board_drivers:
                    sims.append(
                        run_one_sim(
                            conn,
                            slot=slot,
                            seed=sim_seed,
                            max_user_picks=max_user_picks,
                            board_driver=driver,
                            preset=preset,
                        )
                    )
            by_slot[slot] = {"sims": sims}
        return {
            "n_sims": n_sims,
            "slots": slots,
            "max_user_picks": max_user_picks,
            "seed": seed,
            "board_drivers": list(board_drivers),
            "preset": preset,
            "by_slot": by_slot,
        }
    finally:
        if own:
            conn.close()


def _wait_bucket(picks_until_next: int | None) -> str:
    if picks_until_next is None:
        return "unknown"
    if picks_until_next >= 14:
        return "long_14+"
    if picks_until_next >= 6:
        return "mid_6-13"
    return "short_0-5"


def _aggregate(report: dict) -> dict:
    """Cross-sim summaries for hypothesis checks."""
    out: dict[int, dict] = {}
    for slot in report["slots"]:
        pos_pairs: Counter = Counter()
        wait_buckets: Counter = Counter()
        n_disagree = 0
        n_compare = 0
        # Later picks only (excludes the known empty-roster R1 QB→RB effect).
        later_disagree = 0
        later_compare = 0
        later_pos_pairs: Counter = Counter()
        later_wait: Counter = Counter()
        by_pick_index: dict[int, Counter] = defaultdict(Counter)
        # Reconstruct per-pick comparison counts: each sim traces max_user_picks.
        # Agreements aren't stored per index, so infer from traced − listed disagrees.
        agree_by_index: Counter = Counter()
        disagree_by_index: Counter = Counter()
        for sim in report["by_slot"][slot]["sims"]:
            traced = int(sim["user_picks_traced"])
            disagree_idxs = {int(d["user_pick_index"]) for d in sim["disagreements"]}
            for idx in range(1, traced + 1):
                n_compare += 1
                if idx >= 2:
                    later_compare += 1
                if idx in disagree_idxs:
                    disagree_by_index[idx] += 1
                else:
                    agree_by_index[idx] += 1
            for d in sim["disagreements"]:
                n_disagree += 1
                idx = int(d["user_pick_index"])
                raw_pos = (d["raw"] or {}).get("position") or "?"
                vor_pos = (d["vor"] or {}).get("position") or "?"
                pair = f"{raw_pos}->{vor_pos}"
                pos_pairs[pair] += 1
                bucket = _wait_bucket(d.get("picks_until_next"))
                wait_buckets[bucket] += 1
                by_pick_index[idx][pair] += 1
                if idx >= 2:
                    later_disagree += 1
                    later_pos_pairs[pair] += 1
                    later_wait[bucket] += 1
        out[slot] = {
            "comparisons": n_compare,
            "disagreements": n_disagree,
            "disagree_rate": (n_disagree / n_compare) if n_compare else 0.0,
            "later_comparisons": later_compare,
            "later_disagreements": later_disagree,
            "later_disagree_rate": (later_disagree / later_compare) if later_compare else 0.0,
            "pos_pairs": dict(pos_pairs.most_common()),
            "later_pos_pairs": dict(later_pos_pairs.most_common()),
            "wait_bucket_counts": dict(wait_buckets.most_common()),
            "later_wait_bucket_counts": dict(later_wait.most_common()),
            "by_user_pick_index": {
                str(k): {
                    "disagreements": disagree_by_index[k],
                    "agreements": agree_by_index[k],
                    "pos_pairs": dict(v.most_common()),
                }
                for k, v in sorted(by_pick_index.items())
            },
        }
    return out


def to_markdown(report: dict) -> str:
    agg = _aggregate(report)
    lines = [
        "# Divergence trace — raw marginal vs VOR (disagreements only)",
        "",
        "## Setup",
        "",
        f"- slots: `{report['slots']}`",
        f"- n_sims per slot: **{report['n_sims']}**",
        f"- first user picks traced: **{report['max_user_picks']}**",
        f"- board drivers: `{', '.join(report['board_drivers'])}` "
        "(each sim runs once per driver; CPU paired by `pick_rng(seed, overall)`)",
        f"- seed: `{report['seed']}`",
        f"- preset: `{report['preset']}`",
        "",
        "## What this tests",
        "",
        "- **Hypothesis A (snake/opportunity cost):** disagreements cluster at long "
        "`picks_until_next` (slot 1 early) and shrink when the wait is short (slot 10).",
        "- **Hypothesis B (RB bias):** disagreements are mostly Raw=WR vs VOR=RB "
        "(or similar) even at short waits.",
        "- **Hypothesis C (lineup construction):** position pairs look like scarcity "
        "fixes but later diverge via FLEX/roster composition — inspect later picks.",
        "",
        "## Aggregate (all board drivers × sims)",
        "",
        "Overall rates are dominated by R1 (empty-roster raw QB vs VOR RB). "
        "The **later picks (2–5)** rows are the fairer snake-gap check.",
        "",
        "| slot | all disagree% | later (picks 2–5) disagree% | later wait buckets | later pos pairs (raw→vor) |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for slot in report["slots"]:
        a = agg[slot]
        buckets = ", ".join(
            f"{k}={v}" for k, v in sorted(a["later_wait_bucket_counts"].items())
        ) or "—"
        pairs = (
            ", ".join(f"{k}×{v}" for k, v in list(a["later_pos_pairs"].items())[:4])
            or "—"
        )
        lines.append(
            f"| {slot} | {100 * a['disagree_rate']:.0f}% "
            f"({a['disagreements']}/{a['comparisons']}) | "
            f"{100 * a['later_disagree_rate']:.0f}% "
            f"({a['later_disagreements']}/{a['later_comparisons']}) | "
            f"{buckets} | {pairs} |"
        )

    lines.extend(["", "### By user-pick index", ""])
    for slot in report["slots"]:
        lines.append(f"**Slot {slot}** (R1→R2 others ≈ `{2 * (10 - slot)}`)")
        lines.append("")
        lines.append("| user pick | agree | disagree | top pairs |")
        lines.append("| ---: | ---: | ---: | --- |")
        by_idx = agg[slot]["by_user_pick_index"]
        # Also show pure-agree indexes (no entry in by_idx if zero disagrees).
        for idx in range(1, int(report["max_user_picks"]) + 1):
            info = by_idx.get(str(idx))
            if not info:
                # May still have agreements with zero disagrees — reconstruct from sims.
                agrees = 0
                for sim in report["by_slot"][slot]["sims"]:
                    if idx <= int(sim["user_picks_traced"]) and not any(
                        int(d["user_pick_index"]) == idx for d in sim["disagreements"]
                    ):
                        agrees += 1
                lines.append(f"| {idx} | {agrees} | 0 | — |")
                continue
            pairs = (
                ", ".join(f"{k}×{v}" for k, v in list(info["pos_pairs"].items())[:3])
                or "—"
            )
            lines.append(
                f"| {idx} | {info['agreements']} | {info['disagreements']} | {pairs} |"
            )
        lines.append("")

    lines.extend(["", "## Disagreement log", ""])

    for slot in report["slots"]:
        lines.append(f"### Slot {slot}")
        lines.append("")
        others = 2 * (10 - slot)
        lines.append(
            f"Snake sanity: others between R1 and R2 at this seat ≈ **{others}** "
            f"(`2*(n−k)` with n=10)."
        )
        lines.append("")
        for sim in report["by_slot"][slot]["sims"]:
            if not sim["disagreements"]:
                continue
            lines.append(
                f"#### seed={sim['seed']} · board_driver=`{sim['board_driver']}` "
                f"({sim['agreements']} agreements / "
                f"{len(sim['disagreements'])} disagreements in first "
                f"{sim['user_picks_traced']} user picks)"
            )
            lines.append("")
            for d in sim["disagreements"]:
                raw = d.get("raw") or {}
                vor = d.get("vor") or {}
                lines.append("```")
                lines.append(
                    f"SLOT {slot} — PICK {d['user_pick_index']} "
                    f"(overall #{d['overall_pick']}, round {d['round']})"
                )
                lines.append("")
                lines.append("RAW:")
                lines.append(f"{raw.get('player')} — {raw.get('position')}")
                lines.append(f"proj: {raw.get('projection')}")
                lines.append(f"lineup gain: {raw.get('lineup_gain')}")
                lines.append("")
                lines.append("VOR:")
                lines.append(f"{vor.get('player')} — {vor.get('position')}")
                lines.append(f"proj: {vor.get('projection')}")
                lines.append(f"replacement: {vor.get('replacement_pts')}")
                lines.append(f"VOR: {vor.get('VOR')}")
                lines.append("")
                lines.append(f"next pick: #{d.get('next_user_pick')}")
                lines.append(
                    f"picks until next (others): {d.get('picks_until_next')}"
                )
                lines.append(f"wait distance: {d.get('wait_distance')}")
                lines.append("```")
                lines.append("")
        if not any(sim["disagreements"] for sim in report["by_slot"][slot]["sims"]):
            lines.append("_No disagreements in traced window._")
            lines.append("")

    lines.extend(
        [
            "## Reading guide",
            "",
            "- `picks_until_next` = other players drafted before your next turn.",
            "- `wait_distance` = `next_user_pick − overall_pick` (slot-1 R1→R2 = 19).",
            "- Board driver only affects *continuation* after a disagreement; "
            "each comparison itself is on an identical board state for both strategies.",
            "- Slot 10 still has **long** waits after its turn-around pick "
            "(e.g. #11 → #30), so short R1 gap ≠ short gaps all draft.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Disagreement-only raw vs VOR divergence trace"
    )
    parser.add_argument("--n", type=int, default=5, help="Sims per slot")
    parser.add_argument("--slots", type=str, default="1,5,10")
    parser.add_argument("--picks", type=int, default=5, help="First N user picks")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--drivers",
        type=str,
        default="marginal,marginal_vor",
        help="Comma-separated board drivers",
    )
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/divergence_vor_vs_raw_slots_1_5_10.md",
    )
    args = parser.parse_args()
    slots = [int(x.strip()) for x in args.slots.split(",") if x.strip()]
    drivers = tuple(s.strip() for s in args.drivers.split(",") if s.strip())
    report = run_trace(
        slots=slots,
        n_sims=args.n,
        max_user_picks=args.picks,
        seed=args.seed,
        board_drivers=drivers,
        preset=args.preset,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = to_markdown(report)
    out.write_text(md, encoding="utf-8")
    payload = dict(report)
    payload["aggregate"] = _aggregate(report)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} and {out.with_suffix('.json')}")
    for slot in slots:
        a = payload["aggregate"][slot]
        print(
            f"slot {slot}: {a['disagreements']}/{a['comparisons']} disagree "
            f"({100 * a['disagree_rate']:.0f}%); pairs={a['pos_pairs']}"
        )


if __name__ == "__main__":
    main()
