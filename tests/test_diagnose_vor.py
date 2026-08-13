from draftopt.diagnose_vor import run_traces, trace_decision
from draftopt.draft.state import create_draft
from draftopt.vor import replacement_snapshot


def test_replacement_snapshot_exposes_n_and_pts(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    snap = replacement_snapshot(
        conn,
        draft_id,
        n_teams=10,
        slots={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0},
    )
    assert snap["RB"]["replacement_n"] == 29
    assert snap["WR"]["replacement_n"] == 29
    assert "replacement_pts" in snap["QB"]


def test_trace_decision_has_candidate_fields(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    trace = trace_decision(conn, draft_id, top_n=3)
    assert trace["round"] == 1
    assert "rb_vs_wr_replacement" in trace
    assert trace["top_candidates"]
    row = trace["top_candidates"][0]
    for key in (
        "projection",
        "replacement_n",
        "replacement_pts",
        "vor_points",
        "lineup_gain_raw",
        "lineup_gain_vor",
    ):
        assert key in row


def test_run_traces_smoke(catalog, conn):
    # Tiny fixture pool — just ensure the harness completes.
    report = run_traces(n_sims=1, slot=1, max_round=1, seed=1, top_n=3, conn=conn)
    assert report["n_sims"] == 1
    assert report["sims"][0]["picks"]
