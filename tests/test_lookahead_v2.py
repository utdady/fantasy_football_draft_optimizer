from draftopt.lookahead import advance_adp_greedy, two_pick_ev
from draftopt.strategies import get_strategy


def test_advance_adp_greedy_pops_prefix():
    remaining = [
        {"player_id": "1", "name": "A", "adp_espn": 1.0},
        {"player_id": "2", "name": "B", "adp_espn": 2.0},
        {"player_id": "3", "name": "C", "adp_espn": 3.0},
        {"player_id": "4", "name": "D", "adp_espn": 4.0},
    ]
    survivors = advance_adp_greedy(remaining, 2)
    assert [p["player_id"] for p in survivors] == ["3", "4"]
    # Input not mutated
    assert len(remaining) == 4
    assert advance_adp_greedy(remaining, 0) == remaining


def test_two_pick_ev_commutative_back_to_back():
    """With n_cpu=0, taking Nabers then Kyren == Kyren then Nabers."""
    slots = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0}
    roster = [
        {
            "player_id": "qb",
            "name": "QB",
            "position": "QB",
            "season_points": 370,
            "proj_espn": 370,
        }
    ]
    nabers = {
        "player_id": "nabers",
        "name": "Nabers",
        "position": "WR",
        "season_points": 301,
        "proj_espn": 301,
        "adp_espn": 5,
    }
    kyren = {
        "player_id": "kyren",
        "name": "Kyren",
        "position": "RB",
        "season_points": 284,
        "proj_espn": 284,
        "adp_espn": 6,
    }
    remaining = [nabers, kyren]
    a = two_pick_ev(roster, kyren, remaining, slots, n_cpu_picks=0)
    b = two_pick_ev(roster, nabers, remaining, slots, n_cpu_picks=0)
    assert a["ok"] and b["ok"]
    assert abs(a["ev"] - b["ev"]) < 1e-6
    assert a["q"]["player_id"] == "nabers"
    assert b["q"]["player_id"] == "kyren"


def test_get_strategy_marginal_v2():
    s = get_strategy("marginal_v2")
    assert s.name == "marginal_v2"
    assert get_strategy("v2_alpha").name == "marginal_v2"
    assert get_strategy("lookahead_adp").name == "marginal_v2"


def test_recommend_does_not_mutate_draft(catalog, conn):
    from draftopt.draft.state import create_draft

    draft_id = create_draft(conn, user_slot=1)
    before = conn.execute(
        "SELECT current_pick FROM drafts WHERE draft_id = ?", (draft_id,)
    ).fetchone()["current_pick"]
    n_picks = conn.execute(
        "SELECT COUNT(*) AS n FROM picks WHERE draft_id = ?", (draft_id,)
    ).fetchone()["n"]
    recs = get_strategy("marginal_v2").recommend(conn, draft_id, n=1)
    assert recs  # tiny catalog still has candidates
    after = conn.execute(
        "SELECT current_pick FROM drafts WHERE draft_id = ?", (draft_id,)
    ).fetchone()["current_pick"]
    n_after = conn.execute(
        "SELECT COUNT(*) AS n FROM picks WHERE draft_id = ?", (draft_id,)
    ).fetchone()["n"]
    assert after == before
    assert n_after == n_picks
