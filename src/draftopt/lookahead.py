"""V2 helpers: deterministic futures (in-memory, no DB writes).

V2-alpha freezes a single ADP-greedy future. V2-beta averages equal-weight
futures under adp_greedy / proj_greedy / vor opponents.
"""

from __future__ import annotations

from draftopt.lineup import lineup_ev
from draftopt.projection import resolve_projection
from draftopt.vor import replacement_baselines_from_remaining, vor_points

# Futures used by V2-beta (equal weight). Alpha uses only adp_greedy.
BETA_FUTURE_POLICIES = ("adp_greedy", "proj_greedy", "vor")


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


def _proj(player: dict) -> float:
    val = player.get("proj_espn")
    if val is None:
        proj = resolve_projection(player, allow_proxy=False)
        return float(proj.value) if proj.quality == "high" else -1.0
    return float(val)


def _index_to_remove(
    remaining: list[dict],
    policy: str,
    *,
    slots: dict[str, int],
    n_teams: int,
) -> int:
    """Index of the player a deterministic opponent policy would take."""
    if not remaining:
        return -1
    key = (policy or "adp_greedy").strip().lower()
    if key == "adp_greedy":
        return 0

    if key == "proj_greedy":
        best_i = 0
        best_key = (
            _proj(remaining[0]),
            -(
                remaining[0].get("adp_espn")
                if remaining[0].get("adp_espn") is not None
                else 9999
            ),
            remaining[0].get("name") or "",
        )
        for i, p in enumerate(remaining[1:], start=1):
            k = (
                _proj(p),
                -(p.get("adp_espn") if p.get("adp_espn") is not None else 9999),
                p.get("name") or "",
            )
            if k > best_key:
                best_key = k
                best_i = i
        return best_i

    if key == "vor":
        baselines = replacement_baselines_from_remaining(
            remaining, n_teams=n_teams, slots=slots
        )
        best_i = 0
        best_key: tuple | None = None
        for i, p in enumerate(remaining):
            proj = _proj(p)
            if proj <= 0:
                continue
            pos = (p.get("position") or "").upper()
            k = (
                vor_points(proj, pos, baselines),
                proj,
                -(p.get("adp_espn") if p.get("adp_espn") is not None else 9999),
                p.get("name") or "",
            )
            if best_key is None or k > best_key:
                best_key = k
                best_i = i
        return best_i if best_key is not None else 0

    raise ValueError(f"unknown future policy: {policy}")


def advance_future(
    remaining: list[dict],
    n_picks: int,
    policy: str = "adp_greedy",
    *,
    slots: dict[str, int] | None = None,
    n_teams: int = 10,
) -> list[dict]:
    """
    Advance the remaining pool by n_picks under a deterministic opponent policy.

    Does not mutate `remaining`. For adp_greedy, list should be ADP-sorted.
    """
    if n_picks <= 0:
        return list(remaining)
    key = (policy or "adp_greedy").strip().lower()
    if key == "adp_greedy":
        return advance_adp_greedy(remaining, n_picks)

    slots = slots or {}
    survivors = list(remaining)
    for _ in range(min(n_picks, len(survivors))):
        idx = _index_to_remove(survivors, key, slots=slots, n_teams=n_teams)
        if idx < 0:
            break
        survivors.pop(idx)
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
    future_policy: str = "adp_greedy",
    n_teams: int = 10,
) -> dict:
    """
    EV(p) = L(R+p+q) after advancing n_cpu_picks under future_policy.

    Default future_policy=adp_greedy preserves V2-alpha. If no viable q,
    falls back to L(R+p).
    """
    p = as_lineup_player(candidate)
    if p["projection_quality"] != "high" or p["season_points"] <= 0:
        return {
            "ok": False,
            "ev": 0.0,
            "one_pick": 0.0,
            "q": None,
            "n_cpu_picks": n_cpu_picks,
            "future_policy": future_policy,
        }

    roster_p = roster + [p]
    one_pick = lineup_ev(roster_p, slots).total
    after_p = [r for r in remaining if r.get("player_id") != p.get("player_id")]
    survivors = advance_future(
        after_p,
        n_cpu_picks,
        future_policy,
        slots=slots,
        n_teams=n_teams,
    )
    q, _lift = best_raw_marginal_q(roster_p, survivors, slots)
    if q is None:
        return {
            "ok": True,
            "ev": one_pick,
            "one_pick": one_pick,
            "q": None,
            "n_cpu_picks": n_cpu_picks,
            "future_policy": future_policy,
            "fallback": "no_q",
        }
    ev = lineup_ev(roster_p + [q], slots).total
    return {
        "ok": True,
        "ev": ev,
        "one_pick": one_pick,
        "q": q,
        "n_cpu_picks": n_cpu_picks,
        "future_policy": future_policy,
        "fallback": None,
    }


def mixture_two_pick_ev(
    roster: list[dict],
    candidate: dict,
    remaining: list[dict],
    slots: dict[str, int],
    *,
    n_cpu_picks: int,
    n_teams: int = 10,
    policies: tuple[str, ...] = BETA_FUTURE_POLICIES,
) -> dict:
    """
    Equal-weight average of two_pick_ev under each future policy (V2-beta).

    No Monte Carlo / no learned weights.
    """
    if not policies:
        raise ValueError("mixture_two_pick_ev requires at least one policy")
    parts: dict[str, dict] = {}
    for pol in policies:
        parts[pol] = two_pick_ev(
            roster,
            candidate,
            remaining,
            slots,
            n_cpu_picks=n_cpu_picks,
            future_policy=pol,
            n_teams=n_teams,
        )
    # If candidate is not scorable, every part fails the same way.
    if not any(r.get("ok") for r in parts.values()):
        first = next(iter(parts.values()))
        return {
            "ok": False,
            "ev": 0.0,
            "one_pick": 0.0,
            "parts": parts,
            "n_cpu_picks": n_cpu_picks,
            "policies": list(policies),
        }

    ok_parts = [r for r in parts.values() if r.get("ok")]
    ev = sum(float(r["ev"]) for r in ok_parts) / len(ok_parts)
    one_pick = float(ok_parts[0]["one_pick"])
    # Representative q from ADP future when available (diagnostics only).
    q = (parts.get("adp_greedy") or ok_parts[0]).get("q")
    return {
        "ok": True,
        "ev": ev,
        "one_pick": one_pick,
        "q": q,
        "parts": parts,
        "n_cpu_picks": n_cpu_picks,
        "policies": list(policies),
        "fallback": None,
    }
