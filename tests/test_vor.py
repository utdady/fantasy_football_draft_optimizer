from draftopt.draft.state import create_draft
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.strategies.marginal_no_qb_r1 import MarginalNoQBR1Strategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy
from draftopt.vor import league_starter_demand, replacement_baselines, vor_points


def test_vor_points_subtracts_baseline():
    assert vor_points(380, "QB", {"QB": 300}) == 80
    assert vor_points(250, "RB", {"RB": 300}) == 0


def test_league_starter_demand_includes_flex_share():
    d = league_starter_demand(10, {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0})
    assert d["QB"] == 10
    assert d["RB"] == 20 + 9  # 2*10 + round(20*0.45)
    assert d["DST"] == 10
    assert d["K"] == 0


def test_marginal_no_qb_r1_skips_qb(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    raw = MarginalValueStrategy().recommend(conn, draft_id, n=1)
    assert raw[0]["position"] == "QB"
    recs = MarginalNoQBR1Strategy().recommend(conn, draft_id, n=1)
    assert recs
    assert recs[0]["position"] != "QB"
    assert recs[0]["strategy"] == "marginal_no_qb_r1"


def test_marginal_vor_prefers_rb_when_qb_replacement_high(catalog, conn):
    # Inflate QB depth so Nth-best QB replacement is high; elite QB VOR shrinks.
    for i in range(12):
        pid = f"qb{i}"
        conn.execute(
            """
            INSERT INTO players (
                player_id, name, position, team, bye, status, injury_status,
                sleeper_id, espn_id, fantasypros_id, updated_at
            ) VALUES (?, ?, 'QB', 'BUF', 7, 'Active', NULL, ?, ?, NULL, '2026-08-12T00:00:00Z')
            """,
            (pid, f"Backup QB {i}", pid, str(8000 + i)),
        )
        conn.execute(
            "INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at) "
            "VALUES (?, 'espn', ?, '2026-08-12T00:00:00Z')",
            (pid, 310.0 - i),
        )
        conn.execute(
            "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES (?, 'espn', ?, '2026-08-12T00:00:00Z')",
            (pid, 50.0 + i),
        )
    conn.commit()
    draft_id = create_draft(conn, user_slot=1)
    baselines = replacement_baselines(
        conn,
        draft_id,
        n_teams=10,
        slots={"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0},
    )
    assert baselines["QB"] > 250
    raw = MarginalValueStrategy().recommend(conn, draft_id, n=1)
    assert raw[0]["position"] == "QB"
    vor = MarginalVorStrategy().recommend(conn, draft_id, n=1)
    assert vor
    assert vor[0]["strategy"] == "marginal_vor"
    assert vor[0]["position"] != "QB"
