from draftopt.draft.state import create_draft
from draftopt.pool import candidate_pool


def test_candidate_pool_includes_high_proj_outside_adp_window(catalog, conn):
    # Insert a low-ADP-rank (high adp number) player with huge projection.
    conn.execute(
        """
        INSERT INTO players (
            player_id, name, position, team, bye, status, injury_status,
            sleeper_id, espn_id, fantasypros_id, updated_at
        ) VALUES ('sleeper', 'Sleeper Star', 'WR', 'CHI', 7, 'Active', NULL,
                  'sl1', '88881', NULL, '2026-08-12T00:00:00Z')
        """
    )
    conn.execute(
        "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES ('sleeper', 'espn', 400, '2026-08-12T00:00:00Z')"
    )
    conn.execute(
        "INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at) "
        "VALUES ('sleeper', 'espn', 999, '2026-08-12T00:00:00Z')"
    )
    conn.commit()
    draft_id = create_draft(conn, user_slot=1)
    pool = candidate_pool(conn, draft_id, n_adp=2, n_proj=2)
    ids = {p["player_id"] for p in pool}
    assert "sleeper" in ids
    # ADP window still present
    assert len(pool) >= 2
