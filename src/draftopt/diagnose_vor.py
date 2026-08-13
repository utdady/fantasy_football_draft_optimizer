from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    draft_roster,
    is_user_turn,
    record_user_pick,
    round_for_pick,
    snapshot,
)
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool
from draftopt.projection import resolve_projection
from draftopt.strategies.marginal import _user_roster_players
from draftopt.strategies.marginal_vor import MarginalVorStrategy
from draftopt.vor import replacement_snapshot, vor_points


def _as_raw_player(player: dict) -> dict:
    proj = resolve_projection(player, allow_proxy=False)
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "position": player.get("position"),
        "season_points": proj.value,
        "projection_quality": proj.quality,
        "adp_espn": player.get("adp_espn"),
    }


def _as_vor_player(player: dict, baselines: dict[str, float]) -> dict:
    proj = resolve_projection(player, allow_proxy=False)
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "position": player.get("position"),
        "season_points": vor_points(proj.value, player.get("position"), baselines),
        "raw_proj": proj.value,
        "replacement": float(baselines.get((player.get("position") or "").upper()) or 0.0),
        "projection_quality": proj.quality,
        "adp_espn": player.get("adp_espn"),
    }


def trace_decision(conn, draft_id: str, *, top_n: int = 8) -> dict:
    """Full VOR decision dump at the current draft state (no pick made)."""
    from draftopt.draft.state import _draft_row

    draft = _draft_row(conn, draft_id)
    slots = (draft_roster(draft).get("slots") or {})
    n_teams = int(draft["n_teams"])
    overall = int(draft["current_pick"])
    rnd = round_for_pick(overall, n_teams)
    snap = replacement_snapshot(conn, draft_id, n_teams=n_teams, slots=slots)
    baselines = {pos: float(info["replacement_pts"]) for pos, info in snap.items()}

    roster_raw = [
        p
        for p in (_as_raw_player(p) for p in _user_roster_players(conn, draft_id))
        if p["projection_quality"] == "high"
    ]
    roster_vor = [
        p
        for p in (_as_vor_player(p, baselines) for p in _user_roster_players(conn, draft_id))
        if p["projection_quality"] == "high"
    ]
    base_raw = lineup_ev(roster_raw, slots).total
    base_vor = lineup_ev(roster_vor, slots).total

    scored: list[dict] = []
    for cand in candidate_pool(conn, draft_id):
        raw = _as_raw_player(cand)
        vor = _as_vor_player(cand, baselines)
        if raw["projection_quality"] != "high" or raw["season_points"] <= 0:
            continue
        pos = (raw.get("position") or "?").upper()
        info = snap.get(pos) or {}
        raw_gain = lineup_ev(roster_raw + [raw], slots).total - base_raw
        vor_gain = lineup_ev(roster_vor + [vor], slots).total - base_vor
        scored.append(
            {
                "player_id": raw["player_id"],
                "name": raw["name"],
                "position": pos,
                "projection": round(float(raw["season_points"]), 2),
                "replacement_n": info.get("replacement_n"),
                "replacement_pts": round(float(info.get("replacement_pts") or 0.0), 2),
                "replacement_name": info.get("replacement_name"),
                "vor_points": round(float(vor["season_points"]), 2),
                "lineup_gain_raw": round(raw_gain, 2),
                "lineup_gain_vor": round(vor_gain, 2),
                "adp_espn": raw.get("adp_espn"),
            }
        )

    scored.sort(
        key=lambda r: (
            -(r.get("lineup_gain_vor") or 0.0),
            r.get("adp_espn") is None,
            r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
            r.get("name") or "",
        )
    )

    best_by_pos: dict[str, dict] = {}
    for row in scored:
        pos = row["position"]
        if pos not in best_by_pos:
            best_by_pos[pos] = row

    rb = snap.get("RB") or {}
    wr = snap.get("WR") or {}
    return {
        "overall": overall,
        "round": rnd,
        "baselines": snap,
        "rb_vs_wr_replacement": {
            "rb_n": rb.get("replacement_n"),
            "rb_pts": rb.get("replacement_pts"),
            "rb_name": rb.get("replacement_name"),
            "wr_n": wr.get("replacement_n"),
            "wr_pts": wr.get("replacement_pts"),
            "wr_name": wr.get("replacement_name"),
            "rb_minus_wr_pts": round(
                float(rb.get("replacement_pts") or 0.0) - float(wr.get("replacement_pts") or 0.0),
                2,
            ),
        },
        "best_by_pos": best_by_pos,
        "vor_gap_rb_minus_wr": round(
            float((best_by_pos.get("RB") or {}).get("vor_points") or 0.0)
            - float((best_by_pos.get("WR") or {}).get("vor_points") or 0.0),
            2,
        ),
        "top_candidates": scored[:top_n],
        "selected_would_be": scored[0] if scored else None,
    }


def run_traces(
    *,
    n_sims: int = 10,
    slot: int = 1,
    max_round: int = 3,
    seed: int = 0,
    top_n: int = 8,
    preset: str = "league_default",
    conn=None,
    db_path=None,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    strategy = MarginalVorStrategy()
    sims = []
    try:
        for i in range(n_sims):
            sim_seed = seed + i * 1009
            draft_id = create_draft(
                conn,
                user_slot=slot,
                user_name="VOR-diag",
                roster_preset=preset,
            )
            picks = []
            while True:
                state = snapshot(conn, draft_id)
                if state["complete"]:
                    break
                draft_row = conn.execute(
                    "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
                ).fetchone()
                rnd = round_for_pick(int(draft_row["current_pick"]), int(draft_row["n_teams"]))
                if is_user_turn(draft_row):
                    if rnd <= max_round:
                        trace = trace_decision(conn, draft_id, top_n=top_n)
                        picks.append(trace)
                    recs = strategy.recommend(conn, draft_id, n=1)
                    if not recs:
                        break
                    record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")
                    if rnd >= max_round and len(picks) >= max_round:
                        # Still need to finish? For speed, stop after capturing max_round user picks.
                        break
                else:
                    overall = int(draft_row["current_pick"])
                    cpu_pick(conn, draft_id, rng=pick_rng(sim_seed, overall))
            sims.append({"sim": i, "seed": sim_seed, "picks": picks})
        return {
            "n_sims": n_sims,
            "slot": slot,
            "max_round": max_round,
            "seed": seed,
            "preset": preset,
            "sims": sims,
        }
    finally:
        if own:
            conn.close()


def _fmt_baselines(snap: dict) -> str:
    parts = []
    for pos in ("QB", "RB", "WR", "TE", "DST"):
        info = snap.get(pos) or {}
        n = info.get("replacement_n")
        pts = info.get("replacement_pts")
        name = info.get("replacement_name") or "?"
        parts.append(f"{pos}#{n}={pts:.1f} ({name})" if pts is not None else f"{pos}=?")
    return "; ".join(parts)


def to_markdown(report: dict) -> str:
    lines = [
        "# VOR decision-trace diagnostic",
        "",
        "## Setup",
        "",
        f"- n_sims: **{report['n_sims']}** (early rounds only)",
        f"- slot: **{report['slot']}**",
        f"- rounds traced: **1–{report['max_round']}**",
        f"- seed: `{report['seed']}`",
        f"- preset: `{report['preset']}`",
        "- strategy picks: `marginal_vor`",
        "- CPU: noisy ADP (paired pick RNG)",
        "",
        "## Headline: RB#N vs WR#N at pick 1 (sim 0)",
        "",
    ]
    if report["sims"] and report["sims"][0]["picks"]:
        p1 = report["sims"][0]["picks"][0]
        rw = p1["rb_vs_wr_replacement"]
        lines.append(
            f"- RB#{rw['rb_n']} = **{rw['rb_pts']}** (`{rw['rb_name']}`)"
        )
        lines.append(
            f"- WR#{rw['wr_n']} = **{rw['wr_pts']}** (`{rw['wr_name']}`)"
        )
        lines.append(f"- RB#N − WR#N = **{rw['rb_minus_wr_pts']:+.1f}**")
        lines.append(
            f"- Best RB VOR − best WR VOR at pick 1 = **{p1['vor_gap_rb_minus_wr']:+.1f}**"
        )
        lines.append("")
        if (rw.get("rb_pts") or 0) + 1e-6 < (rw.get("wr_pts") or 0):
            lines.append(
                "Interpretation: RB replacement is **lower** than WR at the same N → "
                "elite RB VOR is inflated by a steeper ESPN RB cliff (real scarcity signal "
                "and/or projection artifact), not by unequal FLEX_SHARE ranks."
            )
        else:
            lines.append(
                "Interpretation: RB replacement is **not** lower than WR → RB-heaviness "
                "is likely coming from empty-roster / lineup_ev interaction, not the cliff."
            )
        lines.append("")

    # Aggregate best-by-pos VOR gaps across sims for R1-R3
    lines.append("## Aggregate best-pos VOR by round")
    lines.append("")
    lines.append("| round | mean best RB VOR | mean best WR VOR | mean best QB VOR | mean RB−WR VOR gap |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    by_round: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for sim in report["sims"]:
        for pick in sim["picks"]:
            rnd = int(pick["round"])
            for pos in ("RB", "WR", "QB"):
                row = (pick.get("best_by_pos") or {}).get(pos)
                if row:
                    by_round[rnd][pos].append(float(row["vor_points"]))
            by_round[rnd]["gap"].append(float(pick.get("vor_gap_rb_minus_wr") or 0.0))
    for rnd in sorted(by_round):
        d = by_round[rnd]
        def avg(xs):
            return sum(xs) / len(xs) if xs else 0.0
        lines.append(
            f"| {rnd} | {avg(d['RB']):.1f} | {avg(d['WR']):.1f} | {avg(d['QB']):.1f} | "
            f"{avg(d['gap']):+.1f} |"
        )
    lines.append("")

    lines.append("## Per-sim traces (R1–R3)")
    lines.append("")
    for sim in report["sims"]:
        lines.append(f"### Sim {sim['sim']} (seed={sim['seed']})")
        lines.append("")
        for pick in sim["picks"]:
            sel = pick.get("selected_would_be") or {}
            lines.append(
                f"**Pick {pick['overall']} / Round {pick['round']}** → would take "
                f"**{sel.get('name')}** ({sel.get('position')})"
            )
            lines.append("")
            lines.append(f"Baselines: `{_fmt_baselines(pick['baselines'])}`")
            rw = pick["rb_vs_wr_replacement"]
            lines.append(
                f"RB#N vs WR#N: {rw['rb_pts']} vs {rw['wr_pts']} "
                f"(diff {rw['rb_minus_wr_pts']:+.1f}); "
                f"best RB−WR VOR gap {pick['vor_gap_rb_minus_wr']:+.1f}"
            )
            lines.append("")
            lines.append(
                "| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | "
                "gain_raw | gain_vor |"
            )
            lines.append("| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |")
            for c in pick["top_candidates"]:
                lines.append(
                    f"| {c['name']} | {c['position']} | {c['projection']:.1f} | "
                    f"{c['replacement_n']} | {c['replacement_pts']:.1f} | "
                    f"{c.get('replacement_name') or '—'} | {c['vor_points']:.1f} | "
                    f"{c['lineup_gain_raw']:.1f} | {c['lineup_gain_vor']:.1f} |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="VOR decision-trace diagnostic (R1-R3)")
    parser.add_argument("--n", type=int, default=10, help="Number of sims")
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/diagnose_vor_slot1.md",
    )
    args = parser.parse_args()
    report = run_traces(
        n_sims=args.n,
        slot=args.slot,
        max_round=args.rounds,
        seed=args.seed,
        top_n=args.top,
        preset=args.preset,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out} and {out.with_suffix('.json')}")
    # Short console summary (ASCII-safe)
    if report["sims"] and report["sims"][0]["picks"]:
        p1 = report["sims"][0]["picks"][0]
        rw = p1["rb_vs_wr_replacement"]
        print(
            f"Pick1 RB#{rw['rb_n']}={rw['rb_pts']} vs WR#{rw['wr_n']}={rw['wr_pts']} "
            f"(diff {rw['rb_minus_wr_pts']:+.1f}); "
            f"best RB-WR VOR gap {p1['vor_gap_rb_minus_wr']:+.1f}"
        )
        sel = p1.get("selected_would_be") or {}
        print(f"Would take: {sel.get('name')} ({sel.get('position')})")


if __name__ == "__main__":
    main()
