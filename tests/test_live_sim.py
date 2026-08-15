"""Live league sim: human picks for every seat."""

from __future__ import annotations

import pytest

from draftopt.draft.state import (
    DraftError,
    create_draft,
    record_human_pick,
    record_user_pick,
    snapshot,
    undo_pick,
)


def test_user_only_rejects_off_turn(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, pick_mode="user_only")
    record_human_pick(conn, draft_id, "1001")  # user R1
    with pytest.raises(DraftError, match="not your pick"):
        record_human_pick(conn, draft_id, "1002")


def test_live_sim_allows_proxy_picks(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, pick_mode="live_sim", user_name="addy")
    state = record_human_pick(conn, draft_id, "1001")
    assert state["pick_mode"] == "live_sim"
    assert state["picks"][0]["made_by"] == "user"
    assert state["can_human_pick"] is True
    assert state["is_user_turn"] is False

    state = record_human_pick(conn, draft_id, "1002")
    assert state["picks"][1]["made_by"] == "proxy"
    assert state["picks"][1]["team_slot"] == 2
    assert state["current_pick"] == 3


def test_live_sim_undo_last_only(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, pick_mode="live_sim")
    record_human_pick(conn, draft_id, "1001")
    record_human_pick(conn, draft_id, "1002")
    state = undo_pick(conn, draft_id)
    assert len(state["picks"]) == 1
    assert state["picks"][0]["player_id"] == "1001"
    assert state["current_pick"] == 2


def test_invalid_pick_mode(catalog, conn):
    with pytest.raises(DraftError, match="pick_mode"):
        create_draft(conn, pick_mode="chaos")


def test_snapshot_defaults_user_only(catalog, conn):
    draft_id = create_draft(conn, user_slot=5)
    st = snapshot(conn, draft_id)
    assert st["pick_mode"] == "user_only"
    assert st["can_human_pick"] == st["is_user_turn"]


def test_record_user_pick_unchanged(catalog, conn):
    draft_id = create_draft(conn, user_slot=2)
    with pytest.raises(DraftError, match="not your pick"):
        record_user_pick(conn, draft_id, "1001")
