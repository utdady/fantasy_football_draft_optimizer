"""Contract tests for Branch A crosspos_empty_need_marginal (q* by M_D)."""

from draftopt.phase2.crosspos_empty_need import (
    crosspos_empty_need_nextbest,
    empty_capacity_positions,
)
from draftopt.phase2.crosspos_empty_need_marginal import (
    CONSTRUCTION_ID,
    crosspos_empty_need_marginal,
)

_SLOTS = {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "FLEX": 2,
    "DST": 1,
    "K": 0,
}


def _counts(**kwargs) -> dict[str, int]:
    base = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "DST": 0, "K": 0}
    base.update(kwargs)
    return base


def test_n_r_reuses_b1_flex_accounting():
    assert empty_capacity_positions(_counts(), _SLOTS) == frozenset(
        {"QB", "RB", "WR", "TE", "DST"}
    )
    assert empty_capacity_positions(
        _counts(QB=1, RB=2, WR=2, TE=1, DST=1), _SLOTS
    ) == frozenset({"RB", "WR", "TE"})


def test_q_star_excludes_candidate_and_same_pos():
    counts = _counts()
    pool = [
        {
            "player_id": "w1",
            "position": "WR",
            "marginal_d": 100.0,
            "name": "W1",
            "adp_espn": 10,
        },
        {
            "player_id": "w2",
            "position": "WR",
            "marginal_d": 99.0,
            "name": "W2",
            "adp_espn": 11,
        },
        {
            "player_id": "b1",
            "position": "RB",
            "marginal_d": 80.0,
            "name": "B1",
            "adp_espn": 12,
        },
    ]
    out = crosspos_empty_need_marginal(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_player_id"] == "b1"
    assert out["cross_alt_marginal"] == 80.0
    assert out["construction_id"] == CONSTRUCTION_ID


def test_q_star_selects_highest_marginal_d():
    counts = _counts()
    pool = [
        {"player_id": "qb1", "position": "QB", "marginal_d": 50.0, "name": "Q1"},
        {"player_id": "rb1", "position": "RB", "marginal_d": 90.0, "name": "R1"},
        {"player_id": "wr1", "position": "WR", "marginal_d": 70.0, "name": "W1"},
    ]
    out = crosspos_empty_need_marginal(
        player_id="qb1",
        position="QB",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_player_id"] == "rb1"
    assert out["cross_alt_marginal"] == 90.0


def test_fallback_when_no_cross_alt():
    counts = _counts(QB=1, RB=4, TE=1, DST=1)  # only WR capacity
    assert empty_capacity_positions(counts, _SLOTS) == frozenset({"WR"})
    pool = [
        {"player_id": "w1", "position": "WR", "marginal_d": 100.0},
        {"player_id": "w2", "position": "WR", "marginal_d": 90.0},
        {"player_id": "b1", "position": "RB", "marginal_d": 80.0},
    ]
    out = crosspos_empty_need_marginal(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_missing"] is True
    assert out["cross_alt_marginal"] == 0.0


def test_b1_ne_a_selection_and_subtractand():
    """Contract §5: v-argmax ≠ M_D-argmax → different q* and subtractand."""
    counts = _counts()
    # Candidate WR. Alt pool: u has high v / low M_D; w has low v / high M_D.
    pool_v = [
        {
            "player_id": "w1",
            "position": "WR",
            "calibrated_value": 320.0,
            "name": "W1",
        },
        {
            "player_id": "u",
            "position": "RB",
            "calibrated_value": 310.0,
            "name": "U",
        },
        {
            "player_id": "w",
            "position": "RB",
            "calibrated_value": 200.0,
            "name": "W",
        },
    ]
    pool_md = [
        {
            "player_id": "w1",
            "position": "WR",
            "marginal_d": 100.0,
            "calibrated_value": 320.0,
            "name": "W1",
        },
        {
            "player_id": "u",
            "position": "RB",
            "marginal_d": 40.0,
            "calibrated_value": 310.0,
            "name": "U",
        },
        {
            "player_id": "w",
            "position": "RB",
            "marginal_d": 95.0,
            "calibrated_value": 200.0,
            "name": "W",
        },
    ]
    b1 = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool_v,
        counts=counts,
        slots=_SLOTS,
    )
    a = crosspos_empty_need_marginal(
        player_id="w1",
        position="WR",
        remaining=pool_md,
        counts=counts,
        slots=_SLOTS,
    )
    assert b1["cross_alt_player_id"] == "u"
    assert b1["cross_alt"] == 310.0
    assert a["cross_alt_player_id"] == "w"
    assert a["cross_alt_marginal"] == 95.0
    assert a["cross_alt_player_id"] != b1["cross_alt_player_id"]
    assert a["cross_alt_marginal"] != b1["cross_alt"]


def test_ignores_actual_ppr():
    counts = _counts()
    pool = [
        {
            "player_id": "w1",
            "position": "WR",
            "marginal_d": 100.0,
            "actual_ppr": 999.0,
        },
        {
            "player_id": "b1",
            "position": "RB",
            "marginal_d": 50.0,
            "actual_ppr": 500.0,
        },
    ]
    out = crosspos_empty_need_marginal(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_marginal"] == 50.0
