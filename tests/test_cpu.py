import random

import pytest

from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import DraftError, create_draft, record_user_pick, undo_pick
from draftopt.strategies.adp import ADPStrategy


def test_cpu_cannot_pick_on_user_turn(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, user_name="Tester")
    with pytest.raises(DraftError, match="not a CPU pick"):
        cpu_pick(conn, draft_id)


def test_user_cannot_pick_on_cpu_turn(catalog, conn):
    draft_id = create_draft(conn, user_slot=2, user_name="Tester")
    with pytest.raises(DraftError, match="not your pick"):
        record_user_pick(conn, draft_id, "1001")


def test_cpu_picks_then_user_turn(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, user_name="Tester")
    record_user_pick(conn, draft_id, "1001")
    rng = random.Random(0)
    state = cpu_pick(conn, draft_id, rng=rng)
    assert state["current_pick"] == 3
    assert state["picks"][1]["made_by"] == "cpu"
    assert state["picks"][1]["player_id"] != "1001"


def test_undo_removes_user_pick_and_later_cpu(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, user_name="Tester")
    record_user_pick(conn, draft_id, "1001")
    cpu_pick(conn, draft_id, rng=random.Random(1))
    state = undo_pick(conn, draft_id)
    assert state["current_pick"] == 1
    assert state["picks"] == []
    recs = ADPStrategy().recommend(conn, draft_id, n=1)
    assert recs[0]["player_id"] == "1002"
