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


def test_removed_order_modes_rejected():
    with pytest.raises(DraftError, match="order_mode"):
        resolve_draft_seating(n_teams=12, user_name="addy", order_mode="random_all")
    with pytest.raises(DraftError, match="order_mode"):
        resolve_draft_seating(n_teams=12, user_name="addy", order_mode="fixed")


def test_pick_slot_applies_team_names():
    slot, seating = resolve_draft_seating(
        n_teams=12,
        user_name="addy",
        order_mode="pick_slot",
        user_slot=1,
        team_names={"2": "Sam", "5": "Lee"},
    )
    assert slot == 1
    assert seating[1] == "addy"
    assert seating[2] == "Sam"
    assert seating[5] == "Lee"
    assert seating[3] == "CPU 3"


def test_team_names_must_be_unique():
    with pytest.raises(DraftError, match="unique"):
        resolve_draft_seating(
            n_teams=12,
            user_name="addy",
            user_slot=1,
            team_names={"2": "Sam", "3": "sam"},
        )

