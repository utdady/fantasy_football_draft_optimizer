"""R1 fork opportunity-cost audit (diagnostic only).

Targeted replay of adp_v3a on frozen ladder (slot, seed) pairs until the first
user pick. Captures decision-time marginals, alternatives, roster state, and
joins eventual starter actuals from the ladder.

No map retune. No new strategy. No V3-B implementation.
Classifies A/B/C/D construction-failure hypotheses for the V3-B contract gate.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
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
from draftopt.phase2.diagnose_delta_p22c import _dist_summary
from draftopt.phase2.inspect_loss_cases_p22c import _roster_need
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    N_ROUNDS,
    N_TEAMS,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.v3a_calibration import CURVE_ID
from draftopt.strategies import get_strategy

DEFAULT_LADDER = Path("results/phase2_v3a_ladder.json")
DEFAULT_MECH = Path("results/phase2_v3a_mechanism_audit.json")
STRAT_D = "adp_v3a"
STRAT_C = "adp_structural"
POS_SKILL = ("QB", "RB", "WR", "TE")


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _actual(outcomes: dict, player_id: str) -> float | None:
    pts = outcomes["points"]
    if player_id not in pts:
        return None
    return float(pts[player_id])


def _cand_view(rec: dict, outcomes: dict) -> dict:
    pid = rec["player_id"]
    val = rec.get("proj_espn")
    if val is None:
        val = rec.get("season_points")
    return {
        "player_id": pid,
        "name": rec.get("name"),
        "position": (rec.get("position") or "?").upper(),
        "adp": rec.get("adp_espn"),
        "calibrated_value": None if val is None else float(val),
        "marginal": rec.get("marginal"),
        "lineup_before": rec.get("lineup_before"),
        "lineup_after": rec.get("lineup_after"),
        "why": rec.get("why"),
        "actual_ppr": _actual(outcomes, pid),
    }


def _best_by_pos(scored: list[dict], pos: str, *, skip_ids: set[str] | None = None) -> dict | None:
    skip = skip_ids or set()
    cand = [
        s
        for s in scored
        if (s.get("position") or "").upper() == pos and s["player_id"] not in skip
    ]
    if not cand:
        return None
    return max(cand, key=lambda r: float(r.get("marginal") or -1e18))


def _replacement_by_pos(scored: list[dict]) -> dict[str, dict | None]:
    """
    Crude replacement: 2nd-best marginal at each position among remaining pool
    (decision-time calibrated values via marginal ranking).
    """
    out: dict[str, dict | None] = {}
    for pos in POS_SKILL + ("DST",):
        same = [
            s
            for s in scored
            if (s.get("position") or "").upper() == pos and s.get("marginal") is not None
        ]
        same.sort(key=lambda r: -float(r["marginal"]))
        if len(same) >= 2:
            r = same[1]
            out[pos] = {
                "player_id": r["player_id"],
                "name": r.get("name"),
                "calibrated_value": float(r.get("proj_espn") or r.get("season_points") or 0),
                "marginal": float(r["marginal"]),
                "rank_at_pos": 2,
            }
        elif len(same) == 1:
            out[pos] = {
                "player_id": None,
                "name": None,
                "calibrated_value": 0.0,
                "marginal": 0.0,
                "rank_at_pos": None,
                "note": "only one remaining — replacement treated as 0",
            }
        else:
            out[pos] = None
    return out


def _replay_to_first_user_pick(
    conn,
    *,
    user_slot: int,
    seed: int,
    outcomes: dict,
    roster_slots: dict,
    n_alts: int = 80,
) -> dict:
    """CPU to first user turn; return full scored pool + chosen (adp_v3a)."""
    strategy = get_strategy(STRAT_D)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"R1OC-{STRAT_D}",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            raise RuntimeError("draft completed before user pick")
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            overall = int(draft_row["current_pick"])
            rnd = round_for_pick(overall, N_TEAMS)
            need = _roster_need(conn, draft_id, user_slot, roster_slots)
            # Large window so C's R1 pick is usually visible for marginal compare
            scored_all = strategy.recommend(conn, draft_id, n=n_alts)
            if not scored_all:
                raise RuntimeError("empty recommendations at R1")
            # Also get a larger view if n_alts truncates — recommend already sorts
            alts = [_cand_view(r, outcomes) for r in scored_all]
            chosen = alts[0]
            repl = _replacement_by_pos(scored_all)
            best_pos = {}
            for pos in POS_SKILL:
                b = _best_by_pos(scored_all, pos)
                best_pos[pos] = _cand_view(b, outcomes) if b else None

            return {
                "draft_id": draft_id,
                "slot": user_slot,
                "seed": seed,
                "round": rnd,
                "overall": overall,
                "roster_need": need,
                "lineup_before": chosen.get("lineup_before"),
                "chosen": chosen,
                "top_alts": alts[:12],
                "best_by_pos": best_pos,
                "replacement_by_pos": {
                    pos: (
                        {
                            **repl[pos],
                            "actual_ppr": _actual(outcomes, repl[pos]["player_id"])
                            if repl[pos] and repl[pos].get("player_id")
                            else None,
                        }
                        if repl.get(pos)
                        else None
                    )
                    for pos in list(POS_SKILL) + ["DST"]
                },
                "scored_n": len(scored_all),
            }
        overall = int(draft_row["current_pick"])
        cpu_pick(conn, draft_id, rng=pick_rng(seed, overall), policy="noisy_adp")


def _starter_actual_by_pos(picks: list[dict], slots: dict) -> dict[str, float]:
    from draftopt.lineup import lineup_ev

    roster = [
        {
            "player_id": p["player_id"],
            "name": p["name"],
            "position": p["position"],
            "season_points": float(p["actual_ppr"]),
        }
        for p in picks
    ]
    lined = lineup_ev(roster, slots)
    by_pos: dict[str, float] = defaultdict(float)
    for slot_players in lined.starters.values():
        for p in slot_players:
            by_pos[(p["position"] or "?").upper()] += float(p["season_points"])
    by_pos["_total"] = float(lined.total)
    return dict(by_pos)


def _classify_row(row: dict) -> list[str]:
    """Hypothesis tags — evidence labels, not permission to edit the map."""
    tags: list[str] = []
    d = row["d_decision"]
    before = d.get("lineup_before")
    marg = d["chosen"].get("marginal")
    val = d["chosen"].get("calibrated_value")
    why = (d["chosen"].get("why") or "").lower()

    # A: zero-replacement / empty-slot fill
    if before is not None and float(before) <= 0.01:
        tags.append("A_zero_replacement")
    if why.startswith("+") and "fills" in why:
        tags.append("A_fills_empty_slot_why")
    if (
        marg is not None
        and val is not None
        and abs(float(marg) - float(val)) <= 1.0
        and before is not None
        and float(before) <= 0.01
    ):
        tags.append("A_marginal_equals_full_value")

    # B: scarcity / replacement gap
    pos = d["chosen"]["position"]
    repl = (d.get("replacement_by_pos") or {}).get(pos)
    if repl and marg is not None and val is not None:
        gap = float(val) - float(repl.get("calibrated_value") or 0)
        # Model does not subtract replacement; if gap << value, scarcity exists
        # but model still awards ~full value → poorly estimated opportunity vs pool
        if gap < 0.5 * float(val) and float(before or 0) <= 0.01:
            tags.append("B_replacement_gap_large_but_unused")
        row["model_vs_vorp_like"] = {
            "value": val,
            "replacement": repl.get("calibrated_value"),
            "value_minus_replacement": round(gap, 4),
            "marginal": marg,
            "marginal_minus_vorp_like": round(float(marg) - gap, 4),
        }

    # C: multi-round opportunity cost (realized)
    oc = row.get("actual_opportunity_cost")
    if oc is not None:
        if oc["d_minus_c_starter_total"] is not None and oc["d_minus_c_starter_total"] < -50:
            tags.append("C_large_negative_roster_delta")
        if oc.get("rb_starter_delta") is not None and oc["rb_starter_delta"] < -80:
            tags.append("C_rb_portfolio_hole")
        if (
            oc.get("fork_pick_actual_delta_d_minus_c") is not None
            and oc["fork_pick_actual_delta_d_minus_c"] > 0
            and oc.get("d_minus_c_starter_total") is not None
            and oc["d_minus_c_starter_total"] < 0
        ):
            tags.append("C_won_pick_lost_roster")

    if len([t for t in tags if t.startswith("A_")]) >= 1 and len(
        [t for t in tags if t.startswith("C_")]
    ) >= 1:
        tags.append("D_combination_A_and_C")

    return tags


def run_audit(
    *,
    ladder_path: Path = DEFAULT_LADDER,
    draft_db: Path = P22C_V3A_DB_PATH,
    eval_db: Path | None = None,
    n_alts: int = 40,
) -> dict:
    ladder = json.loads(ladder_path.read_text(encoding="utf-8"))
    pairs = ladder["pairs"]
    roster_slots = get_roster_preset(ROSTER_PRESET)["slots"]

    eval_conn = connect_eval(eval_db or EVAL_DB_PATH)
    outcomes = _load_outcomes(
        eval_conn,
        season=OUTCOME_SEASON,
        contract_id=CONTRACT_ID,
        source=OUTCOME_SOURCE,
    )
    eval_conn.close()

    conn = live_db.connect(draft_db)
    live_db.init(conn)

    rows: list[dict] = []
    for pair in pairs:
        slot = int(pair["slot"])
        seed = int(pair["seed"])
        c_picks = pair["picks"][STRAT_C]
        d_picks = pair["picks"][STRAT_D]
        c_first = c_picks[0]
        d_first = d_picks[0]
        dc = float(pair["metrics"]["full"]["calibration_vs_structural_d_minus_c"])

        decision = _replay_to_first_user_pick(
            conn,
            user_slot=slot,
            seed=seed,
            outcomes=outcomes,
            roster_slots=roster_slots,
            n_alts=n_alts,
        )

        # C alternative on same board = find C's first pick in D's scored alts / pool
        c_pid = c_first["player_id"]
        c_on_board = next(
            (a for a in decision["top_alts"] if a["player_id"] == c_pid), None
        )
        if c_on_board is None:
            # search best_by_pos
            for pos_alt in decision["best_by_pos"].values():
                if pos_alt and pos_alt["player_id"] == c_pid:
                    c_on_board = pos_alt
                    break

        # If still missing, score via a fresh recommend already truncated —
        # re-fetch with larger n
        if c_on_board is None:
            c_on_board = {
                "player_id": c_pid,
                "name": c_first.get("name"),
                "position": c_first.get("position"),
                "calibrated_value": None,
                "marginal": None,
                "actual_ppr": float(c_first["actual_ppr"])
                if c_first.get("actual_ppr") is not None
                else None,
                "note": "not in top_alts window",
            }

        d_starters = _starter_actual_by_pos(d_picks, roster_slots)
        c_starters = _starter_actual_by_pos(c_picks, roster_slots)

        fork_act_d = (
            float(d_first["actual_ppr"]) if d_first.get("actual_ppr") is not None else None
        )
        fork_act_c = (
            float(c_first["actual_ppr"]) if c_first.get("actual_ppr") is not None else None
        )

        oc = {
            "fork_pick_actual_delta_d_minus_c": (
                round(fork_act_d - fork_act_c, 4)
                if fork_act_d is not None and fork_act_c is not None
                else None
            ),
            "d_minus_c_starter_total": round(
                d_starters.get("_total", 0) - c_starters.get("_total", 0), 4
            ),
            "rb_starter_delta": round(
                d_starters.get("RB", 0) - c_starters.get("RB", 0), 4
            ),
            "qb_starter_delta": round(
                d_starters.get("QB", 0) - c_starters.get("QB", 0), 4
            ),
            "wr_starter_delta": round(
                d_starters.get("WR", 0) - c_starters.get("WR", 0), 4
            ),
            "te_starter_delta": round(
                d_starters.get("TE", 0) - c_starters.get("TE", 0), 4
            ),
            "d_starter_by_pos": {k: round(v, 4) for k, v in d_starters.items()},
            "c_starter_by_pos": {k: round(v, 4) for k, v in c_starters.items()},
        }

        # Model opportunity cost at decision: D marginal − C-alt marginal
        d_marg = decision["chosen"].get("marginal")
        c_marg = c_on_board.get("marginal") if c_on_board else None
        model_oc = (
            round(float(d_marg) - float(c_marg), 4)
            if d_marg is not None and c_marg is not None
            else None
        )

        row = {
            "slot": slot,
            "seed": seed,
            "d_minus_c_full": dc,
            "ladder_d_first": {
                "player_id": d_first["player_id"],
                "name": d_first["name"],
                "position": d_first["position"],
                "actual_ppr": fork_act_d,
            },
            "ladder_c_first": {
                "player_id": c_first["player_id"],
                "name": c_first["name"],
                "position": c_first["position"],
                "actual_ppr": fork_act_c,
            },
            "d_decision": decision,
            "c_alternative_on_d_board": c_on_board,
            "model_marginal_adv_d_minus_c_alt": model_oc,
            "actual_opportunity_cost": oc,
            "pick_match_ladder": decision["chosen"]["player_id"] == d_first["player_id"],
        }
        row["mechanism_tags"] = _classify_row(row)
        rows.append(row)

        # Clean up draft rows lightly — leave DB; drafts accumulate. OK for audit.

    conn.close()

    tag_counts = Counter(t for r in rows for t in r["mechanism_tags"])
    n = len(rows)
    n_match = sum(1 for r in rows if r["pick_match_ladder"])

    before_vals = [
        float(r["d_decision"]["lineup_before"])
        for r in rows
        if r["d_decision"].get("lineup_before") is not None
    ]
    marg_vs_val = []
    for r in rows:
        ch = r["d_decision"]["chosen"]
        if ch.get("marginal") is not None and ch.get("calibrated_value") is not None:
            marg_vs_val.append(float(ch["marginal"]) - float(ch["calibrated_value"]))

    model_adv = [
        r["model_marginal_adv_d_minus_c_alt"]
        for r in rows
        if r["model_marginal_adv_d_minus_c_alt"] is not None
    ]
    fork_act = [
        r["actual_opportunity_cost"]["fork_pick_actual_delta_d_minus_c"]
        for r in rows
        if r["actual_opportunity_cost"]["fork_pick_actual_delta_d_minus_c"] is not None
    ]
    roster_dc = [
        r["actual_opportunity_cost"]["d_minus_c_starter_total"] for r in rows
    ]
    rb_dc = [r["actual_opportunity_cost"]["rb_starter_delta"] for r in rows]

    n_a = sum(1 for r in rows if any(t.startswith("A_") for t in r["mechanism_tags"]))
    n_c = sum(1 for r in rows if any(t.startswith("C_") for t in r["mechanism_tags"]))
    n_combo = sum(1 for r in rows if "D_combination_A_and_C" in r["mechanism_tags"])
    n_b = sum(1 for r in rows if any(t.startswith("B_") for t in r["mechanism_tags"]))

    if n_combo >= 0.5 * n and n_a >= 0.9 * n:
        primary = "D_combination"
        primary_text = (
            "Combination: R1 empty-slot / zero-replacement drives the pick "
            "(marginal ≈ full calibrated value); multi-round opportunity cost "
            "drives roster translation failure (won fork pick, RB/portfolio hole)."
        )
    elif n_a >= 0.9 * n and n_c < 0.3 * n:
        primary = "A_zero_replacement"
        primary_text = (
            "Primarily zero-replacement artifact at R1 (empty roster → full value)."
        )
    elif n_c >= 0.5 * n and n_a < 0.5 * n:
        primary = "C_multi_round_opportunity_cost"
        primary_text = "Primarily multi-round opportunity cost without clear R1 zero-replacement."
    else:
        primary = "mixed"
        primary_text = "Mixed tags — inspect per-row table before V3-B contract."

    return {
        "stage": "V3A_R1_FORK_OPPORTUNITY_COST_AUDIT",
        "created_at": _utcnow(),
        "curve_id": CURVE_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "source_ladder": str(ladder_path),
        "draft_db": str(draft_db),
        "claim": (
            "Decision-time opportunity-cost audit at the R1 C/D fork on frozen "
            "V3-A boards. Targeted replay of adp_v3a only; map unchanged. "
            "Findings classify construction failure — not permission to retune "
            "calibration or resurrect V2."
        ),
        "methodological_rule": (
            "D and future E share frozen V3-A values; only construction may change. "
            "E−D is the causal V3-B test. Implementation of E remains blocked until "
            "this audit informs the V3-B contract."
        ),
        "contract": contract_meta(),
        "n_pairs": n,
        "n_pick_match_ladder": n_match,
        "primary_classification": primary,
        "primary_classification_text": primary_text,
        "tag_counts": dict(tag_counts),
        "coverage": {
            "n_with_A_tags": n_a,
            "n_with_B_tags": n_b,
            "n_with_C_tags": n_c,
            "n_combination_A_and_C": n_combo,
        },
        "decision_time_summary": {
            "lineup_before": _dist_summary(before_vals),
            "marginal_minus_calibrated_value": _dist_summary(marg_vs_val),
            "model_marginal_adv_d_minus_c_alt": _dist_summary(model_adv),
            "note": (
                "lineup_before≈0 and marginal≈value ⇒ empty-slot / zero-replacement. "
                "model_marginal_adv = D.marginal − C_alt.marginal on D's board."
            ),
        },
        "realized_summary": {
            "fork_pick_actual_d_minus_c": _dist_summary(fork_act),
            "starter_total_d_minus_c": _dist_summary(roster_dc),
            "rb_starter_d_minus_c": _dist_summary(rb_dc),
            "n_won_pick_lost_roster": sum(
                1
                for r in rows
                if "C_won_pick_lost_roster" in r["mechanism_tags"]
            ),
        },
        "rows": rows,
        "v3b_gate": {
            "design_justified": True,
            "implementation_blocked": True,
            "next": (
                "Freeze V3-B contract: one construction change; identical V3-A "
                "values; evaluate E−D. Do not retune map; no λ/CVaR/V2."
            ),
        },
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    dt = report["decision_time_summary"]
    rz = report["realized_summary"]
    lines = [
        "# V3-A R1 fork opportunity-cost audit",
        "",
        f"- stage: `{report['stage']}`",
        f"- curve: `{report['curve_id']}` (frozen)",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']} "
        f"(ladder pick match: {report['n_pick_match_ladder']}/{report['n_pairs']})",
        f"- source: `{report['source_ladder']}`",
        "",
        report["claim"],
        "",
        f"**{report['methodological_rule']}**",
        "",
        "## Primary classification",
        "",
        f"**`{report['primary_classification']}`** — {report['primary_classification_text']}",
        "",
        f"Tag coverage: `{report['coverage']}`",
        "",
        f"Tag counts: `{report['tag_counts']}`",
        "",
        "## Decision-time (model belief)",
        "",
        dt["note"],
        "",
        f"- lineup_before: mean={_fmt(dt['lineup_before']['mean'], False)}, "
        f"max={_fmt(dt['lineup_before']['max'], False)}",
        f"- marginal − calibrated value: mean={_fmt(dt['marginal_minus_calibrated_value']['mean'])}",
        f"- model marginal adv (D − C_alt): mean={_fmt(dt['model_marginal_adv_d_minus_c_alt']['mean'])}, "
        f"median={_fmt(dt['model_marginal_adv_d_minus_c_alt']['median'])}",
        "",
        "## Realized opportunity cost",
        "",
        f"- fork pick actual D−C: mean={_fmt(rz['fork_pick_actual_d_minus_c']['mean'])}, "
        f"WR(D)={rz['fork_pick_actual_d_minus_c']['win_rate']:.0%}",
        f"- starter total D−C: mean={_fmt(rz['starter_total_d_minus_c']['mean'])}, "
        f"p10={_fmt(rz['starter_total_d_minus_c']['p10'])}",
        f"- RB starter D−C: mean={_fmt(rz['rb_starter_d_minus_c']['mean'])}",
        f"- won pick / lost roster: {rz['n_won_pick_lost_roster']}/{report['n_pairs']}",
        "",
        "## Per-board rows",
        "",
        "| Slot | Seed | D pick | C alt | D marg | C marg | before | "
        "act D | act C | Δfork | Δroster | ΔRB | tags |",
        "| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in report["rows"]:
        d = r["d_decision"]["chosen"]
        c = r["c_alternative_on_d_board"] or {}
        oc = r["actual_opportunity_cost"]
        tags = ",".join(
            t
            for t in (
                "A" if any(x.startswith("A_") for x in r["mechanism_tags"]) else "",
                "B" if any(x.startswith("B_") for x in r["mechanism_tags"]) else "",
                "C" if any(x.startswith("C_") for x in r["mechanism_tags"]) else "",
                "D" if "D_combination_A_and_C" in r["mechanism_tags"] else "",
            )
            if t
        )
        lines.append(
            f"| {r['slot']} | {r['seed']} | {d.get('name')} ({d.get('position')}) | "
            f"{c.get('name')} ({c.get('position')}) | "
            f"{_fmt(d.get('marginal'), False)} | {_fmt(c.get('marginal'), False)} | "
            f"{_fmt(r['d_decision'].get('lineup_before'), False)} | "
            f"{_fmt(d.get('actual_ppr'), False)} | {_fmt(c.get('actual_ppr'), False)} | "
            f"{_fmt(oc.get('fork_pick_actual_delta_d_minus_c'))} | "
            f"{_fmt(oc.get('d_minus_c_starter_total'))} | "
            f"{_fmt(oc.get('rb_starter_delta'))} | {tags or '—'} |"
        )

    lines.extend(
        [
            "",
            "## Mechanism key",
            "",
            "| Code | Meaning |",
            "| --- | --- |",
            "| A | Zero-replacement / empty-slot fill (lineup_before≈0, marg≈value) |",
            "| B | Replacement gap large but unused by model |",
            "| C | Multi-round / portfolio opportunity cost |",
            "| D | Combination of A and C |",
            "",
            "## V3-B gate",
            "",
            f"- design justified: **{report['v3b_gate']['design_justified']}**",
            f"- implementation blocked: **{report['v3b_gate']['implementation_blocked']}**",
            f"- next: {report['v3b_gate']['next']}",
            "",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="R1 fork opportunity-cost audit")
    parser.add_argument("--ladder", type=Path, default=DEFAULT_LADDER)
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--n-alts", type=int, default=80)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_r1_opportunity_cost_audit.md"),
    )
    args = parser.parse_args()
    report = run_audit(
        ladder_path=args.ladder,
        draft_db=args.draft_db,
        eval_db=args.eval_db,
        n_alts=args.n_alts,
    )
    # Slim JSON: drop huge nested scored pools already truncated in top_alts
    slim = dict(report)
    md = _md(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
