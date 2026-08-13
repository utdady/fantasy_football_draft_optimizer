from draftopt.audit_proj_curves import build_report, cliff_flags, positional_curves


def test_positional_curves_rank_by_proj(catalog, conn):
    curves = positional_curves(conn)
    assert "QB" in curves
    assert curves["QB"][0]["name"] == "Josh Allen"
    assert curves["QB"][0]["rank"] == 1


def test_build_report_frozen_rb_wr_window(catalog, conn):
    report = build_report(conn, n_teams=10, preset="league_default")
    assert report["frozen"] is True
    assert report["demand"]["RB"] == report["demand"]["WR"] == 29
    # Tiny fixture pool may not have rank 29; window still present.
    assert report["positions"]["RB"]["window"] == (20, 40)
    assert "curve" in report["positions"]["RB"]


def test_cliff_flags_detects_large_drop():
    players = [
        {"rank": 28, "name": "A", "projection": 240, "delta_to_next": -5},
        {"rank": 29, "name": "B", "projection": 235, "delta_to_next": -40},
        {"rank": 30, "name": "C", "projection": 195, "delta_to_next": -3},
    ]
    notes = cliff_flags(players, replacement_n=29)
    assert any("29->30" in n for n in notes)
