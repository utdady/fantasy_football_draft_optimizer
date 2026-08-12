from draftopt.backtest import run_backtest


def _seed_pool(conn, n: int = 40) -> None:
    for i in range(n):
        pid = f"p{i}"
        pos = ["QB", "RB", "WR", "TE", "DST"][i % 5]
        conn.execute(
            """
            INSERT OR IGNORE INTO players (
                player_id, name, position, team, bye, status, injury_status,
                sleeper_id, espn_id, fantasypros_id, updated_at
            ) VALUES (?, ?, ?, 'SEA', 5, 'Active', NULL, ?, ?, NULL, '2026-08-12T00:00:00Z')
            """,
            (pid, f"Player {i}", pos, pid, str(9000 + i)),
        )
        conn.execute(
            "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES (?, 'espn', ?, '2026-08-12T00:00:00Z')",
            (pid, float(i + 1)),
        )
        conn.execute(
            "INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at) VALUES (?, 'espn', ?, '2026-08-12T00:00:00Z')",
            (pid, float(300 - i * 3)),
        )
        conn.execute(
            "INSERT OR IGNORE INTO player_aliases (player_id, alias) VALUES (?, ?)",
            (pid, f"player{i}"),
        )
    conn.commit()


def test_backtest_smoke(catalog, conn):
    _seed_pool(conn, 40)
    report = run_backtest(n=1, slot=1, preset="league_default", seed=1, conn=conn, n_rounds=2)
    assert report["n"] == 1
    assert report["summaries"]["adp"]["n"] == 1
    assert report["summaries"]["marginal"]["n"] == 1
