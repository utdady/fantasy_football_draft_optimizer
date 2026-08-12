from __future__ import annotations

import random

from draftopt.draft.state import (
    DraftError,
    _draft_row,
    draft_roster,
    is_user_turn,
    record_pick,
    round_for_pick,
    team_for_pick,
)
from draftopt.pool import remaining_ranked

# 70% ADP-weighted, 20% positional need, 10% deeper random.
ADP_WEIGHT = 0.70
NEED_WEIGHT = 0.20


def _roster_counts(conn, draft_id: str, team_slot: int) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT p.position FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        """,
        (draft_id, team_slot),
    ).fetchall()
    counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "DST": 0, "K": 0}
    for row in rows:
        pos = row["position"]
        if pos in counts:
            counts[pos] += 1
    return counts


def _needed_positions(counts: dict[str, int], slots: dict[str, int], round_num: int, n_rounds: int) -> list[str]:
    needed: list[str] = []
    rb_need = int(slots.get("RB") or 0)
    wr_need = int(slots.get("WR") or 0)
    te_need = int(slots.get("TE") or 0)
    qb_need = int(slots.get("QB") or 0)
    dst_need = int(slots.get("DST") or 0)
    k_need = int(slots.get("K") or 0)

    if counts["RB"] < rb_need:
        needed.append("RB")
    if counts["WR"] < wr_need:
        needed.append("WR")
    if te_need and counts["TE"] < te_need and round_num >= 4:
        needed.append("TE")
    if qb_need and counts["QB"] < qb_need and round_num >= 5:
        needed.append("QB")
    late = max(1, n_rounds - 3)
    if dst_need and counts["DST"] < dst_need and round_num >= late:
        needed.append("DST")
    if k_need and counts["K"] < k_need and round_num >= late + 1:
        needed.append("K")
    return needed or ["RB", "WR", "TE"]


def choose_cpu_player(conn, draft_id: str, rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    draft = _draft_row(conn, draft_id)
    remaining = remaining_ranked(conn, draft_id)
    if not remaining:
        raise DraftError("no players remaining")
    overall = draft["current_pick"]
    team_slot = team_for_pick(overall, draft["n_teams"])
    round_num = round_for_pick(overall, draft["n_teams"])
    roster = draft_roster(draft)
    slots = roster.get("slots") or {}
    top8 = remaining[:8]
    top20 = remaining[:20]
    roll = rng.random()
    if roll < ADP_WEIGHT:
        pool = top8
        weights = list(range(len(pool), 0, -1))
        return rng.choices(pool, weights=weights, k=1)[0]["player_id"]
    if roll < ADP_WEIGHT + NEED_WEIGHT:
        counts = _roster_counts(conn, draft_id, team_slot)
        needed = set(_needed_positions(counts, slots, round_num, draft["n_rounds"]))
        pool = [p for p in top20 if p.get("position") in needed] or top8
        weights = list(range(len(pool), 0, -1))
        return rng.choices(pool, weights=weights, k=1)[0]["player_id"]
    return rng.choice(top20)["player_id"]


def cpu_pick(conn, draft_id: str, rng: random.Random | None = None) -> dict:
    draft = _draft_row(conn, draft_id)
    if is_user_turn(draft):
        raise DraftError("not a CPU pick")
    player_id = choose_cpu_player(conn, draft_id, rng=rng)
    return record_pick(conn, draft_id, player_id, made_by="cpu")
