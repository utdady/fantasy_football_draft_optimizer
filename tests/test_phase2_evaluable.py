"""Tests for Phase 2 evaluable gate and snapshot flags."""

from __future__ import annotations

import sqlite3

import pytest

from draftopt.phase2.evaluable import (
    SnapshotNotEvaluable,
    require_evaluable,
    set_snapshot_flags,
)
from draftopt.phase2.schema import migrate_eval_schema


def _fresh_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate_eval_schema(conn)
    return conn


def _insert_snap(
    conn: sqlite3.Connection,
    snapshot_id: str,
    *,
    pipeline_proof: int,
    evaluable: int,
    outcome_season: int | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO eval_snapshots (
            snapshot_id, season, snapshot_date, label, notes, created_at,
            pipeline_proof, evaluable, outcome_season
        ) VALUES (?, 2026, '2026-08-12', ?, 'n', '2026-08-12T00:00:00Z', ?, ?, ?)
        """,
        (snapshot_id, snapshot_id, pipeline_proof, evaluable, outcome_season),
    )
    conn.commit()


def test_require_evaluable_refuses_pipeline_proof():
    conn = _fresh_conn()
    _insert_snap(
        conn, "2026-preseason-2026-08-12", pipeline_proof=1, evaluable=0
    )
    with pytest.raises(SnapshotNotEvaluable, match="not evaluable"):
        require_evaluable(conn, "2026-preseason-2026-08-12")
    conn.close()


def test_require_evaluable_ok():
    conn = _fresh_conn()
    _insert_snap(
        conn,
        "2024-preseason-2024-08-20",
        pipeline_proof=0,
        evaluable=1,
        outcome_season=2024,
    )
    snap = require_evaluable(conn, "2024-preseason-2024-08-20")
    assert int(snap["evaluable"]) == 1
    assert snap["outcome_season"] == 2024
    conn.close()


def test_require_evaluable_unknown():
    conn = _fresh_conn()
    with pytest.raises(SnapshotNotEvaluable, match="unknown"):
        require_evaluable(conn, "missing")
    conn.close()


def test_migrate_adds_flag_columns_to_legacy_table():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE eval_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            season INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            label TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        );
        """
    )
    migrate_eval_schema(conn)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(eval_snapshots)")}
    assert "pipeline_proof" in cols
    assert "evaluable" in cols
    assert "outcome_season" in cols
    conn.close()


def test_set_snapshot_flags():
    conn = _fresh_conn()
    _insert_snap(conn, "s1", pipeline_proof=0, evaluable=0)
    set_snapshot_flags(
        conn, "s1", pipeline_proof=True, evaluable=False, outcome_season=None
    )
    row = conn.execute(
        "SELECT pipeline_proof, evaluable FROM eval_snapshots WHERE snapshot_id='s1'"
    ).fetchone()
    assert int(row["pipeline_proof"]) == 1
    assert int(row["evaluable"]) == 0
    conn.close()
