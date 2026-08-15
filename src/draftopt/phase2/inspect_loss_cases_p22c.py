"""P2.2C left-tail loss-case inspection (worst C−B pairs).

Replays adp_feasible (B) and adp_structural (C) for the worst valuation_gain
pairs, logging decision-time alternatives, roster need, ADP, ADP-curve value,
and eventual actual PPR.

Goal: characterize *why* C lost — not inflate mean. Not V3.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import pick_rng
from draftopt.config import EVAL_DB_PATH, get_roster_preset
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    is_user_turn,
    record_user_pick,
    round_for_pick,
    snapshot,
)
from draftopt.phase2 import connect_eval
from draftopt.phase2.delta_p22c import _load_outcomes
from draftopt.phase2.materialize_p22c import P22C_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    N_ROUNDS,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.strategies import get_strategy
from draftopt.strategies.adp_feasible import (
    _counts_from_rows,
    min_starter_picks_needed,
)

DEFAULT_MECH = Path("results/phase2_p22c_valuation_cb_mechanism.json")
STRAT_B = "adp_feasible"
STRAT_C = "adp_structural"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _actual(outcomes: dict, player_id: str) -> float | None:
    pts = outcomes["points"]
    if player_id not in pts:
        return None
    return float(pts[player_id])


def _roster_need(conn, draft_id: str, user_slot: int, slots: dict) -> dict:
    rows = conn.execute(
        """
        SELECT p.position FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        """,
        (draft_id, user_slot),
    ).fetchall()
    counts = _counts_from_rows([dict(r) for r in rows])
    drafted = len(rows)
    remaining_incl = max(0, N_ROUNDS - drafted)
    need = min_starter_picks_needed(counts, slots)
    return {
        "counts": counts,
        "user_picks_done": drafted,
        "user_picks_remaining_incl_this": remaining_incl,
        "min_starter_picks_needed": need,
        "starter_slack": remaining_incl - need,
    }


def _cand_view(rec: dict, outcomes: dict) -> dict:
    pid = rec["player_id"]
    return {
        "player_id": pid,
        "name": rec.get("name"),
        "position": (rec.get("position") or "?").upper(),
        "adp": rec.get("adp_espn"),
        "curve_value": rec.get("proj_espn")
        if rec.get("proj_espn") is not None
        else rec.get("season_points"),
        "marginal": rec.get("marginal"),
        "why": rec.get("why"),
        "actual_ppr": _actual(outcomes, pid),
    }


def _run_traced(
    conn,
    *,
    strategy_name: str,
    user_slot: int,
    seed: int,
    outcomes: dict,
    roster_slots: dict,
    n_alts: int = 8,
) -> dict:
    strategy = get_strategy(strategy_name)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"Loss-{strategy_name}",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    decisions: list[dict] = []
    pick_i = 0
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            overall = int(draft_row["current_pick"])
            rnd = round_for_pick(overall, N_TEAMS)
            need = _roster_need(conn, draft_id, user_slot, roster_slots)
            recs = strategy.recommend(conn, draft_id, n=n_alts)
            if not recs:
                break
            alts = [_cand_view(r, outcomes) for r in recs]
            chosen = alts[0]
            # Best actual among shown alternatives (hindsight)
            with_actual = [a for a in alts if a["actual_ppr"] is not None]
            best_hindsight = (
                max(with_actual, key=lambda a: float(a["actual_ppr"]))
                if with_actual
                else None
            )
            decisions.append(
                {
                    "pick_index": pick_i,
                    "round": rnd,
                    "overall": overall,
                    "chosen": chosen,
                    "alternatives": alts,
                    "roster_need": need,
                    "best_hindsight_among_alts": best_hindsight,
                    "hindsight_regret": (
                        round(
                            float(best_hindsight["actual_ppr"])
                            - float(chosen["actual_ppr"] or 0),
                            4,
                        )
                        if best_hindsight and chosen.get("actual_ppr") is not None
                        else None
                    ),
                }
            )
            record_user_pick(conn, draft_id, chosen["player_id"], made_by="strategy")
            pick_i += 1
        else:
            overall = int(draft_row["current_pick"])
            cpu_pick(
                conn,
                draft_id,
                rng=pick_rng(seed, overall),
                policy="noisy_adp",
            )

    return {
        "strategy": strategy_name,
        "draft_id": draft_id,
        "slot": user_slot,
        "seed": seed,
        "decisions": decisions,
    }


def _first_fork(b_dec: list[dict], c_dec: list[dict]) -> dict | None:
    for b, c in zip(b_dec, c_dec):
        if b["chosen"]["player_id"] != c["chosen"]["player_id"]:
            return {
                "pick_index": b["pick_index"],
                "round": b["round"],
                "overall": b["overall"],
                "b_chosen": b["chosen"],
                "c_chosen": c["chosen"],
                "b_need": b["roster_need"],
                "c_need": c["roster_need"],
                "b_alternatives": b["alternatives"],
                "c_alternatives": c["alternatives"],
                "b_hindsight_regret": b.get("hindsight_regret"),
                "c_hindsight_regret": c.get("hindsight_regret"),
                "actual_delta_c_minus_b": (
                    round(
                        float(c["chosen"]["actual_ppr"] or 0)
                        - float(b["chosen"]["actual_ppr"] or 0),
                        4,
                    )
                    if c["chosen"].get("actual_ppr") is not None
                    and b["chosen"].get("actual_ppr") is not None
                    else None
                ),
            }
    return None


def _classify_fork(fork: dict) -> list[str]:
    """Heuristic tags — hypotheses to inspect, not conclusions."""
    tags: list[str] = []
    bp = fork["b_chosen"]["position"]
    cp = fork["c_chosen"]["position"]
    rnd = int(fork["round"])
    if cp == "DST" and rnd <= 10:
        tags.append("structural_early_mid_dst")
    if cp == "TE" and rnd <= 10:
        tags.append("structural_mid_te")
    if cp in {"WR", "TE"} and bp in {"RB", "QB"}:
        tags.append("structural_skill_over_rb_qb")
    if bp in {"RB", "TE"} and cp == "DST":
        tags.append("structural_dst_over_rb_te")
    if rnd >= 11:
        tags.append("late_round_fork")
    elif rnd >= 6:
        tags.append("mid_round_fork")
    else:
        tags.append("early_round_fork")
    ad = fork.get("actual_delta_c_minus_b")
    if ad is not None and ad < -50:
        tags.append("fork_pick_itself_large_actual_loss")
    return tags


def _post_fork_misses(c_dec: list[dict], b_dec: list[dict], fork_idx: int) -> list[dict]:
    """After fork: C picks where hindsight regret is large vs shown alts."""
    out = []
    for c in c_dec:
        if c["pick_index"] <= fork_idx:
            continue
        regret = c.get("hindsight_regret")
        if regret is None or regret < 80:
            continue
        b_same = next(
            (x for x in b_dec if x["pick_index"] == c["pick_index"]), None
        )
        out.append(
            {
                "round": c["round"],
                "c_chosen": c["chosen"],
                "best_alt": c.get("best_hindsight_among_alts"),
                "hindsight_regret": regret,
                "b_parallel_pick": b_same["chosen"] if b_same else None,
                "roster_need": c["roster_need"],
            }
        )
    return out


def inspect_cases(
    *,
    mechanism_path: Path,
    draft_db: Path | None = None,
    eval_db: Path | None = None,
    n_tail: int = 10,
    n_alts: int = 8,
) -> dict:
    mech = json.loads(mechanism_path.read_text(encoding="utf-8"))
    # Prefer stored left_tail; else sort pairs
    if mech.get("left_tail", {}).get("pairs"):
        cases = mech["left_tail"]["pairs"][:n_tail]
    else:
        cases = sorted(
            mech["pairs"], key=lambda p: p["valuation_gain_full"]
        )[:n_tail]

    eval_conn = connect_eval(eval_db or EVAL_DB_PATH)
    outcomes = _load_outcomes(
        eval_conn,
        season=OUTCOME_SEASON,
        contract_id=CONTRACT_ID,
        source=OUTCOME_SOURCE,
    )
    eval_conn.close()

    roster_slots = get_roster_preset(ROSTER_PRESET)["slots"]
    draft_path = draft_db or P22C_DB_PATH
    conn = live_db.connect(draft_path)
    live_db.init(conn)

    inspected: list[dict] = []
    tag_counter: Counter[str] = Counter()
    fork_round_counter: Counter[int] = Counter()
    fork_pos_c: Counter[str] = Counter()
    fork_pos_b: Counter[str] = Counter()

    for case in cases:
        slot = int(case["slot"])
        seed = int(case["seed"])
        b_trace = _run_traced(
            conn,
            strategy_name=STRAT_B,
            user_slot=slot,
            seed=seed,
            outcomes=outcomes,
            roster_slots=roster_slots,
            n_alts=n_alts,
        )
        c_trace = _run_traced(
            conn,
            strategy_name=STRAT_C,
            user_slot=slot,
            seed=seed,
            outcomes=outcomes,
            roster_slots=roster_slots,
            n_alts=n_alts,
        )
        fork = _first_fork(b_trace["decisions"], c_trace["decisions"])
        tags = _classify_fork(fork) if fork else ["no_fork_identical_boards"]
        for t in tags:
            tag_counter[t] += 1
        if fork:
            fork_round_counter[int(fork["round"])] += 1
            fork_pos_c[fork["c_chosen"]["position"]] += 1
            fork_pos_b[fork["b_chosen"]["position"]] += 1

        post = (
            _post_fork_misses(
                c_trace["decisions"], b_trace["decisions"], fork["pick_index"]
            )
            if fork
            else []
        )

        # Side-by-side pick table (chosen only)
        aligned = []
        for b, c in zip(b_trace["decisions"], c_trace["decisions"]):
            aligned.append(
                {
                    "pick_index": b["pick_index"],
                    "round": b["round"],
                    "same": b["chosen"]["player_id"] == c["chosen"]["player_id"],
                    "b": b["chosen"],
                    "c": c["chosen"],
                    "actual_delta": (
                        round(
                            float(c["chosen"]["actual_ppr"] or 0)
                            - float(b["chosen"]["actual_ppr"] or 0),
                            4,
                        )
                        if b["chosen"].get("actual_ppr") is not None
                        and c["chosen"].get("actual_ppr") is not None
                        else None
                    ),
                }
            )

        inspected.append(
            {
                "slot": slot,
                "seed": seed,
                "valuation_gain_full": case.get("valuation_gain_full"),
                "valuation_gain_ex_dst": case.get("valuation_gain_ex_dst"),
                "pos_delta": case.get("pos_delta"),
                "band_delta": case.get("band_delta"),
                "fork": fork,
                "fork_tags": tags,
                "post_fork_large_regrets": post,
                "aligned_picks": aligned,
                "b_decisions": b_trace["decisions"],
                "c_decisions": c_trace["decisions"],
            }
        )

    conn.close()

    return {
        "stage": "P2.2C_loss_case_inspection",
        "created_at": _utcnow(),
        "snapshot_id": DECISION_SNAPSHOT_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "claim": (
            "Decision-point inspection of worst C−B pairs: what C chose vs "
            "alternatives available, roster need, ADP-curve value, and actual "
            "PPR. Hypotheses only — not V3."
        ),
        "note": (
            "Structural uses raw marginal on ADP-curve (no explicit replacement). "
            "First fork is on a shared board; later picks diverge. "
            "UI stays marginal."
        ),
        "contract": contract_meta(),
        "source_mechanism": str(mechanism_path),
        "n_cases": len(inspected),
        "n_alts": n_alts,
        "aggregate": {
            "fork_tags": dict(tag_counter),
            "fork_rounds": dict(sorted(fork_round_counter.items())),
            "fork_c_positions": dict(fork_pos_c),
            "fork_b_positions": dict(fork_pos_b),
            "n_with_post_fork_large_regret": sum(
                1 for x in inspected if x["post_fork_large_regrets"]
            ),
            "n_fork_pick_c_wins_actual": sum(
                1
                for x in inspected
                if x.get("fork")
                and x["fork"].get("actual_delta_c_minus_b") is not None
                and x["fork"]["actual_delta_c_minus_b"] > 0
            ),
            "n_fork_pick_c_loses_actual": sum(
                1
                for x in inspected
                if x.get("fork")
                and x["fork"].get("actual_delta_c_minus_b") is not None
                and x["fork"]["actual_delta_c_minus_b"] < 0
            ),
        },
        "cases": inspected,
    }


def _fmt_player(p: dict | None) -> str:
    if not p:
        return "—"
    adp = p.get("adp")
    adp_s = f"ADP {adp:.1f}" if adp is not None else "ADP —"
    cv = p.get("curve_value")
    cv_s = f"curve {cv:.0f}" if cv is not None else "curve —"
    marg = p.get("marginal")
    marg_s = f"marg {marg:+.1f}" if marg is not None else ""
    act = p.get("actual_ppr")
    act_s = f"actual {act:+.1f}" if act is not None else "actual —"
    bits = [f"{p.get('name')} ({p.get('position')})", adp_s, cv_s]
    if marg_s:
        bits.append(marg_s)
    bits.append(act_s)
    return " · ".join(bits)


def _md(report: dict) -> str:
    agg = report["aggregate"]
    lines = [
        "# P2.2C left-tail loss-case inspection",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- cases: {report['n_cases']} (worst C−B)",
        f"- source: `{report['source_mechanism']}`",
        "",
        report["claim"],
        "",
        f"**{report['note']}**",
        "",
        "## Aggregate fork fingerprints",
        "",
        f"- fork tags: `{agg['fork_tags']}`",
        f"- fork rounds: `{agg['fork_rounds']}`",
        f"- C position at fork: `{agg['fork_c_positions']}`",
        f"- B position at fork: `{agg['fork_b_positions']}`",
        f"- fork pick itself (C vs B actual): "
        f"C wins {agg.get('n_fork_pick_c_wins_actual', 0)}, "
        f"C loses {agg.get('n_fork_pick_c_loses_actual', 0)}",
        f"- cases with post-fork hindsight regret ≥80 among shown alts: "
        f"{agg['n_with_post_fork_large_regret']}/{report['n_cases']}",
        "",
        "### Read (provisional)",
        "",
        "- First forks cluster in **R5–R8**, not late DST.",
        "- At the fork, C often takes **TE/WR/RB** while B takes **QB/RB** "
        "(skill-over-QB and mid-TE tags).",
        "- The fork pick itself usually **loses** on actual PPR in this worst-10 "
        "(C wins only rarely); large **post-fork** regrets also appear in 10/10.",
        "- Early/mid DST-at-fork was **not** the dominant first-split pattern "
        "in this worst-10 set (DST timing shows up later on some boards).",
        "",
        "### Working hypotheses (to confirm/reject from cases below)",
        "",
        "1. **Replacement / scarcity timing** — C fills TE (or similar) via "
        "marginal when ADP still prefers QB/RB.",
        "2. **Projection uncertainty** — ADP-curve/marginal ranked the fork "
        "pick above players who crushed in 2024 (esp. QB).",
        "3. **Roster-sequence** — mid-draft fork reshapes the later board "
        "(always accompanied by post-fork regrets here).",
        "4. **Irreducible late RB/TE variance** — not an optimizer bug.",
        "",
        "Do **not** jump to V2 survival from narrative alone.",
        "",
    ]

    for case in report["cases"]:
        lines.extend(
            [
                f"## Slot {case['slot']} seed {case['seed']} — "
                f"C−B {case['valuation_gain_full']:+.2f}",
                "",
                f"Tags: `{', '.join(case['fork_tags'])}`",
                "",
            ]
        )
        if case.get("pos_delta"):
            pd = case["pos_delta"]
            lines.append(
                "Pos Δ: "
                + ", ".join(f"{k} {v:+.1f}" for k, v in pd.items())
            )
            lines.append("")

        fork = case.get("fork")
        if not fork:
            lines.append("No fork — identical user boards.")
            lines.append("")
            continue

        lines.extend(
            [
                f"### First fork — R{fork['round']} (overall ~{fork['overall']})",
                "",
                f"- **B chose:** {_fmt_player(fork['b_chosen'])}",
                f"- **C chose:** {_fmt_player(fork['c_chosen'])}",
                f"- Actual Δ at fork (C−B pick): "
                f"{fork.get('actual_delta_c_minus_b')}",
                f"- C roster need: counts={fork['c_need']['counts']}, "
                f"slack={fork['c_need']['starter_slack']}, "
                f"min_need={fork['c_need']['min_starter_picks_needed']}",
                f"- B roster need: counts={fork['b_need']['counts']}, "
                f"slack={fork['b_need']['starter_slack']}",
                "",
                "C alternatives at fork (decision order):",
                "",
            ]
        )
        for i, a in enumerate(fork["c_alternatives"], start=1):
            mark = " ← chosen" if i == 1 else ""
            lines.append(f"{i}. {_fmt_player(a)}{mark}")
        lines.extend(["", "B alternatives at fork (ADP-feasible order):", ""])
        for i, a in enumerate(fork["b_alternatives"], start=1):
            mark = " ← chosen" if i == 1 else ""
            lines.append(f"{i}. {_fmt_player(a)}{mark}")
        lines.append("")

        if case["post_fork_large_regrets"]:
            lines.append("### Post-fork large hindsight regrets (C board, ≥80 PPR)")
            lines.append("")
            for miss in case["post_fork_large_regrets"]:
                lines.append(
                    f"- R{miss['round']}: took {_fmt_player(miss['c_chosen'])}; "
                    f"best shown alt {_fmt_player(miss['best_alt'])}; "
                    f"regret {miss['hindsight_regret']:+.1f}"
                )
                if miss.get("b_parallel_pick"):
                    lines.append(
                        f"  - B parallel pick: {_fmt_player(miss['b_parallel_pick'])}"
                    )
            lines.append("")

        lines.append("### Aligned pick log (divergences marked)")
        lines.append("")
        lines.append("| R | Same? | B | C | Δ actual |")
        lines.append("| --- | --- | --- | --- | ---: |")
        for row in case["aligned_picks"]:
            same = "Y" if row["same"] else "**N**"
            b = row["b"]
            c = row["c"]
            d = row["actual_delta"]
            ds = f"{d:+.1f}" if d is not None else "—"
            lines.append(
                f"| {row['round']} | {same} | {b['name']} ({b['position']}) "
                f"{b.get('actual_ppr')} | {c['name']} ({c['position']}) "
                f"{c.get('actual_ppr')} | {ds} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Status",
            "",
            "- Loss-case inspection: 🟢 artifact written",
            "- V3: 🔴 still blocked — interpret failure mechanism before design",
            "- UI: `marginal`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C loss-case inspection")
    parser.add_argument("--mechanism", type=Path, default=DEFAULT_MECH)
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--n-tail", type=int, default=10)
    parser.add_argument("--n-alts", type=int, default=8)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_loss_case_inspection.md"),
    )
    args = parser.parse_args()
    report = inspect_cases(
        mechanism_path=args.mechanism,
        draft_db=args.draft_db,
        eval_db=args.eval_db,
        n_tail=args.n_tail,
        n_alts=args.n_alts,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    # Slim JSON for git: drop full per-decision alternative dumps in a lite view?
    # Keep full — it's the point of the artifact; ~modest size for 10 cases.
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
