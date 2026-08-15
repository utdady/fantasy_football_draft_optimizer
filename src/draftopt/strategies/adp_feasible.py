"""ADP + mandatory starter feasibility (not a new valuation model).

Take lowest ADP among players that leave enough remaining picks to fill
required starter slots (QB/RB/WR/TE/FLEX/DST/K). No marginal EV.
"""

from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.pool import remaining_ranked
from draftopt.strategies.adp import ADPStrategy

_POS = ("QB", "RB", "WR", "TE", "DST", "K")


def _counts_from_rows(rows: list[dict]) -> dict[str, int]:
    counts = {p: 0 for p in _POS}
    for row in rows:
        pos = (row.get("position") or "").upper()
        if pos in counts:
            counts[pos] += 1
    return counts


def min_starter_picks_needed(counts: dict[str, int], slots: dict[str, int]) -> int:
    """
    Minimum remaining picks required to complete starter requirements.

    Fixed slots first; leftover RB/WR/TE count toward FLEX.
    """
    qb_need = max(0, int(slots.get("QB") or 0) - counts.get("QB", 0))
    rb_need = max(0, int(slots.get("RB") or 0) - counts.get("RB", 0))
    wr_need = max(0, int(slots.get("WR") or 0) - counts.get("WR", 0))
    te_need = max(0, int(slots.get("TE") or 0) - counts.get("TE", 0))
    dst_need = max(0, int(slots.get("DST") or 0) - counts.get("DST", 0))
    k_need = max(0, int(slots.get("K") or 0) - counts.get("K", 0))
    rb_extra = max(0, counts.get("RB", 0) - int(slots.get("RB") or 0))
    wr_extra = max(0, counts.get("WR", 0) - int(slots.get("WR") or 0))
    te_extra = max(0, counts.get("TE", 0) - int(slots.get("TE") or 0))
    flex_cap = int(slots.get("FLEX") or 0)
    flex_filled = min(flex_cap, rb_extra + wr_extra + te_extra)
    flex_need = max(0, flex_cap - flex_filled)
    return qb_need + rb_need + wr_need + te_need + flex_need + dst_need + k_need


def is_feasible_add(
    counts: dict[str, int],
    position: str,
    *,
    slots: dict[str, int],
    remaining_picks_after: int,
) -> bool:
    pos = (position or "").upper()
    if pos not in _POS:
        # Unknown position: allow only if already complete (bench fluff)
        return min_starter_picks_needed(counts, slots) <= remaining_picks_after
    nxt = dict(counts)
    nxt[pos] = nxt.get(pos, 0) + 1
    return min_starter_picks_needed(nxt, slots) <= remaining_picks_after


class AdpFeasibleStrategy(ADPStrategy):
    """
    Pure ADP subject to starter feasibility.

    Separates 'knows required slots must be filled' from structural valuation.
    """

    name = "adp_feasible"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = (draft_roster(draft).get("slots") or {})
        user_slot = int(draft["user_slot"])
        n_rounds = int(draft["n_rounds"])
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
        remaining_including_this = max(0, n_rounds - drafted)

        out: list[dict] = []
        for rec in remaining_ranked(conn, draft_id):
            rem_after = remaining_including_this - 1
            if not is_feasible_add(
                counts,
                rec.get("position") or "",
                slots=slots,
                remaining_picks_after=rem_after,
            ):
                continue
            item = dict(rec)
            item["strategy"] = self.name
            item["why"] = (
                "P2.2C: lowest ADP among picks that preserve starter feasibility"
            )
            out.append(item)
            if len(out) >= n:
                break
        # Fail-open only if nothing is feasible (should not happen with valid pool)
        if not out:
            return super().recommend(conn, draft_id, n=n)
        return out
