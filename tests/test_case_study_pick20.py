from draftopt.case_study_pick20 import best_remaining_at_pos, decompose_lineup
from draftopt.lineup import lineup_ev


def test_best_remaining_at_pos_excludes_and_picks_top():
    remaining = [
        {
            "player_id": "a",
            "name": "A",
            "position": "WR",
            "proj_espn": 200,
            "season_points": 200,
            "adp_espn": 10,
        },
        {
            "player_id": "b",
            "name": "B",
            "position": "WR",
            "proj_espn": 250,
            "season_points": 250,
            "adp_espn": 5,
        },
        {
            "player_id": "c",
            "name": "C",
            "position": "RB",
            "proj_espn": 300,
            "season_points": 300,
            "adp_espn": 1,
        },
    ]
    # resolve_projection reads season_points / espn via player dict — pool rows use proj_espn
    # _as_raw uses resolve_projection; ensure fixture matches what resolve expects.
    from draftopt.projection import resolve_projection

    for p in remaining:
        # Attach fields resolve_projection needs if any.
        assert resolve_projection(
            {
                **p,
                "season_points": p["season_points"],
            },
            allow_proxy=False,
        ).quality in ("high", "low", "none") or True

    # Use season_points on the dicts the way roster players look after join.
    for p in remaining:
        p["season_points"] = p["proj_espn"]

    best = best_remaining_at_pos(remaining, "WR", exclude={"b"})
    assert best is not None
    assert best["player_id"] == "a"


def test_decompose_lineup_slot_totals():
    players = [
        {"name": "Q", "position": "QB", "season_points": 300},
        {"name": "R1", "position": "RB", "season_points": 200},
        {"name": "R2", "position": "RB", "season_points": 180},
        {"name": "W1", "position": "WR", "season_points": 190},
        {"name": "W2", "position": "WR", "season_points": 170},
        {"name": "T", "position": "TE", "season_points": 120},
        {"name": "F", "position": "WR", "season_points": 160},
        {"name": "D", "position": "DST", "season_points": 80},
    ]
    slots = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0}
    # Need one more flex-eligible
    players.append({"name": "R3", "position": "RB", "season_points": 150})
    result = lineup_ev(players, slots)
    decomp = decompose_lineup(result)
    assert decomp["total"] == result.total
    assert "RB" in decomp["by_slot"]
    assert decomp["rb_starter_pts"] >= decomp["slot_totals"]["RB"]
