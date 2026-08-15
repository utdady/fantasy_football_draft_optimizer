"""Contract tests for V3-B replacement_nextbest (r*)."""

from draftopt.phase2.replacement_nextbest import CONSTRUCTION_ID, replacement_nextbest


def _pool(*rows):
    return list(rows)


def test_excludes_candidate_from_replacement_set():
    pool = _pool(
        {"player_id": "a", "position": "QB", "calibrated_value": 350.0, "name": "A"},
        {"player_id": "b", "position": "QB", "calibrated_value": 300.0, "name": "B"},
        {"player_id": "c", "position": "QB", "calibrated_value": 280.0, "name": "C"},
    )
    out = replacement_nextbest(player_id="a", position="QB", remaining=pool)
    assert out["replacement_missing"] is False
    assert out["replacement"] == 300.0
    assert out["replacement_player_id"] == "b"
    assert out["construction_id"] == CONSTRUCTION_ID


def test_only_same_position_candidates():
    pool = _pool(
        {"player_id": "qb1", "position": "QB", "calibrated_value": 350.0},
        {"player_id": "rb1", "position": "RB", "calibrated_value": 400.0},
        {"player_id": "qb2", "position": "QB", "calibrated_value": 310.0},
    )
    out = replacement_nextbest(player_id="qb1", position="QB", remaining=pool)
    assert out["replacement"] == 310.0
    assert out["replacement_player_id"] == "qb2"


def test_position_matching_is_case_insensitive_and_deterministic():
    pool = _pool(
        {"player_id": "1", "position": "rb", "calibrated_value": 200.0, "name": "X"},
        {"player_id": "2", "position": "RB", "calibrated_value": 220.0, "name": "Y"},
        {"player_id": "3", "position": "Rb", "calibrated_value": 210.0, "name": "Z"},
    )
    out = replacement_nextbest(player_id="1", position="RB", remaining=pool)
    assert out["replacement"] == 220.0
    assert out["replacement_player_id"] == "2"


def test_replacement_missing_when_no_other_at_position():
    pool = _pool(
        {"player_id": "only", "position": "TE", "calibrated_value": 190.0},
        {"player_id": "rb", "position": "RB", "calibrated_value": 250.0},
    )
    out = replacement_nextbest(player_id="only", position="TE", remaining=pool)
    assert out["replacement_missing"] is True
    assert out["replacement"] == 0.0
    assert out["replacement_player_id"] is None


def test_skips_none_values_but_not_silent_on_empty_set():
    pool = _pool(
        {"player_id": "a", "position": "WR", "calibrated_value": 280.0},
        {"player_id": "b", "position": "WR", "calibrated_value": None},
    )
    out = replacement_nextbest(player_id="a", position="WR", remaining=pool)
    assert out["replacement_missing"] is True
    assert out["replacement"] == 0.0


def test_uses_frozen_value_key_not_actual_ppr():
    """Guard: actual_ppr must not affect r* even if present on rows."""
    pool = _pool(
        {
            "player_id": "a",
            "position": "QB",
            "calibrated_value": 350.0,
            "actual_ppr": 999.0,
        },
        {
            "player_id": "b",
            "position": "QB",
            "calibrated_value": 200.0,
            "actual_ppr": 500.0,
        },
    )
    out = replacement_nextbest(player_id="a", position="QB", remaining=pool)
    assert out["replacement"] == 200.0  # not 500
