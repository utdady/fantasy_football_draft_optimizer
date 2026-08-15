"""V3-B Branch B: one-step continuation after T(R,p).

Frozen by results/V3B_STATE_DEPENDENT_DESIGN.md
(construction_id onestep_continuation_marginal_v1).

M_B(p) = M_D(p|R) + C(R∪{p}), where C(R') = max_q M_D(q|R').
Pure lineup math — no outcomes, no multi-round, no opponent sim.
"""

from __future__ import annotations

from typing import Any

from draftopt.lineup import lineup_ev

CONSTRUCTION_ID = "onestep_continuation_marginal_v1"


def _pts(player: dict) -> float:
    val = player.get("season_points")
    if val is None:
        val = player.get("proj_espn")
    return float(val or 0.0)


def _lineup_row(player: dict) -> dict:
    return {
        "player_id": str(player.get("player_id")),
        "name": player.get("name"),
        "position": (player.get("position") or "").upper(),
        "team": player.get("team"),
        "season_points": _pts(player),
        "adp_espn": player.get("adp_espn"),
        "ecr_fp_ppr": player.get("ecr_fp_ppr"),
    }


def transition_roster(roster: list[dict], player: dict) -> list[dict]:
    """R' = T(R, p)."""
    return list(roster) + [_lineup_row(player)]


def marginal_given_roster(
    roster: list[dict],
    candidate: dict,
    slots: dict[str, int],
) -> float:
    """M_D(candidate | roster) via same lineup_ev path as D."""
    base = lineup_ev(roster, slots).total
    after = lineup_ev(roster + [_lineup_row(candidate)], slots).total
    return float(after - base)


def continuation_value(
    roster_after: list[dict],
    remaining: list[dict],
    slots: dict[str, int],
    *,
    exclude_player_id: str | None = None,
) -> dict[str, Any]:
    """
    C(R') = max M_D(q|R') over remaining q (excluding exclude_player_id / already on roster).
    """
    on_roster = {str(p.get("player_id")) for p in roster_after}
    skip = {exclude_player_id} if exclude_player_id else set()
    best_md: float | None = None
    best_row: dict | None = None
    base = lineup_ev(roster_after, slots).total
    for q in remaining:
        qid = str(q.get("player_id"))
        if qid in on_roster or qid in skip:
            continue
        if _pts(q) <= 0:
            continue
        after = lineup_ev(roster_after + [_lineup_row(q)], slots).total
        md = float(after - base)
        if best_md is None or md > best_md + 1e-12:
            best_md = md
            best_row = q
        elif best_md is not None and abs(md - best_md) <= 1e-12 and best_row is not None:
            # tie-break like D: lower ADP, then name
            def key(r: dict, m: float) -> tuple:
                return (
                    -m,
                    r.get("adp_espn") is None,
                    r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                    r.get("name") or "",
                )

            if key(q, md) < key(best_row, best_md):
                best_row = q
                best_md = md

    if best_md is None:
        return {
            "continuation": 0.0,
            "continuation_missing": True,
            "continuation_player_id": None,
            "continuation_name": None,
            "continuation_position": None,
            "construction_id": CONSTRUCTION_ID,
        }
    return {
        "continuation": float(best_md),
        "continuation_missing": False,
        "continuation_player_id": str(best_row.get("player_id")),
        "continuation_name": best_row.get("name"),
        "continuation_position": (best_row.get("position") or "").upper(),
        "construction_id": CONSTRUCTION_ID,
    }


def score_one_step(
    *,
    roster: list[dict],
    candidate: dict,
    remaining: list[dict],
    slots: dict[str, int],
) -> dict[str, Any]:
    """M_B(p) = M_D(p|R) + C(R∪{p})."""
    md = marginal_given_roster(roster, candidate, slots)
    roster_p = transition_roster(roster, candidate)
    cinfo = continuation_value(
        roster_p,
        remaining,
        slots,
        exclude_player_id=str(candidate.get("player_id")),
    )
    mb = round(float(md) + float(cinfo["continuation"]), 2)
    return {
        "marginal_d": round(float(md), 2),
        "continuation": cinfo["continuation"],
        "continuation_missing": cinfo["continuation_missing"],
        "continuation_player_id": cinfo["continuation_player_id"],
        "continuation_name": cinfo["continuation_name"],
        "continuation_position": cinfo["continuation_position"],
        "marginal_b": mb,
        "construction_id": CONSTRUCTION_ID,
    }


def rank_by_mb(
    *,
    roster: list[dict],
    remaining: list[dict],
    slots: dict[str, int],
) -> list[dict]:
    """Score every remaining candidate; sort by M_B then D tie-breaks."""
    out: list[dict] = []
    for cand in remaining:
        if _pts(cand) <= 0:
            continue
        scored = score_one_step(
            roster=roster,
            candidate=cand,
            remaining=remaining,
            slots=slots,
        )
        row = dict(cand)
        row.update(scored)
        row["marginal"] = scored["marginal_b"]
        out.append(row)
    out.sort(
        key=lambda r: (
            -(r.get("marginal") or 0.0),
            r.get("adp_espn") is None,
            r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
            r.get("ecr_fp_ppr") is None,
            r.get("ecr_fp_ppr") if r.get("ecr_fp_ppr") is not None else 9999,
            r.get("name") or "",
        )
    )
    return out
