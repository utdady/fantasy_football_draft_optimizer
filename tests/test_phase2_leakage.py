"""Unit tests for Phase 2 leakage validator (no DB ingest required)."""

import pytest

from draftopt.phase2.leakage import (
    LeakageError,
    assert_snapshot_clean,
    check_as_of,
    validate_snapshot_player_row,
)


def test_check_as_of_ok():
    check_as_of(as_of="2024-08-20", snapshot_date="2024-08-25", field="adp_as_of")
    check_as_of(as_of="2024-08-25", snapshot_date="2024-08-25", field="adp_as_of")


def test_check_as_of_leak_raises():
    with pytest.raises(LeakageError, match="leakage"):
        check_as_of(
            as_of="2024-09-01", snapshot_date="2024-08-25", field="proj_as_of"
        )


def test_validate_row_findings():
    findings = validate_snapshot_player_row(
        snapshot_id="s1",
        snapshot_date="2024-08-25",
        player_id="p1",
        adp_as_of="2024-08-20",
        proj_as_of="2024-09-01",
    )
    assert len(findings) == 1
    assert findings[0].field == "proj_as_of"


def test_assert_snapshot_clean():
    rows = [
        {
            "player_id": "a",
            "adp_as_of": "2024-08-20",
            "proj_as_of": "2024-08-20",
        }
    ]
    assert_snapshot_clean(rows, snapshot_id="s1", snapshot_date="2024-08-25")
    rows[0]["adp_as_of"] = "2024-08-26"
    with pytest.raises(LeakageError):
        assert_snapshot_clean(rows, snapshot_id="s1", snapshot_date="2024-08-25")
