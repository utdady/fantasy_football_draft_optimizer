"""V3-B Branch A structural inertness diagnostic (replay D boards).

At each user pick under adp_v3a: record whether D's argmax is the unique
global M_D max and whether pos(p*) ∈ N(R). Under those conditions,
M_A = M_D(p) − M_D(q*) with q* excluding pos(p) structurally protects p*
against cross-position challengers — so 0/60 policy identity is expected,
not a strong empirical kill of opportunity cost.

Also records same-pos runner-up gap (cannot flip A vs D within-position,
because M_A is an affine shift of M_D inside a position) for clarity.

No strategy change. No outcomes in recommend.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots, pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    draft_roster,
    is_user_turn,
    record_user_pick,
    snapshot,
    _draft_row,
)
from draftopt.phase2.crosspos_empty_need import empty_capacity_positions
from draftopt.phase2.crosspos_empty_need_marginal import crosspos_empty_need_marginal
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import N_ROUNDS, N_TEAMS, ROSTER_PRESET
from draftopt.strategies import get_strategy
from draftopt.strategies.adp_feasible import _counts_from_rows


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _user_counts(conn, draft_id: str, user_slot: int) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT p.position FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        """,
        (draft_id, user_slot),
    ).fetchall()
    return _counts_from_rows([dict(r) for r in rows])


def _inspect_decision(conn, draft_id: str, *, user_slot: int) -> dict:
    draft = _draft_row(conn, draft_id)
    slots = draft_roster(draft).get("slots") or {}
    counts = _user_counts(conn, draft_id, user_slot)
    n_r = empty_capacity_positions(counts, slots)

    d_full = get_strategy("adp_v3a").recommend(conn, draft_id, n=10_000)
    a_top = get_strategy("adp_v3ba").recommend(conn, draft_id, n=1)
    if not d_full:
        return {"empty": True}

    # Sort already by M_D desc
    top = d_full[0]
    md_top = float(top["marginal"])
    pos_top = (top.get("position") or "").upper()
    pid_top = str(top["player_id"])

    n_at_top = sum(
        1
        for r in d_full
        if r.get("marginal") is not None and abs(float(r["marginal"]) - md_top) < 1e-9
    )
    unique_global = n_at_top == 1
    pos_in_nr = pos_top in n_r

    same_pos = [
        r
        for r in d_full[1:]
        if (r.get("position") or "").upper() == pos_top and r.get("marginal") is not None
    ]
    same_pos_gap = None
    same_pos_second = None
    if same_pos:
        same_pos_second = {
            "name": same_pos[0].get("name"),
            "player_id": str(same_pos[0]["player_id"]),
            "marginal_d": float(same_pos[0]["marginal"]),
        }
        same_pos_gap = round(md_top - float(same_pos[0]["marginal"]), 4)

    remaining = [
        {
            "player_id": str(item["player_id"]),
            "name": item.get("name"),
            "position": (item.get("position") or "").upper(),
            "marginal_d": (
                float(item["marginal"]) if item.get("marginal") is not None else None
            ),
            "adp_espn": item.get("adp_espn"),
            "ecr_fp_ppr": item.get("ecr_fp_ppr"),
        }
        for item in d_full
    ]
    qinfo = crosspos_empty_need_marginal(
        player_id=pid_top,
        position=pos_top,
        remaining=remaining,
        counts=counts,
        slots=slots,
    )
    incumbent_penalty = float(qinfo["cross_alt_marginal"])
    incumbent_ma = round(md_top - incumbent_penalty, 4)

    a_pid = str(a_top[0]["player_id"]) if a_top else None
    a_matches_d = a_pid == pid_top

    structural_protected = bool(unique_global and pos_in_nr and not qinfo["cross_alt_missing"])

    overall = int(draft["current_pick"])
    rnd = (overall - 1) // N_TEAMS + 1

    return {
        "empty": False,
        "round": rnd,
        "overall": overall,
        "d_top": {
            "name": top.get("name"),
            "player_id": pid_top,
            "position": pos_top,
            "marginal_d": md_top,
        },
        "a_top_player_id": a_pid,
        "a_matches_d": a_matches_d,
        "unique_global_md_max": unique_global,
        "n_tied_at_md_max": n_at_top,
        "pos_in_N_R": pos_in_nr,
        "N_R": sorted(n_r),
        "cross_alt_missing": qinfo["cross_alt_missing"],
        "qstar": {
            "player_id": qinfo["cross_alt_player_id"],
            "name": qinfo["cross_alt_name"],
            "position": qinfo["cross_alt_position"],
            "marginal_d": qinfo["cross_alt_marginal"],
        },
        "incumbent_penalty_md_qstar": incumbent_penalty,
        "incumbent_m_a": incumbent_ma,
        "same_pos_second": same_pos_second,
        "same_pos_gap_md": same_pos_gap,
        "structural_protected": structural_protected,
    }


def run_board(conn, *, slot: int, seed: int) -> dict:
    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="V3BA-struct",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    decisions: list[dict] = []
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            info = _inspect_decision(conn, draft_id, user_slot=slot)
            if info.get("empty"):
                break
            decisions.append(info)
            record_user_pick(
                conn,
                draft_id,
                info["d_top"]["player_id"],
                made_by="strategy",
            )
        else:
            overall = int(draft_row["current_pick"])
            cpu_pick(
                conn,
                draft_id,
                rng=pick_rng(seed, overall),
                policy="noisy_adp",
            )
    n_prot = sum(1 for d in decisions if d["structural_protected"])
    n_match = sum(1 for d in decisions if d["a_matches_d"])
    return {
        "slot": slot,
        "seed": seed,
        "draft_id": draft_id,
        "n_user_decisions": len(decisions),
        "n_a_matches_d": n_match,
        "n_structural_protected": n_prot,
        "decisions": decisions,
    }


def run_diagnostic(
    *,
    draft_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 5,
    seed0: int = 42,
) -> dict:
    path = draft_db or P22C_V3A_DB_PATH
    slots = slots or list(range(1, N_TEAMS + 1))
    conn = live_db.connect(path)
    live_db.init(conn)

    boards: list[dict] = []
    for slot in slots:
        for i in range(n_sims):
            boards.append(run_board(conn, slot=slot, seed=seed0 + i))
    conn.close()

    all_dec = [d for b in boards for d in b["decisions"]]
    n_dec = len(all_dec)
    n_prot = sum(1 for d in all_dec if d["structural_protected"])
    n_unique = sum(1 for d in all_dec if d["unique_global_md_max"])
    n_pos_in = sum(1 for d in all_dec if d["pos_in_N_R"])
    n_match = sum(1 for d in all_dec if d["a_matches_d"])
    n_mismatch = n_dec - n_match
    n_missing = sum(1 for d in all_dec if d["cross_alt_missing"])

    gaps = [d["same_pos_gap_md"] for d in all_dec if d["same_pos_gap_md"] is not None]
    penalties = [
        d["incumbent_penalty_md_qstar"]
        for d in all_dec
        if not d["cross_alt_missing"]
    ]

    # Among structurally protected decisions, did A ever disagree? (should be 0)
    prot_mismatch = sum(
        1 for d in all_dec if d["structural_protected"] and not d["a_matches_d"]
    )
    unprotected = [d for d in all_dec if not d["structural_protected"]]
    unprot_mismatch = sum(1 for d in unprotected if not d["a_matches_d"])
    unprot_missing = sum(1 for d in unprotected if d["cross_alt_missing"])
    unprot_not_unique = sum(
        1
        for d in unprotected
        if (not d["cross_alt_missing"]) and (not d["unique_global_md_max"])
    )
    unprot_pos_out = sum(
        1
        for d in unprotected
        if (not d["cross_alt_missing"])
        and d["unique_global_md_max"]
        and (not d["pos_in_N_R"])
    )

    by_round = Counter()
    prot_by_round = Counter()
    for d in all_dec:
        r = d.get("round") or 0
        by_round[r] += 1
        if d["structural_protected"]:
            prot_by_round[r] += 1

    return {
        "stage": "V3BA_structural_inertness",
        "created_at": _utcnow(),
        "claim": (
            "Branch A q* excludes the candidate's whole position, so the unique "
            "global M_D argmax with pos in N(R) is structurally protected vs "
            "cross-position challengers; within-position M_A is an affine shift of M_D."
        ),
        "note": (
            "Same-pos gap cannot create A≠D (order preserved within position). "
            "0/60 ladder identity is expected when structural_protected holds almost always. "
            "This is not a strong empirical falsification of opportunity cost as a concept."
        ),
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_boards": len(boards),
        "summary": {
            "n_user_decisions": n_dec,
            "n_a_matches_d": n_match,
            "n_a_mismatch_d": n_mismatch,
            "frac_a_matches_d": round(n_match / n_dec, 4) if n_dec else None,
            "n_unique_global_md_max": n_unique,
            "frac_unique_global_md_max": round(n_unique / n_dec, 4) if n_dec else None,
            "n_pos_in_N_R": n_pos_in,
            "frac_pos_in_N_R": round(n_pos_in / n_dec, 4) if n_dec else None,
            "n_structural_protected": n_prot,
            "frac_structural_protected": round(n_prot / n_dec, 4) if n_dec else None,
            "n_cross_alt_missing": n_missing,
            "frac_cross_alt_missing": round(n_missing / n_dec, 4) if n_dec else None,
            "n_protected_but_a_mismatch": prot_mismatch,
            "n_unprotected_decisions": len(unprotected),
            "n_unprotected_a_mismatch": unprot_mismatch,
            "unprotected_breakdown": {
                "cross_alt_missing_fallback_to_md": unprot_missing,
                "not_unique_global_max": unprot_not_unique,
                "unique_but_pos_not_in_N_R": unprot_pos_out,
            },
            "same_pos_gap_md": {
                "n": len(gaps),
                "mean": round(statistics.mean(gaps), 4) if gaps else None,
                "median": round(statistics.median(gaps), 4) if gaps else None,
                "p10": round(sorted(gaps)[max(0, int(0.1 * (len(gaps) - 1)))], 4)
                if gaps
                else None,
                "min": round(min(gaps), 4) if gaps else None,
            },
            "incumbent_penalty_md_qstar": {
                "n": len(penalties),
                "mean": round(statistics.mean(penalties), 4) if penalties else None,
                "median": round(statistics.median(penalties), 4) if penalties else None,
            },
            "structural_protected_by_round": {
                str(r): {
                    "n": by_round[r],
                    "n_protected": prot_by_round[r],
                    "frac": round(prot_by_round[r] / by_round[r], 4)
                    if by_round[r]
                    else None,
                }
                for r in sorted(by_round)
            },
        },
        "boards": [
            {
                "slot": b["slot"],
                "seed": b["seed"],
                "n_user_decisions": b["n_user_decisions"],
                "n_a_matches_d": b["n_a_matches_d"],
                "n_structural_protected": b["n_structural_protected"],
            }
            for b in boards
        ],
        # Keep a small sample of unprotected decisions for inspection
        "unprotected_sample": unprotected[:25],
    }


def _md(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# V3-B Branch A structural inertness diagnostic",
        "",
        f"- created: `{report['created_at']}`",
        f"- boards: {report['n_boards']}",
        f"- user decisions: {s['n_user_decisions']}",
        "",
        report["claim"],
        "",
        f"**{report['note']}**",
        "",
        "## Headline",
        "",
        f"- A top1 == D top1: **{s['n_a_matches_d']}/{s['n_user_decisions']}** "
        f"({s['frac_a_matches_d']:.1%})",
        f"- unique global M_D max: {s['n_unique_global_md_max']}/{s['n_user_decisions']} "
        f"({s['frac_unique_global_md_max']:.1%})",
        f"- pos(p*) in N(R): {s['n_pos_in_N_R']}/{s['n_user_decisions']} "
        f"({s['frac_pos_in_N_R']:.1%})",
        f"- **structural_protected** (unique max AND pos in N(R) AND q* present): "
        f"**{s['n_structural_protected']}/{s['n_user_decisions']}** "
        f"({s['frac_structural_protected']:.1%})",
        f"- protected but A≠D: **{s['n_protected_but_a_mismatch']}** (expect 0)",
        f"- unprotected decisions: {s['n_unprotected_decisions']}; "
        f"among them A≠D: {s['n_unprotected_a_mismatch']}",
        f"- cross_alt_missing (M_A falls back to M_D): "
        f"{s['n_cross_alt_missing']}/{s['n_user_decisions']} "
        f"({s['frac_cross_alt_missing']:.1%})",
        f"- unprotected breakdown: `{s['unprotected_breakdown']}`",
        "",
        "Early rounds are almost entirely **incumbent-protected**. Later rounds "
        "are mostly **missing-alt fallback** (N(R) empty / no cross need) where "
        "M_A = M_D by definition — still not an empirical OC test.",
        "",
        "## Same-position gap (cannot flip A vs D)",
        "",
        f"- n with same-pos runner-up: {s['same_pos_gap_md']['n']}",
        f"- mean / median / p10 / min gap: "
        f"{s['same_pos_gap_md']['mean']} / {s['same_pos_gap_md']['median']} / "
        f"{s['same_pos_gap_md']['p10']} / {s['same_pos_gap_md']['min']}",
        "",
        "Within a position, M_A subtracts the same outside q*, so order "
        "matches M_D. Narrow same-pos gaps do **not** create policy divergence.",
        "",
        "## Protected rate by round",
        "",
        "| Round | n | protected | frac |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for r, row in s["structural_protected_by_round"].items():
        lines.append(
            f"| {r} | {row['n']} | {row['n_protected']} | {row['frac']:.0%} |"
        )
    lines.extend(
        [
            "",
            "## Reading for Branch B",
            "",
            "| Wrong sentence | Better sentence |",
            "| --- | --- |",
            "| OC failed empirically; only lookahead remains | "
            "This single-reference, position-excluded subtraction was "
            "**structurally near-inert** |",
            "| Same-pos near-ties might have saved A | "
            "Same-pos margins cannot produce A≠D under this formula |",
            "",
            "Branch B design (when opened) must **forbid** scores of the form "
            "M_D(p)-c(p) where c is constant across candidates or "
            "systematically smaller for the current M_D-argmax than for "
            "cross-position rivals.",
            "",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Branch A structural inertness")
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1-12")
    parser.add_argument("--n-sims", type=int, default=5)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3ba_structural_inertness.md"),
    )
    args = parser.parse_args()
    report = run_diagnostic(
        draft_db=args.draft_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
    )
    # Drop full decision dumps from JSON boards already summarized; keep sample
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
