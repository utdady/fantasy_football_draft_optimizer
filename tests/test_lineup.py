from draftopt.lineup import lineup_ev, starter_points


SLOTS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0, "BENCH": 7}


def test_empty_roster_is_zero():
    assert starter_points([], SLOTS) == 0.0


def test_fills_fixed_slots_then_flex():
    players = [
        {"name": "QB1", "position": "QB", "season_points": 300},
        {"name": "RB1", "position": "RB", "season_points": 250},
        {"name": "RB2", "position": "RB", "season_points": 200},
        {"name": "RB3", "position": "RB", "season_points": 180},
        {"name": "WR1", "position": "WR", "season_points": 240},
        {"name": "WR2", "position": "WR", "season_points": 220},
        {"name": "WR3", "position": "WR", "season_points": 210},
        {"name": "TE1", "position": "TE", "season_points": 150},
        {"name": "DST1", "position": "DST", "season_points": 100},
    ]
    result = lineup_ev(players, SLOTS)
    # Starters: QB+2RB+2WR+TE+2FLEX+DST
    # FLEX should take WR3 (210) and RB3 (180)
    assert len(result.starters["FLEX"]) == 2
    flex_names = {p["name"] for p in result.starters["FLEX"]}
    assert flex_names == {"WR3", "RB3"}
    assert result.total == 300 + 250 + 200 + 240 + 220 + 150 + 210 + 180 + 100


def test_missing_dst_still_scores_skill():
    players = [{"name": "QB1", "position": "QB", "season_points": 300}]
    assert starter_points(players, SLOTS) == 300.0
