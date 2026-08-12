from draftopt.draft.state import create_draft, record_user_pick
from draftopt.strategies.adp import ADPStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


def test_adp_strategy_orders_by_espn_adp(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    recs = ADPStrategy().recommend(conn, draft_id, n=3)
    assert recs[0]["name"] == "Bijan Robinson"
    assert recs[1]["name"] == "Ja'Marr Chase"
    assert recs[0]["strategy"] == "adp"


def test_marginal_on_empty_roster_prefers_high_projection(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    recs = MarginalValueStrategy().recommend(conn, draft_id, n=3)
    assert recs
    assert recs[0]["marginal"] is not None
    # Josh Allen has highest proj in fixtures (369)
    assert recs[0]["name"] == "Josh Allen"
    assert recs[0]["strategy"] == "marginal"


def test_marginal_with_two_rbs_prefers_non_rb(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    # Only one RB in fixtures (Bijan). Add a second RB via raw insert + pick path:
    # Draft Bijan first for user (slot 1), then simulate we already have two RBs by
    # inserting another RB onto the roster through an extra player + direct pick insert.
    record_user_pick(conn, draft_id, "1002")  # Bijan
    # After user pick, current team is 2 — inject a second RB onto user roster directly.
    conn.execute(
        """
        INSERT INTO players (
            player_id, name, position, team, bye, status, injury_status,
            sleeper_id, espn_id, fantasypros_id, updated_at
        ) VALUES ('rbx', 'Bench RB', 'RB', 'DAL', 7, 'Active', NULL, 'rbx', '777', NULL, '2026-08-12T00:00:00Z')
        """
    )
    conn.execute(
        "INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at) VALUES ('rbx', 'espn', 190, '2026-08-12T00:00:00Z')"
    )
    conn.execute(
        """
        INSERT INTO picks (draft_id, overall, team_slot, round, player_id, picked_at, made_by)
        VALUES (?, 99, 1, 10, 'rbx', '2026-08-12T00:00:00Z', 'setup')
        """,
        (draft_id,),
    )
    conn.commit()
    # Advance draft back so it's user turn somehow — recommend doesn't require user turn.
    recs = MarginalValueStrategy().recommend(conn, draft_id, n=5)
    assert recs
    # With 2 RBs filled, taking another RB should not beat a high-proj WR/QB for starter lift.
    top_positions = [r["position"] for r in recs[:2]]
    assert "RB" not in top_positions or recs[0]["position"] != "RB"
