"""Draft seating / order modes."""

from __future__ import annotations

import random

import pytest

from draftopt.draft.state import DraftError, resolve_draft_seating


def test_pick_slot_defaults_cpu_labels():
    slot, seating = resolve_draft_seating(
        n_teams=12,
        user_name="addy",
        order_mode="pick_slot",
        user_slot=3,
    )
    assert slot == 3
    assert seating[3] == "addy"
    assert seating[1] == "CPU 1"


def test_random_slot_is_in_range():
    rng = random.Random(0)
    slots = {
        resolve_draft_seating(
            n_teams=12, user_name="addy", order_mode="random_slot", rng=rng
        )[0]
        for _ in range(40)
    }
    assert slots <= set(range(1, 13))
    assert len(slots) > 1


def test_random_all_shuffles_user_and_opponents():
    rng = random.Random(1)
    opponents = [f"P{i}" for i in range(11)]
    slot, seating = resolve_draft_seating(
        n_teams=12,
        user_name="addy",
        order_mode="random_all",
        opponent_names=opponents,
        rng=rng,
    )
    assert seating[slot] == "addy"
    assert set(seating.values()) == {"addy", *opponents}
    assert len(seating) == 12


def test_random_all_requires_exact_count():
    with pytest.raises(DraftError):
        resolve_draft_seating(
            n_teams=12,
            user_name="addy",
            order_mode="random_all",
            opponent_names=["a", "b"],
        )


def test_fixed_order():
    names = {str(i): f"P{i}" for i in range(1, 13)}
    names["7"] = "addy"
    slot, seating = resolve_draft_seating(
        n_teams=12,
        user_name="addy",
        order_mode="fixed",
        team_names=names,
    )
    assert slot == 7
    assert seating[7] == "addy"
    assert seating[1] == "P1"
