"""Phase 2 historical evaluation helpers (schema stubs + leakage checks)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from draftopt.phase2.evaluable import (
    SnapshotNotEvaluable,
    get_snapshot_meta,
    require_evaluable,
    set_snapshot_flags,
)
from draftopt.phase2.leakage import (
    LeakageError,
    LeakageFinding,
    assert_snapshot_clean,
    check_as_of,
    validate_snapshot_player_row,
    validate_snapshot_table,
)
from draftopt.phase2.schema import EVAL_SCHEMA, migrate_eval_schema


def init_eval_db(conn: sqlite3.Connection) -> None:
    """Create Phase 2 eval tables on this connection (prefer a dedicated DB file)."""
    migrate_eval_schema(conn)


def connect_eval(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate_eval_schema(conn)
    return conn


__all__ = [
    "EVAL_SCHEMA",
    "LeakageError",
    "LeakageFinding",
    "SnapshotNotEvaluable",
    "assert_snapshot_clean",
    "check_as_of",
    "connect_eval",
    "get_snapshot_meta",
    "init_eval_db",
    "migrate_eval_schema",
    "require_evaluable",
    "set_snapshot_flags",
    "validate_snapshot_player_row",
    "validate_snapshot_table",
]
