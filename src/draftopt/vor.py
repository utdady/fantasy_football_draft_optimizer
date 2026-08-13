from __future__ import annotations

from draftopt.pool import remaining_ranked
from draftopt.projection import resolve_projection

# FLEX starter demand split across RB/WR/TE (approx. PPR usage).
FLEX_SHARE = {"RB": 0.45, "WR": 0.45, "TE": 0.10}


def league_starter_demand(n_teams: int, slots: dict[str, int]) -> dict[str, int]:
    """How many starters the league starts at each position (incl. FLEX share)."""
    flex = int(slots.get("FLEX") or 0) * n_teams
    demand = {
        "QB": int(slots.get("QB") or 0) * n_teams,
        "RB": int(slots.get("RB") or 0) * n_teams + int(round(flex * FLEX_SHARE["RB"])),
        "WR": int(slots.get("WR") or 0) * n_teams + int(round(flex * FLEX_SHARE["WR"])),
        "TE": int(slots.get("TE") or 0) * n_teams + int(round(flex * FLEX_SHARE["TE"])),
        "DST": int(slots.get("DST") or 0) * n_teams,
        "K": int(slots.get("K") or 0) * n_teams,
    }
    return {k: max(1, v) if v > 0 else 0 for k, v in demand.items()}


def replacement_baselines(
    conn,
    draft_id: str,
    *,
    n_teams: int,
    slots: dict[str, int],
) -> dict[str, float]:
    """
    VOR-lite: Nth-best remaining ESPN projection at each position.

    N ≈ league starter demand (fixed slots + FLEX share). If fewer than N
    projected players remain, baseline is 0 (no reliable replacement).
    """
    demand = league_starter_demand(n_teams, slots)
    by_pos: dict[str, list[float]] = {p: [] for p in demand}
    for p in remaining_ranked(conn, draft_id):
        proj = resolve_projection(p, allow_proxy=False)
        if proj.quality != "high":
            continue
        pos = (p.get("position") or "").upper()
        if pos not in by_pos:
            continue
        by_pos[pos].append(proj.value)
    baselines: dict[str, float] = {}
    for pos, vals in by_pos.items():
        n = demand.get(pos) or 0
        if n <= 0:
            baselines[pos] = 0.0
            continue
        vals.sort(reverse=True)
        if len(vals) < n:
            baselines[pos] = 0.0
        else:
            baselines[pos] = float(vals[n - 1])
    return baselines


def vor_points(proj: float, position: str | None, baselines: dict[str, float]) -> float:
    pos = (position or "").upper()
    base = float(baselines.get(pos) or 0.0)
    return max(0.0, float(proj) - base)
