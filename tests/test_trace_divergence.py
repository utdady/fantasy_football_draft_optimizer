from draftopt.draft.snake import next_user_overall
from draftopt.draft.state import create_draft
from draftopt.trace_divergence import compare_at_turn, run_trace


def test_next_user_overall_snake_gaps():
    # Slot 1: pick 1 → next 20; others between = 18; wait_distance = 19
    assert next_user_overall(1, user_slot=1, n_teams=10) == 20
    # Slot 5: pick 5 → next 16
    assert next_user_overall(5, user_slot=5, n_teams=10) == 16
    # Slot 10: pick 10 → next 11 (back-to-back)
    assert next_user_overall(10, user_slot=10, n_teams=10) == 11


def test_compare_at_turn_fields(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    cmp = compare_at_turn(conn, draft_id, user_slot=1, n_teams=10)
    assert cmp["overall_pick"] == 1
    assert cmp["next_user_pick"] == 20
    assert cmp["picks_until_next"] == 18
    assert cmp["wait_distance"] == 19
    assert cmp["raw"] and cmp["vor"]
    for side in (cmp["raw"], cmp["vor"]):
        for key in ("player", "position", "projection", "lineup_gain", "replacement_pts", "VOR"):
            assert key in side


def test_run_trace_smoke(catalog, conn):
    # Tiny fixture pool: only the first user pick is reachable.
    report = run_trace(
        slots=[1],
        n_sims=1,
        max_user_picks=1,
        seed=1,
        board_drivers=("marginal",),
        conn=conn,
    )
    assert report["slots"] == [1]
    assert len(report["by_slot"][1]["sims"]) == 1
    sim = report["by_slot"][1]["sims"][0]
    assert sim["user_picks_traced"] == 1
    assert sim["agreements"] + len(sim["disagreements"]) == 1
