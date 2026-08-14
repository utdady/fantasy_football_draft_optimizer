from draftopt.lookahead import (
    advance_adp_greedy,
    advance_future,
    mixture_two_pick_ev,
    two_pick_ev,
)
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


def test_advance_future_proj_greedy_takes_highest_proj():
    remaining = [
        {
            "player_id": "adp1",
            "name": "LowProj",
            "position": "WR",
            "adp_espn": 1.0,
            "proj_espn": 100.0,
        },
        {
            "player_id": "adp2",
            "name": "HighProj",
            "position": "RB",
            "adp_espn": 2.0,
            "proj_espn": 300.0,
        },
        {
            "player_id": "adp3",
            "name": "Mid",
            "position": "WR",
            "adp_espn": 3.0,
            "proj_espn": 200.0,
        },
    ]
    survivors = advance_future(remaining, 1, "proj_greedy")
    assert [p["player_id"] for p in survivors] == ["adp1", "adp3"]
    assert advance_future(remaining, 1, "adp_greedy")[0]["player_id"] == "adp2"


def test_mixture_equals_mean_of_parts():
    slots = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 2, "DST": 1, "K": 0}
    roster = []
    cand = {
        "player_id": "c1",
        "name": "Cand",
        "position": "WR",
        "season_points": 280,
        "proj_espn": 280,
        "adp_espn": 5,
    }
    remaining = [
        cand,
        {
            "player_id": "q1",
            "name": "Q1",
            "position": "RB",
            "season_points": 270,
            "proj_espn": 270,
            "adp_espn": 6,
        },
        {
            "player_id": "q2",
            "name": "Q2",
            "position": "QB",
            "season_points": 360,
            "proj_espn": 360,
            "adp_espn": 7,
        },
    ]
    mix = mixture_two_pick_ev(
        roster, cand, remaining, slots, n_cpu_picks=0, n_teams=10
    )
    assert mix["ok"]
    parts = mix["parts"]
    mean = sum(float(parts[p]["ev"]) for p in parts) / len(parts)
    assert abs(mix["ev"] - mean) < 1e-9
    # n_cpu=0 → all futures identical survivors → mixture equals alpha.
    alpha = two_pick_ev(
        roster, cand, remaining, slots, n_cpu_picks=0, future_policy="adp_greedy"
    )
    assert abs(mix["ev"] - alpha["ev"]) < 1e-9


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
    assert get_strategy("marginal_v2_beta").name == "marginal_v2_beta"
    assert get_strategy("v2_beta").name == "marginal_v2_beta"
    assert get_strategy("v2b").name == "marginal_v2_beta"


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
