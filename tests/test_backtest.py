from draftopt.backtest import parse_slots, pick_rng, run_backtest, run_matrix, run_one
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import create_draft, is_user_turn, record_user_pick, snapshot
from draftopt.pool import remaining_ranked


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


def test_pick_rng_deterministic_per_overall():
    a = pick_rng(7, 12)
    b = pick_rng(7, 12)
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]
    assert pick_rng(7, 12).random() != pick_rng(7, 13).random()


def test_paired_cpu_identical_when_user_picks_match(catalog, conn):
    """Same seed + same user picks ⇒ identical CPU boards (paired environment)."""
    _seed_pool(conn, 60)
    seed = 99
    cpu_seqs = []
    for _ in range(2):
        draft_id = create_draft(
            conn, user_slot=1, user_name="Pair", roster_preset="league_default", n_rounds=3
        )
        cpu_picks = []
        while True:
            state = snapshot(conn, draft_id)
            if state["complete"]:
                break
            draft_row = conn.execute(
                "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
            ).fetchone()
            if is_user_turn(draft_row):
                # Fixed policy: always take best remaining ADP.
                pid = remaining_ranked(conn, draft_id)[0]["player_id"]
                record_user_pick(conn, draft_id, pid, made_by="test")
            else:
                overall = int(draft_row["current_pick"])
                before = {
                    r["player_id"]
                    for r in conn.execute(
                        "SELECT player_id FROM picks WHERE draft_id = ?", (draft_id,)
                    )
                }
                cpu_pick(conn, draft_id, rng=pick_rng(seed, overall))
                after = conn.execute(
                    "SELECT player_id FROM picks WHERE draft_id = ? AND overall = ?",
                    (draft_id, overall),
                ).fetchone()
                assert after is not None
                assert after["player_id"] not in before
                cpu_picks.append((overall, after["player_id"]))
        cpu_seqs.append(cpu_picks)
    assert cpu_seqs[0] == cpu_seqs[1]
    assert len(cpu_seqs[0]) > 0


def test_parse_slots():
    assert parse_slots("1,5,10") == [1, 5, 10]
    assert parse_slots("1-3") == [1, 2, 3]
    assert parse_slots("2-4,1") == [2, 3, 4, 1]


def test_backtest_smoke(catalog, conn):
    _seed_pool(conn, 40)
    report = run_backtest(
        n=1,
        slot=1,
        preset="league_default",
        seed=1,
        conn=conn,
        n_rounds=2,
        strategies=("adp", "greedy", "marginal"),
    )
    assert report["n"] == 1
    assert report["paired"] is True
    assert report["summaries"]["adp"]["n"] == 1
    assert report["summaries"]["greedy"]["n"] == 1
    assert report["summaries"]["marginal"]["n"] == 1
    assert "marginal_vs_adp" in report["comparisons"]
    assert "marginal_vs_greedy" in report["comparisons"]
    assert "mean_starter_rank" in report["summaries"]["adp"]
    assert "median_starter_pts" in report["summaries"]["adp"]
    assert "position_share" in report["summaries"]["marginal"]
    assert "by_round_share" in report["summaries"]["marginal"]


def test_matrix_smoke(catalog, conn):
    _seed_pool(conn, 40)
    matrix = run_matrix(
        n=1,
        slots=[1, 2],
        preset="league_default",
        seed=2,
        conn=conn,
        n_rounds=2,
        strategies=("adp", "marginal"),
    )
    assert matrix["slots"] == [1, 2]
    assert len(matrix["rows"]) == 2


def test_run_one_reports_starter_rank(catalog, conn):
    _seed_pool(conn, 40)
    result = run_one(
        conn,
        strategy_name="adp",
        user_slot=1,
        roster_preset="league_default",
        seed=3,
        n_rounds=2,
    )
    assert 1 <= result.starter_rank <= 10
    assert 1 <= result.roster_rank <= 10
