from __future__ import annotations

from dataclasses import dataclass


FLEX_ELIGIBLE = frozenset({"RB", "WR", "TE"})
FIXED_SLOTS = ("QB", "RB", "WR", "TE", "DST", "K")


@dataclass
class LineupResult:
    total: float
    starters: dict[str, list[dict]]  # slot -> assigned players
    bench: list[dict]


def _points(player: dict) -> float:
    val = player.get("season_points")
    if val is None:
        val = player.get("proj_espn")
    if val is None:
        return 0.0
    return float(val)


def lineup_ev(players: list[dict], slots: dict[str, int]) -> LineupResult:
    """
    Greedy optimal starter assignment.

    Fill fixed position slots by points, then FLEX from leftover RB/WR/TE.
    Bench is everyone unused. IR/BENCH slot counts are ignored for EV.
    """
    pool = sorted((dict(p) for p in players), key=_points, reverse=True)
    used: set[int] = set()
    starters: dict[str, list[dict]] = {k: [] for k in (*FIXED_SLOTS, "FLEX")}
    total = 0.0

    def take(pos: str, need: int, eligible: set[str]) -> None:
        nonlocal total
        if need <= 0:
            return
        taken = 0
        for i, p in enumerate(pool):
            if i in used:
                continue
            if (p.get("position") or "").upper() not in eligible:
                continue
            used.add(i)
            starters[pos].append(p)
            total += _points(p)
            taken += 1
            if taken >= need:
                return

    for pos in FIXED_SLOTS:
        need = int(slots.get(pos) or 0)
        if need:
            take(pos, need, {pos})

    flex_need = int(slots.get("FLEX") or 0)
    if flex_need:
        take("FLEX", flex_need, set(FLEX_ELIGIBLE))

    bench = [p for i, p in enumerate(pool) if i not in used]
    return LineupResult(total=total, starters=starters, bench=bench)


def starter_points(players: list[dict], slots: dict[str, int]) -> float:
    return lineup_ev(players, slots).total
