"""Unit tests for ADP feasibility helper."""

from draftopt.strategies.adp_feasible import is_feasible_add, min_starter_picks_needed
from draftopt.strategies import get_strategy


def test_get_strategy_adp_feasible():
    assert get_strategy("adp_feasible").name == "adp_feasible"


def test_min_picks_empty_roster():
    slots = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "FLEX": 2,
        "DST": 1,
        "K": 0,
    }
    counts = {p: 0 for p in ("QB", "RB", "WR", "TE", "DST", "K")}
    # 1+2+2+1+2+1 = 9
    assert min_starter_picks_needed(counts, slots) == 9


def test_dst_forced_when_last_pick():
    slots = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "FLEX": 2,
        "DST": 1,
        "K": 0,
    }
    # Starters filled except DST; one pick left → only DST feasible
    counts = {"QB": 1, "RB": 3, "WR": 3, "TE": 1, "DST": 0, "K": 0}
    assert min_starter_picks_needed(counts, slots) == 1
    assert is_feasible_add(counts, "DST", slots=slots, remaining_picks_after=0) is True
    assert is_feasible_add(counts, "RB", slots=slots, remaining_picks_after=0) is False
