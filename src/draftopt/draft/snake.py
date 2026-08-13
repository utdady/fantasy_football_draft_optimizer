"""Snake-draft schedule helpers."""

from __future__ import annotations

from draftopt.draft.state import team_for_pick


def next_user_overall(
    overall: int, user_slot: int, n_teams: int, *, n_rounds: int = 16
) -> int | None:
    """Next overall pick belonging to user_slot after `overall` (exclusive)."""
    limit = n_teams * n_rounds
    for o in range(overall + 1, limit + 1):
        if team_for_pick(o, n_teams) == user_slot:
            return o
    return None


def picks_until_next(overall: int, user_slot: int, n_teams: int, *, n_rounds: int = 16) -> int | None:
    """Other players drafted before the user's next turn (None if no next turn)."""
    nxt = next_user_overall(overall, user_slot, n_teams, n_rounds=n_rounds)
    if nxt is None:
        return None
    return nxt - overall - 1
