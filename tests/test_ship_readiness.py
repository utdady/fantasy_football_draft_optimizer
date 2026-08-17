"""Ship-readiness DB gates."""

from __future__ import annotations

from draftopt.ship_readiness import check_db


def _check(name: str, checks: list[dict]) -> dict:
    for c in checks:
        if c["check"] == name:
            return c
    raise AssertionError(f"missing check {name!r}")


def test_draftable_skill_proj_passes_on_catalog(catalog, conn):
    result = _check("draftable_skill_proj", check_db(conn))
    assert result["ok"] is True
    assert "missing=0" in result["detail"]


def test_draftable_skill_proj_fails_when_draftable_skill_missing_proj(catalog, conn):
    conn.execute(
        """
        INSERT INTO players (
            player_id, name, position, team, bye, status, injury_status,
            sleeper_id, espn_id, fantasypros_id, updated_at
        ) VALUES ('gap1', 'Proj Gap Guy', 'WR', 'SEA', 5, 'Active', NULL, 'gap1', '8888', NULL, '2026-08-12T00:00:00Z')
        """
    )
    conn.execute(
        "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES ('gap1', 'espn', 50.0, '2026-08-12T00:00:00Z')"
    )
    conn.commit()

    result = _check("draftable_skill_proj", check_db(conn))
    assert result["ok"] is False
    assert "missing=1" in result["detail"]
