"""V2-alpha helpers: deterministic ADP-greedy futures (in-memory, no DB writes)."""

from __future__ import annotations

from draftopt.lineup import lineup_ev
from draftopt.projection import resolve_projection


def advance_adp_greedy(remaining: list[dict], n_picks: int) -> list[dict]:
    """
    Simulate n_picks opponent selections by always taking the current ADP leader.

    `remaining` must already be ADP-sorted (as from remaining_ranked).
    Returns the survivor list (does not mutate the input list).
    """
    if n_picks <= 0:
        return list(remaining)
    survivors = list(remaining)
    for _ in range(min(n_picks, len(survivors))):
        survivors.pop(0)
    return survivors


def as_lineup_player(player: dict) -> dict:
    proj = resolve_projection(player, allow_proxy=False)
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "position": player.get("position"),
        "team": player.get("team"),
        "season_points": proj.value,
        "projection_source": proj.source,
        "projection_quality": proj.quality,
        "adp_espn": player.get("adp_espn"),
        "ecr_fp_ppr": player.get("ecr_fp_ppr"),
    }


def best_raw_marginal_q(
    roster: list[dict],
    survivors: list[dict],
    slots: dict[str, int],
) -> tuple[dict | None, float]:
    """
    Among survivors with high-quality ESPN proj, pick q maximizing
    lineup_ev(roster + [q]) - lineup_ev(roster). Returns (q_lined, lift).
    """
    base = lineup_ev(roster, slots).total
    best: dict | None = None
    best_lift = float("-inf")
    for cand in survivors:
        lined = as_lineup_player(cand)
        if lined["projection_quality"] != "high" or lined["season_points"] <= 0:
            continue
        lift = lineup_ev(roster + [lined], slots).total - base
        if best is None or lift > best_lift + 1e-9:
            best = lined
            best_lift = lift
            continue
        if abs(lift - best_lift) <= 1e-9 and best is not None:
            # Stable ADP / name tie-break (match marginal strategy).
            ba = best.get("adp_espn")
            ca = lined.get("adp_espn")
            if (ca is not None) and (ba is None or ca < ba):
                best = lined
                best_lift = lift
            elif ca == ba and (lined.get("name") or "") < (best.get("name") or ""):
                best = lined
                best_lift = lift
    if best is None:
        return None, 0.0
    return best, best_lift


def two_pick_ev(
    roster: list[dict],
    candidate: dict,
    remaining: list[dict],
    slots: dict[str, int],
    *,
    n_cpu_picks: int,
) -> dict:
    """
    EV(p) = L(R+p+q) after ADP-greedy removal of n_cpu_picks between picks.

    If no viable q, falls back to L(R+p).
    """
    p = as_lineup_player(candidate)
    if p["projection_quality"] != "high" or p["season_points"] <= 0:
        return {
            "ok": False,
            "ev": 0.0,
            "one_pick": 0.0,
            "q": None,
            "n_cpu_picks": n_cpu_picks,
        }

    roster_p = roster + [p]
    one_pick = lineup_ev(roster_p, slots).total
    after_p = [r for r in remaining if r.get("player_id") != p.get("player_id")]
    survivors = advance_adp_greedy(after_p, n_cpu_picks)
    q, _lift = best_raw_marginal_q(roster_p, survivors, slots)
    if q is None:
        return {
            "ok": True,
            "ev": one_pick,
            "one_pick": one_pick,
            "q": None,
            "n_cpu_picks": n_cpu_picks,
            "fallback": "no_q",
        }
    ev = lineup_ev(roster_p + [q], slots).total
    return {
        "ok": True,
        "ev": ev,
        "one_pick": one_pick,
        "q": q,
        "n_cpu_picks": n_cpu_picks,
        "fallback": None,
    }
