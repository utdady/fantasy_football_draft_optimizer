"""
Case study: Slot 1 overall #20 — Nabers vs Kyren with one-pick lookahead.

Scientific experiment (not a strategy). Freezes a marginal-driven board at #20,
then compares two-pick roster EV:

  Kyren now + best remaining WR at #21
  vs
  Nabers now + best remaining RB at #21

"Best at #21" = highest ESPN season projection at that position among remaining
players (deterministic; not VOR — avoids circularity).
Primary score = raw lineup_ev starter points (same metric as UI/backtest).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    draft_roster,
    is_user_turn,
    record_user_pick,
    snapshot,
)
from draftopt.lineup import lineup_ev
from draftopt.pool import remaining_ranked
from draftopt.projection import resolve_projection
from draftopt.strategies.marginal import MarginalValueStrategy, _user_roster_players
from draftopt.strategies.marginal_vor import MarginalVorStrategy
from draftopt.vor import replacement_baselines, vor_points


def _as_raw(player: dict) -> dict:
    proj = resolve_projection(player, allow_proxy=False)
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "position": (player.get("position") or "?").upper(),
        "season_points": float(proj.value or 0.0),
        "projection_quality": proj.quality,
        "adp_espn": player.get("adp_espn"),
    }


def _player_brief(p: dict) -> dict:
    return {
        "player_id": p.get("player_id"),
        "name": p.get("name"),
        "position": (p.get("position") or "?").upper(),
        "projection": round(float(p.get("season_points") or 0.0), 2),
        "adp_espn": p.get("adp_espn"),
    }


def best_remaining_at_pos(remaining: list[dict], position: str, *, exclude: set[str]) -> dict | None:
    """Highest ESPN proj among remaining players at `position`."""
    pos = position.upper()
    scored = []
    for p in remaining:
        if p["player_id"] in exclude:
            continue
        if (p.get("position") or "").upper() != pos:
            continue
        raw = _as_raw(p)
        if raw["projection_quality"] != "high" or raw["season_points"] <= 0:
            continue
        scored.append(raw)
    if not scored:
        return None
    scored.sort(
        key=lambda r: (
            -r["season_points"],
            r.get("adp_espn") is None,
            r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
            r.get("name") or "",
        )
    )
    return scored[0]


def decompose_lineup(result) -> dict:
    by_slot: dict[str, list[dict]] = {}
    slot_totals: dict[str, float] = {}
    for slot, players in (result.starters or {}).items():
        rows = [_player_brief(p) for p in players]
        by_slot[slot] = rows
        slot_totals[slot] = round(sum(float(p["projection"]) for p in rows), 2)
    return {
        "total": round(float(result.total), 2),
        "by_slot": by_slot,
        "slot_totals": slot_totals,
        "rb_starter_pts": round(
            slot_totals.get("RB", 0.0) + sum(
                float(p["projection"])
                for p in by_slot.get("FLEX", [])
                if p["position"] == "RB"
            ),
            2,
        ),
        "wr_starter_pts": round(
            slot_totals.get("WR", 0.0) + sum(
                float(p["projection"])
                for p in by_slot.get("FLEX", [])
                if p["position"] == "WR"
            ),
            2,
        ),
        "flex_contribution": slot_totals.get("FLEX", 0.0),
        "flex_players": by_slot.get("FLEX", []),
        "bench": [_player_brief(p) for p in result.bench],
    }


def advance_to_overall(
    conn,
    *,
    slot: int = 1,
    target_overall: int = 20,
    seed: int = 0,
    preset: str = "league_default",
) -> str:
    """Create draft; raw marginal picks on user turns until current_pick == target."""
    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="case-study",
        roster_preset=preset,
    )
    driver = MarginalValueStrategy()
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            raise RuntimeError("draft completed before reaching target overall")
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        overall = int(draft_row["current_pick"])
        if overall == target_overall:
            if not is_user_turn(draft_row):
                raise RuntimeError(
                    f"overall #{target_overall} is not user turn for slot {slot}"
                )
            return draft_id
        if overall > target_overall:
            raise RuntimeError(f"passed target overall (now #{overall})")
        if is_user_turn(draft_row):
            recs = driver.recommend(conn, draft_id, n=1)
            if not recs:
                raise RuntimeError(f"no raw recommendation at overall #{overall}")
            record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")
        else:
            cpu_pick(conn, draft_id, rng=pick_rng(seed, overall))


def run_case_study(
    *,
    seed: int = 0,
    slot: int = 1,
    target_overall: int = 20,
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

    try:
        draft_id = advance_to_overall(
            conn,
            slot=slot,
            target_overall=target_overall,
            seed=seed,
            preset=preset,
        )
        draft = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        slots = draft_roster(draft).get("slots") or {}
        n_teams = int(draft["n_teams"])

        roster_raw = [
            p
            for p in (_as_raw(p) for p in _user_roster_players(conn, draft_id))
            if p["projection_quality"] == "high"
        ]
        remaining = remaining_ranked(conn, draft_id)

        raw_rec = MarginalValueStrategy().recommend(conn, draft_id, n=1)
        vor_rec = MarginalVorStrategy().recommend(conn, draft_id, n=1)
        if not raw_rec or not vor_rec:
            raise RuntimeError("missing strategy recommendations at freeze point")

        nabers = _as_raw(raw_rec[0])
        kyren = _as_raw(vor_rec[0])
        # Keep names explicit in the report even if strategies ever change.
        decision = {
            "raw_choice": _player_brief(nabers),
            "vor_choice": _player_brief(kyren),
            "agree": nabers["player_id"] == kyren["player_id"],
        }

        baselines = replacement_baselines(conn, draft_id, n_teams=n_teams, slots=slots)

        def branch(now: dict, next_pos: str, label: str) -> dict:
            nxt = best_remaining_at_pos(
                remaining, next_pos, exclude={now["player_id"]}
            )
            if nxt is None:
                raise RuntimeError(f"no remaining {next_pos} for branch {label}")
            roster = roster_raw + [now, nxt]
            ev = lineup_ev(roster, slots)
            decomp = decompose_lineup(ev)
            # Footnote: same roster scored in VOR-space (not primary verdict).
            vor_roster = []
            for p in roster:
                vor_roster.append(
                    {
                        **p,
                        "season_points": vor_points(
                            float(p["season_points"]), p["position"], baselines
                        ),
                        "raw_proj": float(p["season_points"]),
                    }
                )
            vor_ev = lineup_ev(vor_roster, slots)
            return {
                "label": label,
                "pick_now": _player_brief(now),
                "pick_now_vor": round(
                    vor_points(float(now["season_points"]), now["position"], baselines),
                    2,
                ),
                "pick_21": _player_brief(nxt),
                "pick_21_rule": f"best remaining {next_pos} by ESPN proj",
                "lineup": decomp,
                "vor_space_total": round(float(vor_ev.total), 2),
            }

        branch_kyren = branch(kyren, "WR", "Kyren + best WR@21")
        branch_nabers = branch(nabers, "RB", "Nabers + best RB@21")

        delta = round(
            branch_nabers["lineup"]["total"] - branch_kyren["lineup"]["total"], 2
        )

        # Secondary: if the other fork candidate is unavailable at #21 (the
        # interesting case when wait > 0), what is the EV gap?
        def branch_excluding(now: dict, next_pos: str, exclude_id: str, label: str) -> dict:
            nxt = best_remaining_at_pos(
                remaining, next_pos, exclude={now["player_id"], exclude_id}
            )
            if nxt is None:
                raise RuntimeError(f"no remaining {next_pos} for branch {label}")
            roster = roster_raw + [now, nxt]
            ev = lineup_ev(roster, slots)
            return {
                "label": label,
                "pick_now": _player_brief(now),
                "pick_21": _player_brief(nxt),
                "pick_21_rule": (
                    f"best remaining {next_pos} by ESPN proj, "
                    f"excluding the other fork candidate"
                ),
                "lineup": decompose_lineup(ev),
            }

        kyren_if_nabers_gone = branch_excluding(
            kyren, "WR", nabers["player_id"], "Kyren + best WR≠Nabers@21"
        )
        nabers_if_kyren_gone = branch_excluding(
            nabers, "RB", kyren["player_id"], "Nabers + best RB≠Kyren@21"
        )
        delta_if_other_gone = round(
            nabers_if_kyren_gone["lineup"]["total"]
            - kyren_if_nabers_gone["lineup"]["total"],
            2,
        )

        commutative = (
            branch_kyren["pick_21"]["player_id"] == nabers["player_id"]
            and branch_nabers["pick_21"]["player_id"] == kyren["player_id"]
        )

        if commutative and abs(delta) < 0.5:
            verdict = "commutative_tie"
            meaning = (
                "With back-to-back picks and both players still available, "
                "best WR after Kyren is Nabers and best RB after Nabers is Kyren — "
                "the branches draft the same two players (order irrelevant). "
                "This fork cannot adjudicate positional VOR; the relevant question "
                "is the secondary 'other player gone' gap, or a longer-wait fork."
            )
        elif abs(delta) < 0.5:
            verdict = "tie"
            meaning = (
                "Branches essentially equal on two-pick raw starter EV — "
                "VOR's RB preference is not grossly wrong at this fork."
            )
        elif delta > 0:
            verdict = "nabers_branch_wins"
            meaning = (
                "Nabers + best RB@21 beats Kyren + best WR@21 on raw starter EV. "
                "Positional VOR can select the wrong player even with zero wait."
            )
        else:
            verdict = "kyren_branch_wins"
            meaning = (
                "Kyren + best WR@21 beats Nabers + best RB@21 on raw starter EV. "
                "VOR's RB preference is justified at this fork."
            )

        return {
            "experiment": "pick20_nabers_vs_kyren_lookahead",
            "seed": seed,
            "slot": slot,
            "target_overall": target_overall,
            "board_driver": "marginal",
            "preset": preset,
            "freeze": {
                "overall": target_overall,
                "current_roster": [_player_brief(p) for p in roster_raw],
                "current_lineup_ev": round(
                    float(lineup_ev(roster_raw, slots).total), 2
                ),
            },
            "decision_at_20": decision,
            "branch_a_vor_choice": branch_kyren,
            "branch_b_alternative": branch_nabers,
            "delta_nabers_minus_kyren": delta,
            "commutative": commutative,
            "secondary_if_other_gone": {
                "kyren_branch": kyren_if_nabers_gone,
                "nabers_branch": nabers_if_kyren_gone,
                "delta_nabers_minus_kyren": delta_if_other_gone,
                "note": (
                    "Counterfactual: complementary #21 cannot be the other fork "
                    "candidate (as if CPU took them between picks). Relevant when "
                    "wait > 0; not the literal #20→#21 board."
                ),
            },
            "verdict": verdict,
            "meaning": meaning,
            "scoring": {
                "primary": "raw lineup_ev starter points (ESPN projections)",
                "pick_21_rule": "highest ESPN proj at complementary position",
                "footnote": "vor_space_total scores the same roster in VOR units",
            },
        }
    finally:
        if own:
            conn.close()


def to_markdown(report: dict) -> str:
    a = report["branch_a_vor_choice"]
    b = report["branch_b_alternative"]
    freeze = report["freeze"]
    dec = report["decision_at_20"]
    lines = [
        "# Case study — Pick #20 Nabers vs Kyren (one-pick lookahead)",
        "",
        "## Setup",
        "",
        f"- seed: `{report['seed']}`",
        f"- slot: **{report['slot']}**",
        f"- freeze overall: **#{report['target_overall']}**",
        f"- board driver to freeze: `{report['board_driver']}` (raw R1 already made)",
        f"- preset: `{report['preset']}`",
        f"- pick #21 rule: {report['scoring']['pick_21_rule']}",
        f"- primary score: {report['scoring']['primary']}",
        "",
        "## Question",
        "",
        "At slot 1 pick #20 the wait to #21 is **one pick** (zero others). "
        "Does positional VOR's Kyren choice beat the cross-positional alternative "
        "Nabers + best RB at #21 on **final two-pick raw starter EV**?",
        "",
        "## Freeze state",
        "",
        f"Current roster EV: **{freeze['current_lineup_ev']:.1f}**",
        "",
    ]
    for p in freeze["current_roster"]:
        lines.append(f"- {p['name']} ({p['position']}) — {p['projection']:.1f}")
    lines.extend(
        [
            "",
            "### Strategy recommendations at #20",
            "",
            f"- RAW → **{dec['raw_choice']['name']}** ({dec['raw_choice']['position']}) "
            f"proj {dec['raw_choice']['projection']:.1f}",
            f"- VOR → **{dec['vor_choice']['name']}** ({dec['vor_choice']['position']}) "
            f"proj {dec['vor_choice']['projection']:.1f}",
            "",
            "## Branches",
            "",
        ]
    )

    def dump_branch(title: str, br: dict) -> None:
        L = br["lineup"]
        lines.append(f"### {title}")
        lines.append("")
        now_extra = ""
        if br.get("pick_now_vor") is not None:
            now_extra = f" (positional VOR {br['pick_now_vor']:.1f})"
        lines.append(
            f"- Now: **{br['pick_now']['name']}** ({br['pick_now']['position']}) "
            f"proj {br['pick_now']['projection']:.1f}{now_extra}"
        )
        lines.append(
            f"- #21: **{br['pick_21']['name']}** ({br['pick_21']['position']}) "
            f"proj {br['pick_21']['projection']:.1f} "
            f"— _{br['pick_21_rule']}_"
        )
        lines.append(f"- Final starter points: **{L['total']:.1f}**")
        if br.get("vor_space_total") is not None:
            lines.append(
                f"- VOR-space starter total (footnote): {br['vor_space_total']:.1f}"
            )
        lines.append("")
        lines.append("| slot | players | pts |")
        lines.append("| --- | --- | ---: |")
        for slot in ("QB", "RB", "WR", "TE", "FLEX", "DST", "K"):
            plist = L["by_slot"].get(slot) or []
            if not plist and L["slot_totals"].get(slot, 0) == 0:
                continue
            names = ", ".join(
                f"{p['name']} ({p['projection']:.1f})" for p in plist
            ) or "—"
            lines.append(f"| {slot} | {names} | {L['slot_totals'].get(slot, 0):.1f} |")
        lines.append("")
        lines.append(
            f"- RB starter contribution (RB slots + RB-in-FLEX): "
            f"**{L['rb_starter_pts']:.1f}**"
        )
        lines.append(
            f"- WR starter contribution (WR slots + WR-in-FLEX): "
            f"**{L['wr_starter_pts']:.1f}**"
        )
        lines.append(f"- FLEX contribution: **{L['flex_contribution']:.1f}**")
        if L["bench"]:
            bench = ", ".join(
                f"{p['name']} ({p['position']} {p['projection']:.1f})" for p in L["bench"]
            )
            lines.append(f"- Bench (unused): {bench}")
        else:
            lines.append("- Bench (unused): —")
        lines.append("")

    dump_branch("Branch A — VOR choice (Kyren + best WR@21)", a)
    dump_branch("Branch B — alternative (Nabers + best RB@21)", b)

    sec = report.get("secondary_if_other_gone") or {}
    if sec:
        lines.extend(
            [
                "## Secondary counterfactual — other fork candidate gone at #21",
                "",
                sec.get("note") or "",
                "",
            ]
        )
        dump_branch("Kyren now + best WR ≠ Nabers", sec["kyren_branch"])
        dump_branch("Nabers now + best RB ≠ Kyren", sec["nabers_branch"])
        lines.append(
            f"**Δ if other gone** (Nabers branch − Kyren branch) = "
            f"**{sec['delta_nabers_minus_kyren']:+.1f}**"
        )
        lines.append("")

    lines.extend(
        [
            "## Verdict",
            "",
            f"- Commutative (mutual complements)? "
            f"**{'yes' if report.get('commutative') else 'no'}**",
            f"- Δ (Nabers branch − Kyren branch) = "
            f"**{report['delta_nabers_minus_kyren']:+.1f}**",
            f"- Outcome: `{report['verdict']}`",
            f"- {report['meaning']}",
            "",
            "## Interpretation guide",
            "",
            "- If branches are **commutative** (each other's #21 pick) → back-to-back "
            "ownership means order cannot change the two-pick roster; this fork does "
            "not test VOR vs raw value — look at longer waits or the secondary gap.",
            "- If Nabers branch wins (non-commutative) → positional VOR ≠ final roster "
            "value even with no waiting cost → strong case for V2-alpha.",
            "- If Kyren branch wins → VOR's RB preference is justified here.",
            "- Secondary Δ (other gone) approximates the stake when survival matters.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pick #20 Nabers vs Kyren one-pick lookahead case study"
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--overall", type=int, default=20)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/case_study_pick20_nabers_vs_kyren.md",
    )
    args = parser.parse_args()
    report = run_case_study(
        seed=args.seed,
        slot=args.slot,
        target_overall=args.overall,
        preset=args.preset,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out} and {out.with_suffix('.json')}")
    print(
        f"verdict={report['verdict']} Δ={report['delta_nabers_minus_kyren']:+.1f} "
        f"nabers={report['branch_b_alternative']['lineup']['total']:.1f} "
        f"kyren={report['branch_a_vor_choice']['lineup']['total']:.1f}"
    )


if __name__ == "__main__":
    main()
