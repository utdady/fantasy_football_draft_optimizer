from draftopt.draft.state import create_draft
from draftopt.trace_v2_divergence import compare_three, run_trace


def test_compare_three_fields(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    cmp = compare_three(conn, draft_id, user_slot=1, n_teams=10)
    assert cmp["overall_pick"] == 1
    assert cmp["next_user_pick"] == 20
    for side in ("raw", "vor", "v2"):
        assert cmp[side]
        assert "player" in cmp[side]
        assert "projection" in cmp[side]
    assert "ev_two_pick" in cmp["v2"]
    assert "q_player" in cmp["v2"]


def test_run_trace_smoke(catalog, conn):
    report = run_trace(
        slots=[1],
        n_sims=1,
        max_user_picks=1,
        seed=1,
        board_drivers=("marginal",),
        conn=conn,
    )
    assert len(report["by_slot"][1]["sims"]) == 1
    assert report["by_slot"][1]["sims"][0]["user_picks_traced"] == 1
