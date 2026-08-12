import pytest

from draftopt.draft.state import DraftError, create_draft, record_pick, resolve_player, search_remaining, undo_pick


def test_record_and_reject_duplicate(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    state = record_pick(conn, draft_id, "1001")
    assert state["picks"][0]["name"] == "Ja'Marr Chase"
    assert state["current_pick"] == 2
    assert state["current_team"] == 2
    with pytest.raises(DraftError, match="already drafted"):
        record_pick(conn, draft_id, "1001")


def test_undo_restores_player(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    record_pick(conn, draft_id, "1001")
    state = undo_pick(conn, draft_id)
    assert state["current_pick"] == 1
    assert state["picks"] == []
    record_pick(conn, draft_id, "1001")


def test_search_and_resolve_punctuation(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    hits = search_remaining(conn, draft_id, "jamarr")
    assert any(h["name"] == "Ja'Marr Chase" for h in hits)
    assert resolve_player(conn, draft_id, "Ja'Marr Chase") == "1001"
    record_pick(conn, draft_id, "1001")
    with pytest.raises(DraftError, match="no matching"):
        resolve_player(conn, draft_id, "jamarr")


def test_recommend_orders_by_espn_adp(catalog, conn):
    from draftopt.strategies.adp import ADPStrategy

    draft_id = create_draft(conn, user_slot=1)
    recs = ADPStrategy().recommend(conn, draft_id, n=3)
    assert recs[0]["name"] == "Bijan Robinson"
    assert recs[1]["name"] == "Ja'Marr Chase"
    record_pick(conn, draft_id, recs[0]["player_id"])
    recs = ADPStrategy().recommend(conn, draft_id, n=3)
    assert recs[0]["name"] == "Ja'Marr Chase"
