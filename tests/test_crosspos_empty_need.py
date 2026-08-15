"""Contract tests for V3-B.1 crosspos_empty_need_nextbest (a*)."""

from draftopt.phase2.crosspos_empty_need import (
    CONSTRUCTION_ID,
    crosspos_empty_need_nextbest,
    empty_capacity_positions,
)
from draftopt.phase2.replacement_nextbest import replacement_nextbest

# league_default-shaped slots (no K)
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


def test_fixed_slot_deficits_empty_roster():
    n = empty_capacity_positions(_counts(), _SLOTS)
    assert n == frozenset({"QB", "RB", "WR", "TE", "DST"})  # K=0; FLEX expands RB/WR/TE


def test_fixed_slot_deficits_partial_fill():
    # 1 QB, 2 RB, 0 WR, 0 TE, 0 DST — WR/TE/DST fixed open; FLEX still open
    n = empty_capacity_positions(_counts(QB=1, RB=2), _SLOTS)
    assert "QB" not in n
    assert "RB" in n  # via FLEX capacity
    assert "WR" in n
    assert "TE" in n
    assert "DST" in n


def test_flex_expansion_only_when_flex_open():
    # Fixed starters full with extras filling both FLEX: no capacity left
    # 1 QB, 2 RB + 1 extra, 2 WR + 1 extra, 1 TE, 1 DST → flex_filled=2
    n = empty_capacity_positions(
        _counts(QB=1, RB=3, WR=3, TE=1, DST=1),
        _SLOTS,
    )
    assert n == frozenset()


def test_flex_only_capacity_includes_rb_wr_te():
    # Fixed RB/WR/TE filled exactly; FLEX still empty → N = {RB, WR, TE} (+DST/QB if open)
    n = empty_capacity_positions(
        _counts(QB=1, RB=2, WR=2, TE=1, DST=1),
        _SLOTS,
    )
    assert n == frozenset({"RB", "WR", "TE"})


def test_a_star_selects_best_cross_need():
    counts = _counts()  # all empty
    pool = [
        {"player_id": "w1", "position": "WR", "calibrated_value": 300.0, "name": "W1"},
        {"player_id": "w2", "position": "WR", "calibrated_value": 280.0, "name": "W2"},
        {"player_id": "b1", "position": "RB", "calibrated_value": 290.0, "name": "B1"},
        {"player_id": "q1", "position": "QB", "calibrated_value": 250.0, "name": "Q1"},
    ]
    out = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_missing"] is False
    assert out["cross_alt"] == 290.0
    assert out["cross_alt_player_id"] == "b1"
    assert out["construction_id"] == CONSTRUCTION_ID


def test_no_same_position_alternative():
    counts = _counts()
    pool = [
        {"player_id": "w1", "position": "WR", "calibrated_value": 300.0},
        {"player_id": "w2", "position": "WR", "calibrated_value": 299.0},
        {"player_id": "b1", "position": "RB", "calibrated_value": 100.0},
    ]
    out = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt"] == 100.0
    assert out["cross_alt_player_id"] == "b1"


def test_empty_alternative_set_fallback():
    # Only WR capacity left; candidate is WR → no cross-pos alternative
    counts = _counts(QB=1, RB=4, TE=1, DST=1)  # WR fixed open; FLEX may still need
    # RB extras: 4-2=2 fill FLEX; WR need fixed; TE/QB/DST filled
    # N includes WR (and maybe others). Candidate WR → alternatives must be non-WR in N.
    # If N is only WR, A empty.
    n = empty_capacity_positions(counts, _SLOTS)
    # FLEX filled by 2 RB extras; WR fixed still open → N={WR}
    assert n == frozenset({"WR"})
    pool = [
        {"player_id": "w1", "position": "WR", "calibrated_value": 300.0},
        {"player_id": "w2", "position": "WR", "calibrated_value": 280.0},
        {"player_id": "b1", "position": "RB", "calibrated_value": 200.0},
    ]
    out = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_missing"] is True
    assert out["cross_alt"] == 0.0
    assert out["cross_alt_player_id"] is None


def test_bench_phase_all_capacity_full():
    counts = _counts(QB=1, RB=3, WR=3, TE=1, DST=1)
    assert empty_capacity_positions(counts, _SLOTS) == frozenset()
    pool = [
        {"player_id": "w1", "position": "WR", "calibrated_value": 300.0},
        {"player_id": "b1", "position": "RB", "calibrated_value": 290.0},
    ]
    out = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt_missing"] is True
    assert out["cross_alt"] == 0.0


def test_b0_ne_b1_fixture():
    """Contract §4: empty WR+RB; candidate best WR; v(b1) != v(w2)."""
    counts = _counts()
    pool = [
        {"player_id": "w1", "position": "WR", "calibrated_value": 320.0, "name": "W1"},
        {"player_id": "w2", "position": "WR", "calibrated_value": 280.0, "name": "W2"},
        {"player_id": "b1", "position": "RB", "calibrated_value": 300.0, "name": "B1"},
    ]
    r = replacement_nextbest(player_id="w1", position="WR", remaining=pool)
    a = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert r["replacement"] == 280.0  # same-pos w2
    assert a["cross_alt"] == 300.0  # cross-pos b1
    assert a["cross_alt"] != r["replacement"]


def test_ignores_actual_ppr():
    counts = _counts()
    pool = [
        {
            "player_id": "w1",
            "position": "WR",
            "calibrated_value": 300.0,
            "actual_ppr": 999.0,
        },
        {
            "player_id": "b1",
            "position": "RB",
            "calibrated_value": 200.0,
            "actual_ppr": 500.0,
        },
    ]
    out = crosspos_empty_need_nextbest(
        player_id="w1",
        position="WR",
        remaining=pool,
        counts=counts,
        slots=_SLOTS,
    )
    assert out["cross_alt"] == 200.0
