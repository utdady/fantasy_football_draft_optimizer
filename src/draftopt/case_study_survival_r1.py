"""
Causal diagnostic: does explicit q-survival flip Chase vs Daniels at slot-1 #1?

Frozen failure state from proj-greedy V2 stress:
  overall #1, slot 1, wait 18, empty roster, Chase take-now, Daniels deferred q.

Records per-future policy disagreement (survives ✓/✗) — does NOT invent P=2/3.
Then compares take-q-now vs take-Chase-now under each future, including the
death branch where the deferred QB is gone.

Secondary: same survival table for Fields & Stafford after Chase removed
(R1 board), plus authentic #20 board after Chase + 18 proj-greedy CPU picks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.case_study_pick20 import _as_raw, _player_brief, best_remaining_at_pos
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import (
    create_draft,
    draft_roster,
    is_user_turn,
    record_user_pick,
    snapshot,
)
from draftopt.lookahead import (
    BETA_FUTURE_POLICIES,
    advance_future,
    as_lineup_player,
    best_raw_marginal_q,
    two_pick_ev,
)
from draftopt.lineup import lineup_ev
from draftopt.pool import remaining_ranked
from draftopt.strategies.marginal_v2 import MarginalV2Strategy
from draftopt.strategies.marginal_v2_beta import MarginalV2BetaStrategy
from draftopt.vor import replacement_baselines_from_remaining, vor_points

FUTURES = BETA_FUTURE_POLICIES


def _find_by_name(remaining: list[dict], name: str) -> dict:
    key = name.strip().lower()
    for p in remaining:
        if (p.get("name") or "").strip().lower() == key:
            return p
    # substring fallback
    hits = [p for p in remaining if key in (p.get("name") or "").lower()]
    if len(hits) == 1:
        return hits[0]
    raise LookupError(f"player not found uniquely: {name!r} (hits={len(hits)})")


def _rank_tables(remaining: list[dict], *, slots: dict, n_teams: int) -> dict:
    """ADP / proj / VOR ranks (1-based) among remaining high-quality players."""
    adp_order = list(remaining)  # remaining_ranked is ADP-sorted
    proj_order = sorted(
        [p for p in remaining if _as_raw(p)["projection_quality"] == "high"],
        key=lambda p: (
            -float(_as_raw(p)["season_points"]),
            p.get("adp_espn") is None,
            p.get("adp_espn") if p.get("adp_espn") is not None else 9999,
            p.get("name") or "",
        ),
    )
    baselines = replacement_baselines_from_remaining(
        remaining, n_teams=n_teams, slots=slots
    )
    vor_order = sorted(
        [p for p in remaining if _as_raw(p)["projection_quality"] == "high"],
        key=lambda p: (
            -vor_points(
                float(_as_raw(p)["season_points"]),
                p.get("position"),
                baselines,
            ),
            -float(_as_raw(p)["season_points"]),
            p.get("adp_espn") is None,
            p.get("adp_espn") if p.get("adp_espn") is not None else 9999,
            p.get("name") or "",
        ),
    )

    def rank_of(order: list[dict], pid: str) -> int | None:
        for i, p in enumerate(order, start=1):
            if p["player_id"] == pid:
                return i
        return None

    out = {}
    for p in remaining:
        pid = p["player_id"]
        raw = _as_raw(p)
        if raw["projection_quality"] != "high":
            continue
        out[pid] = {
            "name": p.get("name"),
            "position": (p.get("position") or "?").upper(),
            "proj": round(float(raw["season_points"]), 2),
            "adp_espn": p.get("adp_espn"),
            "adp_rank": rank_of(adp_order, pid),
            "proj_rank": rank_of(proj_order, pid),
            "vor_rank": rank_of(vor_order, pid),
            "vor": round(
                vor_points(float(raw["season_points"]), p.get("position"), baselines),
                2,
            ),
        }
    return out


def _survives(survivors: list[dict], player_id: str) -> bool:
    return any(p.get("player_id") == player_id for p in survivors)


def diagnose_q_survival(
    *,
    roster: list[dict],
    remaining: list[dict],
    take_now: dict,
    deferred_q: dict,
    slots: dict,
    n_teams: int,
    n_cpu: int,
) -> dict:
    """
    Per-future survival of deferred_q after take_now, plus two-pick EVs for
    take_now vs take deferred_q now.
    """
    take_lined = as_lineup_player(take_now)
    q_lined = as_lineup_player(deferred_q)
    after_take = [r for r in remaining if r["player_id"] != take_now["player_id"]]
    after_q = [r for r in remaining if r["player_id"] != deferred_q["player_id"]]

    one_take = lineup_ev(roster + [take_lined], slots).total
    one_q = lineup_ev(roster + [q_lined], slots).total

    by_future: dict[str, dict] = {}
    for pol in FUTURES:
        survivors_after_take = advance_future(
            after_take, n_cpu, pol, slots=slots, n_teams=n_teams
        )
        survivors_after_q = advance_future(
            after_q, n_cpu, pol, slots=slots, n_teams=n_teams
        )
        q_alive = _survives(survivors_after_take, deferred_q["player_id"])

        best_after_take, _ = best_raw_marginal_q(
            roster + [take_lined], survivors_after_take, slots
        )
        best_qb = best_remaining_at_pos(
            survivors_after_take, "QB", exclude=set()
        )
        # Force QB second pick when measuring death-branch replacement.
        qb_lined = as_lineup_player(best_qb) if best_qb else None
        if best_qb and qb_lined and qb_lined["projection_quality"] == "high":
            chase_plus_qb = lineup_ev(
                roster + [take_lined, qb_lined], slots
            ).total
        else:
            chase_plus_qb = one_take

        if best_after_take is not None:
            chase_plus_best = lineup_ev(
                roster + [take_lined, best_after_take], slots
            ).total
        else:
            chase_plus_best = one_take

        # Counterfactual: if we could still take deferred q at next pick.
        if q_alive:
            chase_plus_deferred = lineup_ev(
                roster + [take_lined, q_lined], slots
            ).total
        else:
            chase_plus_deferred = None

        ev_take_q_now = two_pick_ev(
            roster,
            deferred_q,
            remaining,
            slots,
            n_cpu_picks=n_cpu,
            future_policy=pol,
            n_teams=n_teams,
        )
        ev_take_now = two_pick_ev(
            roster,
            take_now,
            remaining,
            slots,
            n_cpu_picks=n_cpu,
            future_policy=pol,
            n_teams=n_teams,
        )

        by_future[pol] = {
            "q_survives": q_alive,
            "best_second_after_take": _player_brief(best_after_take)
            if best_after_take
            else None,
            "best_qb_after_take": _player_brief(qb_lined) if qb_lined else None,
            "ev_take_now_plus_best": round(float(chase_plus_best), 2),
            "ev_take_now_plus_best_qb": round(float(chase_plus_qb), 2),
            "ev_take_now_plus_deferred_if_alive": (
                round(float(chase_plus_deferred), 2)
                if chase_plus_deferred is not None
                else None
            ),
            "ev_take_deferred_now_two_pick": round(float(ev_take_q_now["ev"]), 2),
            "q_after_taking_deferred": _player_brief(ev_take_q_now["q"])
            if ev_take_q_now.get("q")
            else None,
            "ev_take_now_two_pick": round(float(ev_take_now["ev"]), 2),
            "q_after_taking_now": _player_brief(ev_take_now["q"])
            if ev_take_now.get("q")
            else None,
            "delta_deferred_now_minus_take_now": round(
                float(ev_take_q_now["ev"]) - float(ev_take_now["ev"]), 2
            ),
            # Death-branch lens: take deferred now vs take-now + replacement QB
            "delta_deferred_now_minus_take_now_plus_qb": round(
                float(ev_take_q_now["ev"]) - float(chase_plus_qb), 2
            ),
        }

    disagreement = {
        pol: ("survives" if by_future[pol]["q_survives"] else "dies")
        for pol in FUTURES
    }
    # Outcome A vs B under the proj death branch (if it dies there).
    proj = by_future.get("proj_greedy") or {}
    death_flips = None
    if proj and not proj.get("q_survives"):
        # Knowing q dies: does take-q-now beat take-now + best QB?
        death_flips = proj["delta_deferred_now_minus_take_now_plus_qb"] > 1e-6

    return {
        "take_now": _player_brief(take_lined),
        "deferred_q": _player_brief(q_lined),
        "n_cpu_picks": n_cpu,
        "one_pick_take_now": round(float(one_take), 2),
        "one_pick_deferred": round(float(one_q), 2),
        "delta_one_pick_deferred_minus_take": round(float(one_q - one_take), 2),
        "policy_disagreement": disagreement,
        "by_future": by_future,
        "outcome_hint": {
            "proj_q_dies": bool(proj and not proj.get("q_survives")),
            "under_proj_death_take_deferred_beats_take_plus_qb": death_flips,
            "reading": (
                "Outcome A (survival explains it): under proj death, "
                "taking deferred q now beats take-now + replacement QB"
                if death_flips
                else (
                    "Outcome B (survival insufficient): even knowing deferred q "
                    "dies under proj, take-now + replacement QB still wins "
                    "(or q does not die under proj)"
                    if death_flips is False
                    else "inconclusive (proj does not kill q)"
                )
            ),
        },
    }


def _advance_chase_then_cpu(
    conn,
    *,
    chase_id: str,
    n_cpu: int,
    opponent_policy: str,
    seed: int,
    preset: str,
) -> str:
    draft_id = create_draft(
        conn,
        user_slot=1,
        user_name="survival-diag",
        roster_preset=preset,
    )
    record_user_pick(conn, draft_id, chase_id, made_by="diagnostic")
    for _ in range(n_cpu):
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        overall = int(draft_row["current_pick"])
        if is_user_turn(draft_row):
            raise RuntimeError("unexpected user turn during CPU advance")
        cpu_pick(
            conn,
            draft_id,
            rng=pick_rng(seed, overall),
            policy=opponent_policy,
        )
    return draft_id


def run_diagnostic(
    *,
    seed: int = 0,
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
        draft_id = create_draft(
            conn,
            user_slot=1,
            user_name="survival-r1",
            roster_preset=preset,
        )
        draft = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        slots = draft_roster(draft).get("slots") or {}
        n_teams = int(draft["n_teams"])
        n_rounds = int(draft["n_rounds"])
        overall = int(draft["current_pick"])
        assert overall == 1
        n_cpu = picks_until_next(overall, 1, n_teams, n_rounds=n_rounds)
        nxt = next_user_overall(overall, 1, n_teams, n_rounds=n_rounds)
        assert n_cpu == 18 and nxt == 20

        remaining = remaining_ranked(conn, draft_id)
        ranks = _rank_tables(remaining, slots=slots, n_teams=n_teams)

        chase = _find_by_name(remaining, "Ja'Marr Chase")
        daniels = _find_by_name(remaining, "Jayden Daniels")
        fields = _find_by_name(remaining, "Justin Fields")
        stafford = _find_by_name(remaining, "Matthew Stafford")

        alpha = MarginalV2Strategy().recommend(conn, draft_id, n=1)[0]
        beta = MarginalV2BetaStrategy().recommend(conn, draft_id, n=1)[0]

        primary = diagnose_q_survival(
            roster=[],
            remaining=remaining,
            take_now=chase,
            deferred_q=daniels,
            slots=slots,
            n_teams=n_teams,
            n_cpu=int(n_cpu),
        )
        secondary_fields = diagnose_q_survival(
            roster=[],
            remaining=remaining,
            take_now=chase,
            deferred_q=fields,
            slots=slots,
            n_teams=n_teams,
            n_cpu=int(n_cpu),
        )
        secondary_stafford = diagnose_q_survival(
            roster=[],
            remaining=remaining,
            take_now=chase,
            deferred_q=stafford,
            slots=slots,
            n_teams=n_teams,
            n_cpu=int(n_cpu),
        )

        # Authentic #20 board: Chase + 18 proj-greedy CPU picks.
        d20 = _advance_chase_then_cpu(
            conn,
            chase_id=chase["player_id"],
            n_cpu=int(n_cpu),
            opponent_policy="proj_greedy",
            seed=seed,
            preset=preset,
        )
        draft20 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d20,)
        ).fetchone()
        overall20 = int(draft20["current_pick"])
        rem20 = remaining_ranked(conn, d20)
        daniels_alive_20 = any(
            p["player_id"] == daniels["player_id"] for p in rem20
        )
        fields_alive_20 = any(p["player_id"] == fields["player_id"] for p in rem20)
        stafford_alive_20 = any(
            p["player_id"] == stafford["player_id"] for p in rem20
        )
        v2_at_20 = MarginalV2Strategy().recommend(conn, d20, n=3)
        n_cpu_20 = picks_until_next(overall20, 1, n_teams, n_rounds=n_rounds)

        board20_diag = None
        if fields_alive_20 and v2_at_20:
            # Use α's top rec as take_now; Fields as deferred if still the story.
            take20 = _find_by_name(rem20, v2_at_20[0]["name"])
            # Prefer Fields as deferred q if present; else α's stated q.
            deferred20_name = v2_at_20[0].get("q_player") or "Justin Fields"
            try:
                deferred20 = _find_by_name(rem20, deferred20_name)
            except LookupError:
                deferred20 = _find_by_name(rem20, "Justin Fields")
            roster20 = [
                as_lineup_player(chase)
            ]  # only Chase on user roster after R1
            # Rebuild roster from DB picks for accuracy.
            from draftopt.strategies.marginal import _user_roster_players

            roster20 = [
                p
                for p in (
                    as_lineup_player(r) for r in _user_roster_players(conn, d20)
                )
                if p["projection_quality"] == "high"
            ]
            board20_diag = diagnose_q_survival(
                roster=roster20,
                remaining=rem20,
                take_now=take20,
                deferred_q=deferred20,
                slots=slots,
                n_teams=n_teams,
                n_cpu=int(n_cpu_20 or 0),
            )

        return {
            "state": {
                "slot": 1,
                "overall": 1,
                "next_user_pick": nxt,
                "picks_until_next": n_cpu,
                "roster": [],
                "failure_source": "proj_greedy V2 stress / β pilot R1",
            },
            "strategy_picks_r1": {
                "marginal_v2": {
                    "name": alpha.get("name"),
                    "position": alpha.get("position"),
                    "q_player": alpha.get("q_player"),
                    "ev_two_pick": alpha.get("ev_two_pick"),
                    "why": alpha.get("why"),
                },
                "marginal_v2_beta": {
                    "name": beta.get("name"),
                    "position": beta.get("position"),
                    "q_player": beta.get("q_player"),
                    "ev_two_pick": beta.get("ev_two_pick"),
                    "ev_by_future": beta.get("ev_by_future"),
                    "why": beta.get("why"),
                },
            },
            "player_ranks": {
                chase["player_id"]: ranks.get(chase["player_id"]),
                daniels["player_id"]: ranks.get(daniels["player_id"]),
                fields["player_id"]: ranks.get(fields["player_id"]),
                stafford["player_id"]: ranks.get(stafford["player_id"]),
            },
            "primary_chase_daniels": primary,
            "secondary_r1_board_fields": secondary_fields,
            "secondary_r1_board_stafford": secondary_stafford,
            "after_chase_proj18": {
                "overall": overall20,
                "daniels_still_available": daniels_alive_20,
                "fields_still_available": fields_alive_20,
                "stafford_still_available": stafford_alive_20,
                "v2_top3": [
                    {
                        "name": r.get("name"),
                        "position": r.get("position"),
                        "q_player": r.get("q_player"),
                        "ev_two_pick": r.get("ev_two_pick"),
                    }
                    for r in v2_at_20
                ],
                "diagnostic": board20_diag,
            },
            "verdict": primary["outcome_hint"],
        }
    finally:
        if own:
            conn.close()


def to_markdown(report: dict) -> str:
    s = report["state"]
    prim = report["primary_chase_daniels"]
    lines = [
        "# Survival diagnostic: Chase / Daniels @ slot-1 #1",
        "",
        "## Question",
        "",
        "Is the proj-greedy V2 failure caused by missing **explicit survival risk** "
        "for the deferred player (Outcome A), or does the **downstream roster** "
        "still prefer Chase even when Daniels is known dead (Outcome B)?",
        "",
        "## Frozen state",
        "",
        f"- slot `{s['slot']}`, overall `#{s['overall']}`, next `#{s['next_user_pick']}`, "
        f"wait **{s['picks_until_next']}**",
        f"- source: {s['failure_source']}",
        "- roster: empty",
        "- take-now candidate: **Ja'Marr Chase**; deferred q: **Jayden Daniels**",
        "- policy disagreement only (no invented P=2/3)",
        "",
        "## What α / β actually pick",
        "",
    ]
    for name, row in (report.get("strategy_picks_r1") or {}).items():
        lines.append(
            f"- `{name}`: **{row.get('name')}** ({row.get('position')}) "
            f"q={row.get('q_player')} EV={row.get('ev_two_pick')}"
        )
        if row.get("ev_by_future"):
            lines.append(f"  - ev_by_future: `{row['ev_by_future']}`")
    lines.extend(["", "## Player ranks (among remaining @ #1)", ""])
    lines.append("| player | pos | proj | ADP rank | proj rank | VOR rank | VOR |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for info in (report.get("player_ranks") or {}).values():
        if not info:
            continue
        lines.append(
            f"| {info['name']} | {info['position']} | {info['proj']:.1f} | "
            f"{info.get('adp_rank')} | {info.get('proj_rank')} | "
            f"{info.get('vor_rank')} | {info.get('vor'):.1f} |"
        )

    def _future_table(block: dict, title: str) -> None:
        lines.extend(["", f"## {title}", ""])
        lines.append(
            f"- one-pick: take-now={block['one_pick_take_now']:.1f}, "
            f"deferred={block['one_pick_deferred']:.1f} "
            f"(Δ deferred−take = {block['delta_one_pick_deferred_minus_take']:+.1f})"
        )
        lines.append(
            f"- policy disagreement: `{block['policy_disagreement']}`"
        )
        lines.extend(
            [
                "",
                "| future | q survives? | take-now + best q | take-now + best QB | "
                "deferred-now two-pick | Δ (deferred−take) | Δ (deferred − take+QB) |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for pol in FUTURES:
            f = block["by_future"][pol]
            surv = "✓" if f["q_survives"] else "✗"
            bq = (f.get("best_second_after_take") or {}).get("name") or "—"
            bqb = (f.get("best_qb_after_take") or {}).get("name") or "—"
            lines.append(
                f"| {pol} | {surv} | {f['ev_take_now_plus_best']:.1f} ({bq}) | "
                f"{f['ev_take_now_plus_best_qb']:.1f} ({bqb}) | "
                f"{f['ev_take_deferred_now_two_pick']:.1f} | "
                f"{f['delta_deferred_now_minus_take_now']:+.1f} | "
                f"{f['delta_deferred_now_minus_take_now_plus_qb']:+.1f} |"
            )
        hint = block.get("outcome_hint") or {}
        lines.extend(
            [
                "",
                f"**Outcome hint:** {hint.get('reading')}",
                "",
            ]
        )

    _future_table(prim, "Primary: Chase now vs Daniels now")
    _future_table(
        report["secondary_r1_board_fields"],
        "Secondary (same R1 board): Chase now vs Fields deferred",
    )
    _future_table(
        report["secondary_r1_board_stafford"],
        "Secondary (same R1 board): Chase now vs Stafford deferred",
    )

    a20 = report.get("after_chase_proj18") or {}
    lines.extend(
        [
            "## After Chase + 18 proj-greedy CPUs (authentic #20 board)",
            "",
            f"- overall: `#{a20.get('overall')}`",
            f"- Daniels still available: **{a20.get('daniels_still_available')}**",
            f"- Fields still available: **{a20.get('fields_still_available')}**",
            f"- Stafford still available: **{a20.get('stafford_still_available')}**",
            "",
            "V2-alpha top-3:",
            "",
        ]
    )
    for r in a20.get("v2_top3") or []:
        lines.append(
            f"- {r.get('name')} ({r.get('position')}) q={r.get('q_player')} "
            f"EV={r.get('ev_two_pick')}"
        )
    if a20.get("diagnostic"):
        _future_table(
            a20["diagnostic"],
            "Diagnostic at #20 (α take-now vs its deferred q)",
        )

    v = report.get("verdict") or {}
    lines.extend(
        [
            "## Verdict (primary R1)",
            "",
            f"- proj kills Daniels: **{v.get('proj_q_dies')}**",
            f"- under that death, Daniels-now beats Chase+replacement QB: "
            f"**{v.get('under_proj_death_take_deferred_beats_take_plus_qb')}**",
            f"- {v.get('reading')}",
            "",
            "### Architecture implication",
            "",
            "- **Outcome A** → build β2 around survival-aware EV "
            "(with a principled survival model — not 2/3 policy votes).",
            "- **Outcome B** → survival alone is not enough; need a richer "
            "distribution over future roster states before coding β2.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chase/Daniels survival causal diagnostic (slot-1 #1)"
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/case_study_survival_chase_daniels.md",
    )
    args = parser.parse_args()
    report = run_diagnostic(seed=args.seed, preset=args.preset)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    v = report.get("verdict") or {}
    print(v.get("reading"))


if __name__ == "__main__":
    main()
