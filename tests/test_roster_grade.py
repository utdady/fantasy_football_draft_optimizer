from draftopt.config import get_roster_preset, roster_draft_rounds
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import create_draft, record_pick, search_remaining


def test_default_roster_is_16_rounds_no_k():
    preset = get_roster_preset("league_default")
    assert preset["slots"]["K"] == 0
    assert preset["slots"]["BENCH"] == 7
    assert preset["n_rounds"] == 16
    assert roster_draft_rounds(preset["slots"], draft_ir=False) == 16


def test_espn_with_k_is_16_rounds():
    preset = get_roster_preset("espn_with_k")
    assert preset["slots"]["K"] == 1
    assert preset["n_rounds"] == 16


def test_create_draft_stores_roster(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, user_name="Tester", roster_preset="league_default")
    row = conn.execute("SELECT n_rounds, roster_json FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
    assert row["n_rounds"] == 16
    assert "league_default" in row["roster_json"]


def test_search_filters_by_position(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    rbs = search_remaining(conn, draft_id, position="RB", sort="adp")
    assert rbs
    assert all(r["position"] == "RB" for r in rbs)


def test_recommend_skips_kicker_when_league_has_no_k(catalog, conn):
    # Inject a fake high-ADP kicker so it would otherwise be recommended first.
    conn.execute(
        """
        INSERT INTO players (
            player_id, name, position, team, bye, status, injury_status,
            sleeper_id, espn_id, fantasypros_id, updated_at
        ) VALUES ('k1', 'Fake Kicker', 'K', 'SEA', 5, 'Active', NULL, 'k1', '999', NULL, '2026-08-12T00:00:00Z')
        """
    )
    conn.execute(
        "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES ('k1', 'espn', 0.5, '2026-08-12T00:00:00Z')"
    )
    conn.commit()
    draft_id = create_draft(conn, user_slot=1, roster_preset="league_default")
    from draftopt.recommend import recommend

    recs = recommend(conn, draft_id, n=5)
    assert all(r["position"] != "K" for r in recs)
    assert recs[0]["player_id"] != "k1"


def test_search_hides_kickers_in_no_k_league(catalog, conn):
    conn.execute(
        """
        INSERT INTO players (
            player_id, name, position, team, bye, status, injury_status,
            sleeper_id, espn_id, fantasypros_id, updated_at
        ) VALUES ('k2', 'Another Kicker', 'K', 'SEA', 5, 'Active', NULL, 'k2', '998', NULL, '2026-08-12T00:00:00Z')
        """
    )
    conn.execute(
        "INSERT INTO player_aliases (player_id, alias) VALUES ('k2', 'anotherkicker')"
    )
    conn.commit()
    draft_id = create_draft(conn, user_slot=1, roster_preset="league_default")
    hits = search_remaining(conn, draft_id, query="another", position="ALL")
    assert all(h["position"] != "K" for h in hits)


def test_grade_ranks_teams(catalog, conn):
    draft_id = create_draft(conn, user_slot=1, user_name="Tester", n_rounds=2)
    record_pick(conn, draft_id, "1002", made_by="user")
    grade = grade_draft(conn, draft_id)
    assert grade["user"]["is_user"] is True
    assert grade["user"]["picks"] == 1
    assert len(grade["teams"]) == 10
    assert grade["teams"][0]["rank"] == 1

