"""Unit tests + Gates P/N for Branch B one-step continuation."""

from draftopt.config import get_roster_preset
from draftopt.phase2.onestep_continuation import (
    CONSTRUCTION_ID,
    continuation_value,
    marginal_given_roster,
    rank_by_mb,
    score_one_step,
    transition_roster,
)

_SLOTS = get_roster_preset("league_default")["slots"]


def _p(pid, name, pos, pts, adp=None):
    return {
        "player_id": pid,
        "name": name,
        "position": pos,
        "season_points": pts,
        "adp_espn": adp,
    }


def test_transition_appends_player():
    roster = [_p("1", "X", "RB", 100)]
    nxt = transition_roster(roster, _p("2", "Y", "WR", 90))
    assert len(nxt) == 2
    assert nxt[1]["player_id"] == "2"
    assert nxt[1]["position"] == "WR"


def test_continuation_excludes_picked_player():
    roster = []
    pool = [
        _p("a", "A", "WR", 200.0, 1),
        _p("b", "B", "QB", 180.0, 2),
        _p("c", "C", "RB", 170.0, 3),
    ]
    after_a = transition_roster(roster, pool[0])
    cinfo = continuation_value(
        after_a, pool, _SLOTS, exclude_player_id="a"
    )
    assert cinfo["continuation_missing"] is False
    assert cinfo["continuation_player_id"] != "a"
    assert cinfo["construction_id"] == CONSTRUCTION_ID


def test_md_unchanged_by_continuation_helpers():
    roster = []
    cand = _p("w", "WR1", "WR", 210.0)
    pool = [cand, _p("q", "QB1", "QB", 200.0)]
    md1 = marginal_given_roster(roster, cand, _SLOTS)
    scored = score_one_step(roster=roster, candidate=cand, remaining=pool, slots=_SLOTS)
    assert scored["marginal_d"] == round(md1, 2)


def _filled_except_te_dst():
    """Starters full except TE and DST — isolates need-specific continuations."""
    return [
        _p("qb", "QB0", "QB", 250),
        _p("rb1", "RB1", "RB", 200),
        _p("rb2", "RB2", "RB", 190),
        _p("rb3", "RB3", "RB", 180),  # FLEX
        _p("wr1", "WR1", "WR", 200),
        _p("wr2", "WR2", "WR", 190),
        _p("wr3", "WR3", "WR", 180),  # FLEX
    ]


def test_gate_p_controlled_reversal():
    """
    Gate P: M_D(A) > M_D(B) but M_B(B) > M_B(A) via different continuations.
    Only TE+DST open. A=TE mediocre-high; B=DST slightly lower;
    after TE, only weak DST remains; after DST, elite TE remains.
    """
    roster = _filled_except_te_dst()
    a = _p("A", "CandA_TE", "TE", 100.0, adp=10)
    b = _p("B", "CandB_DST", "DST", 90.0, adp=20)
    te_star = _p("TE*", "TE_Star", "TE", 200.0, adp=30)
    dst_weak = _p("DST*", "DST_Weak", "DST", 20.0, adp=40)
    pool = [a, b, te_star, dst_weak]

    md_a = marginal_given_roster(roster, a, _SLOTS)
    md_b = marginal_given_roster(roster, b, _SLOTS)
    assert md_a > md_b

    sa = score_one_step(roster=roster, candidate=a, remaining=pool, slots=_SLOTS)
    sb = score_one_step(roster=roster, candidate=b, remaining=pool, slots=_SLOTS)
    assert sb["continuation"] > sa["continuation"]
    assert sb["marginal_b"] > sa["marginal_b"], (
        f"Gate P fail: M_B(B)={sb['marginal_b']} not > M_B(A)={sa['marginal_b']}"
    )

    ranked = rank_by_mb(roster=roster, remaining=pool, slots=_SLOTS)
    assert ranked[0]["player_id"] == "B"


def test_gate_n_no_spurious_reversal():
    """
    Gate N: M_D(A) > M_D(B); similar continuations → B must not reverse.
    Only TE+DST open; after either, the complementary star is similar value.
    """
    roster = _filled_except_te_dst()
    a = _p("A", "CandA_TE", "TE", 100.0, adp=10)
    b = _p("B", "CandB_DST", "DST", 95.0, adp=20)
    te_alt = _p("TE2", "TE_Alt", "TE", 80.0, adp=30)
    dst_alt = _p("DST2", "DST_Alt", "DST", 80.0, adp=40)
    pool = [a, b, te_alt, dst_alt]

    md_a = marginal_given_roster(roster, a, _SLOTS)
    md_b = marginal_given_roster(roster, b, _SLOTS)
    assert md_a > md_b

    sa = score_one_step(roster=roster, candidate=a, remaining=pool, slots=_SLOTS)
    sb = score_one_step(roster=roster, candidate=b, remaining=pool, slots=_SLOTS)
    # Continuations similar (other need ~80–100); gap must not reverse D's order.
    assert abs(sa["continuation"] - sb["continuation"]) <= 5.0

    ranked = rank_by_mb(roster=roster, remaining=pool, slots=_SLOTS)
    assert ranked[0]["player_id"] == "A"
    assert sa["marginal_b"] >= sb["marginal_b"]


def test_empty_remaining_continuation_missing():
    roster = []
    only = _p("only", "Only", "WR", 100.0)
    scored = score_one_step(
        roster=roster, candidate=only, remaining=[only], slots=_SLOTS
    )
    assert scored["continuation_missing"] is True
    assert scored["continuation"] == 0.0
    assert scored["marginal_b"] == scored["marginal_d"]
