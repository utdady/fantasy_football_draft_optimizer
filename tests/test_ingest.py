def test_join_maps_ids_and_metrics(catalog, conn):
    assert catalog["players"] == 4
    chase = conn.execute("SELECT * FROM players WHERE player_id = '1001'").fetchone()
    assert chase["name"] == "Ja'Marr Chase"
    assert chase["espn_id"] == "4241479"
    assert chase["fantasypros_id"] == "17288"
    assert chase["bye"] == 10

    adp = conn.execute(
        "SELECT adp FROM adp_snapshots WHERE player_id = '1001' AND source = 'espn'"
    ).fetchone()
    assert adp["adp"] == 4.7

    proj = conn.execute(
        "SELECT season_points FROM projections_snapshots WHERE player_id = '1001'"
    ).fetchone()
    assert proj["season_points"] == 336.35

    ecr = conn.execute(
        "SELECT ecr, sd FROM rankings_snapshots WHERE player_id = '1001'"
    ).fetchone()
    assert ecr["ecr"] == 1.8
    assert ecr["sd"] == 1.08


def test_dst_normalized_and_searchable(catalog, conn):
    dst = conn.execute("SELECT * FROM players WHERE player_id = 'SF'").fetchone()
    assert dst["position"] == "DST"
    aliases = {
        r["alias"]
        for r in conn.execute("SELECT alias FROM player_aliases WHERE player_id = 'SF'")
    }
    assert "sf" in aliases
    assert "49ers" in aliases


def test_dynasty_page_excluded(catalog, conn):
    n = conn.execute("SELECT COUNT(*) AS n FROM players WHERE name = 'Ignore Me'").fetchone()
    assert n["n"] == 0
