"""Three-way divergence: raw marginal vs VOR vs V2-alpha (early user picks).

Primary question: what does V2 choose differently, and what future player (q)
does it expect after the ADP-greedy wait?
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
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
from draftopt.strategies import get_strategy
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.strategies.marginal_v2 import MarginalV2Strategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy
from draftopt.vor import replacement_baselines, vor_points


def _enrich(conn, draft_id: str, rec: dict) -> dict:
    pos = (rec.get("position") or "?").upper()
    proj = float(
        rec.get("proj_espn")
        if rec.get("proj_espn") is not None
        else rec.get("season_points")
        or 0.0
    )
    replacement = rec.get("replacement")
    vor = rec.get("vor_points")
    if replacement is None or vor is None:
        draft = conn.execute(
            "SELECT n_teams, roster_json FROM drafts WHERE draft_id = ?",
            (draft_id,),
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
        "ev_two_pick": rec.get("ev_two_pick"),
        "q_player": rec.get("q_player"),
        "q_position": rec.get("q_position"),
        "picks_until_next": rec.get("picks_until_next"),
        "why": rec.get("why"),
    }


def compare_three(conn, draft_id: str, user_slot: int, n_teams: int) -> dict:
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
    v2 = MarginalV2Strategy().recommend(conn, draft_id, n=1)
    if not raw or not vor or not v2:
        return {
            "overall_pick": overall,
            "round": rnd,
            "next_user_pick": nxt,
            "picks_until_next": picks_until_next,
            "wait_distance": wait_distance,
            "all_agree": True,
            "raw": None,
            "vor": None,
            "v2": None,
        }

    raw_c = _enrich(conn, draft_id, raw[0])
    vor_c = _enrich(conn, draft_id, vor[0])
    v2_c = _enrich(conn, draft_id, v2[0])
    ids = {raw_c["player_id"], vor_c["player_id"], v2_c["player_id"]}
    return {
        "user_pick_index": None,
        "overall_pick": overall,
        "round": rnd,
        "next_user_pick": nxt,
        "picks_until_next": picks_until_next,
        "wait_distance": wait_distance,
        "all_agree": len(ids) == 1,
        "raw_vor_agree": raw_c["player_id"] == vor_c["player_id"],
        "raw_v2_agree": raw_c["player_id"] == v2_c["player_id"],
        "vor_v2_agree": vor_c["player_id"] == v2_c["player_id"],
        "raw": raw_c,
        "vor": vor_c,
        "v2": v2_c,
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
    allowed = ("marginal", "marginal_vor", "marginal_v2")
    if board_driver not in allowed:
        raise ValueError(f"board_driver must be one of {allowed}")

    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="v2-div",
        roster_preset=preset,
    )
    driver = get_strategy(board_driver)
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
            cmp = compare_three(conn, draft_id, slot, n_teams)
            cmp["user_pick_index"] = user_picks_seen
            if cmp["all_agree"]:
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
    n_sims: int = 3,
    max_user_picks: int = 5,
    seed: int = 0,
    board_drivers: tuple[str, ...] = ("marginal",),
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


def _aggregate(report: dict) -> dict:
    out: dict[int, dict] = {}
    for slot in report["slots"]:
        triples: Counter = Counter()
        v2_vs_raw: Counter = Counter()
        v2_vs_vor: Counter = Counter()
        q_pos: Counter = Counter()
        n_disagree = 0
        n_compare = 0
        for sim in report["by_slot"][slot]["sims"]:
            traced = int(sim["user_picks_traced"])
            disagree_idxs = {int(d["user_pick_index"]) for d in sim["disagreements"]}
            for idx in range(1, traced + 1):
                n_compare += 1
                if idx not in disagree_idxs:
                    continue
                n_disagree += 1
            for d in sim["disagreements"]:
                rp = (d["raw"] or {}).get("position") or "?"
                vp = (d["vor"] or {}).get("position") or "?"
                v2p = (d["v2"] or {}).get("position") or "?"
                triples[f"{rp}/{vp}/{v2p}"] += 1
                if not d.get("raw_v2_agree"):
                    v2_vs_raw[f"{rp}->{v2p}"] += 1
                if not d.get("vor_v2_agree"):
                    v2_vs_vor[f"{vp}->{v2p}"] += 1
                qp = (d["v2"] or {}).get("q_position")
                if qp:
                    q_pos[qp] += 1
        out[slot] = {
            "comparisons": n_compare,
            "disagreements": n_disagree,
            "disagree_rate": (n_disagree / n_compare) if n_compare else 0.0,
            "pos_triples_raw_vor_v2": dict(triples.most_common()),
            "v2_vs_raw_pairs": dict(v2_vs_raw.most_common()),
            "v2_vs_vor_pairs": dict(v2_vs_vor.most_common()),
            "v2_expected_q_positions": dict(q_pos.most_common()),
        }
    return out


def to_markdown(report: dict) -> str:
    agg = _aggregate(report)
    lines = [
        "# Divergence trace — RAW / VOR / V2-alpha",
        "",
        "## Setup",
        "",
        f"- slots: `{report['slots']}`",
        f"- n_sims per slot: **{report['n_sims']}**",
        f"- first user picks traced: **{report['max_user_picks']}**",
        f"- board drivers: `{', '.join(report['board_drivers'])}`",
        f"- seed: `{report['seed']}`",
        f"- preset: `{report['preset']}`",
        "- V2 lookahead: ADP-greedy (frozen V2-alpha)",
        "- Draft CPU between user picks: noisy ADP (`pick_rng`)",
        "",
        "## Aggregate",
        "",
        "| slot | disagree% | top triples (raw/vor/v2 pos) | V2≠raw pairs | V2 expected q pos |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for slot in report["slots"]:
        a = agg[slot]
        triples = (
            ", ".join(f"{k}×{v}" for k, v in list(a["pos_triples_raw_vor_v2"].items())[:4])
            or "—"
        )
        pairs = (
            ", ".join(f"{k}×{v}" for k, v in list(a["v2_vs_raw_pairs"].items())[:4])
            or "—"
        )
        qpos = (
            ", ".join(f"{k}×{v}" for k, v in list(a["v2_expected_q_positions"].items())[:4])
            or "—"
        )
        lines.append(
            f"| {slot} | {100 * a['disagree_rate']:.0f}% "
            f"({a['disagreements']}/{a['comparisons']}) | {triples} | {pairs} | {qpos} |"
        )

    lines.extend(["", "## Disagreement log", ""])
    for slot in report["slots"]:
        lines.append(f"### Slot {slot}")
        lines.append("")
        any_d = False
        for sim in report["by_slot"][slot]["sims"]:
            if not sim["disagreements"]:
                continue
            any_d = True
            lines.append(
                f"#### seed={sim['seed']} · board_driver=`{sim['board_driver']}` "
                f"({sim['agreements']} all-agree / {len(sim['disagreements'])} disagree)"
            )
            lines.append("")
            for d in sim["disagreements"]:
                raw = d.get("raw") or {}
                vor = d.get("vor") or {}
                v2 = d.get("v2") or {}
                lines.append("```")
                lines.append(
                    f"SLOT {slot} — PICK {d['user_pick_index']} "
                    f"(overall #{d['overall_pick']}, round {d['round']})"
                )
                lines.append("")
                lines.append("RAW:")
                lines.append(f"{raw.get('player')} — {raw.get('position')}")
                lines.append(f"proj: {raw.get('projection')}")
                lines.append(f"lineup_gain: {raw.get('lineup_gain')}")
                lines.append(f"VOR(shadow): {raw.get('VOR')}")
                lines.append("")
                lines.append("VOR:")
                lines.append(f"{vor.get('player')} — {vor.get('position')}")
                lines.append(f"proj: {vor.get('projection')}")
                lines.append(f"replacement: {vor.get('replacement_pts')}")
                lines.append(f"VOR: {vor.get('VOR')}")
                lines.append(f"lineup_gain(VOR-space): {vor.get('lineup_gain')}")
                lines.append("")
                lines.append("V2:")
                lines.append(f"{v2.get('player')} — {v2.get('position')}")
                lines.append(f"proj: {v2.get('projection')}")
                lines.append(f"VOR(shadow): {v2.get('VOR')}")
                lines.append(f"V2 EV (two-pick): {v2.get('ev_two_pick')}")
                lines.append(
                    f"V2 expected future q: {v2.get('q_player')} "
                    f"({v2.get('q_position')})"
                )
                lines.append("")
                lines.append(f"next pick: #{d.get('next_user_pick')}")
                lines.append(f"picks until next (others): {d.get('picks_until_next')}")
                lines.append(f"wait distance: {d.get('wait_distance')}")
                lines.append("```")
                lines.append("")
        if not any_d:
            lines.append("_No disagreements in traced window._")
            lines.append("")

    lines.extend(
        [
            "## Reading guide",
            "",
            "- Log shows turns where **any** of RAW / VOR / V2 disagree on player_id.",
            "- `V2 expected future q` is the ADP-greedy survivor V2 would take at the "
            "next user pick — the opportunity-cost signal.",
            "- Board driver only affects continuation after the logged turn.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAW / VOR / V2-alpha three-way divergence trace"
    )
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--slots", type=str, default="1,5,10")
    parser.add_argument("--picks", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--drivers",
        type=str,
        default="marginal",
        help="Comma-separated board drivers (default: marginal only)",
    )
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/divergence_raw_vor_v2_slots_1_5_10.md",
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
    out.write_text(to_markdown(report), encoding="utf-8")
    payload = dict(report)
    payload["aggregate"] = _aggregate(report)
    out.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} and {out.with_suffix('.json')}")
    for slot in slots:
        a = payload["aggregate"][slot]
        print(
            f"slot {slot}: {a['disagreements']}/{a['comparisons']} disagree "
            f"({100 * a['disagree_rate']:.0f}%); "
            f"v2≠raw={a['v2_vs_raw_pairs']}; q_pos={a['v2_expected_q_positions']}"
        )


if __name__ == "__main__":
    main()
