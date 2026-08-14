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


def replacement_snapshot(
    conn,
    draft_id: str,
    *,
    n_teams: int,
    slots: dict[str, int],
) -> dict:
    """
    VOR-lite replacement detail for diagnostics.

    Returns demand N, baseline pts, and the Nth player (when available) per position.
    """
    demand = league_starter_demand(n_teams, slots)
    by_pos: dict[str, list[tuple[float, str]]] = {p: [] for p in demand}
    for p in remaining_ranked(conn, draft_id):
        proj = resolve_projection(p, allow_proxy=False)
        if proj.quality != "high":
            continue
        pos = (p.get("position") or "").upper()
        if pos not in by_pos:
            continue
        by_pos[pos].append((proj.value, p.get("name") or p["player_id"]))
    out: dict[str, dict] = {}
    for pos, rows in by_pos.items():
        n = int(demand.get(pos) or 0)
        rows.sort(key=lambda t: t[0], reverse=True)
        if n <= 0:
            out[pos] = {
                "replacement_n": 0,
                "replacement_pts": 0.0,
                "replacement_name": None,
                "pool_size": len(rows),
            }
            continue
        if len(rows) < n:
            out[pos] = {
                "replacement_n": n,
                "replacement_pts": 0.0,
                "replacement_name": None,
                "pool_size": len(rows),
            }
        else:
            pts, name = rows[n - 1]
            out[pos] = {
                "replacement_n": n,
                "replacement_pts": float(pts),
                "replacement_name": name,
                "pool_size": len(rows),
            }
    return out


def replacement_baselines(
    conn,
    draft_id: str,
    *,
    n_teams: int,
    slots: dict[str, int],
) -> dict[str, float]:
    """Nth-best remaining ESPN projection at each position (league starter demand)."""
    snap = replacement_snapshot(conn, draft_id, n_teams=n_teams, slots=slots)
    return {pos: float(info["replacement_pts"]) for pos, info in snap.items()}


def replacement_baselines_from_remaining(
    remaining: list[dict],
    *,
    n_teams: int,
    slots: dict[str, int],
) -> dict[str, float]:
    """In-memory VOR baselines from a remaining pool (no DB)."""
    demand = league_starter_demand(n_teams, slots)
    by_pos: dict[str, list[float]] = {p: [] for p in demand}
    for p in remaining:
        proj = resolve_projection(p, allow_proxy=False)
        if proj.quality != "high":
            continue
        pos = (p.get("position") or "").upper()
        if pos not in by_pos:
            continue
        by_pos[pos].append(float(proj.value))
    out: dict[str, float] = {}
    for pos, vals in by_pos.items():
        n = int(demand.get(pos) or 0)
        vals.sort(reverse=True)
        if n <= 0 or len(vals) < n:
            out[pos] = 0.0
        else:
            out[pos] = float(vals[n - 1])
    return out


def vor_points(proj: float, position: str | None, baselines: dict[str, float]) -> float:
    pos = (position or "").upper()
    base = float(baselines.get(pos) or 0.0)
    return max(0.0, float(proj) - base)
