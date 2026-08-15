"""Gate: evaluation runners must refuse non-evaluable snapshots.

Pipeline-proof freezes (e.g. current-year live ESPN cuts) validate ingest +
leakage only. They must never be scored against nonexistent outcomes or used
to claim strategy wins on actual fantasy points.

CLI: python -m draftopt.phase2.assert_evaluable <snapshot_id>
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from draftopt.config import EVAL_DB_PATH
from draftopt.phase2.schema import migrate_eval_schema


class SnapshotNotEvaluable(RuntimeError):
    """Raised when a Phase 2 runner is asked to evaluate a non-evaluable snapshot."""


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_snapshot_meta(
    conn: sqlite3.Connection,
    snapshot_id: str,
) -> sqlite3.Row | None:
    migrate_eval_schema(conn)
    return conn.execute(
        "SELECT * FROM eval_snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()


def require_evaluable(
    conn: sqlite3.Connection,
    snapshot_id: str,
) -> sqlite3.Row:
    """
    Hard gate for P2.4+ replay / scoring / strategy comparison.

    Raises SnapshotNotEvaluable unless evaluable=1.
    """
    snap = get_snapshot_meta(conn, snapshot_id)
    if snap is None:
        raise SnapshotNotEvaluable(
            f"unknown snapshot_id={snapshot_id!r}; freeze an evaluation "
            f"snapshot first (not a pipeline-proof-only freeze)"
        )
    evaluable = int(snap["evaluable"] or 0)
    pipeline_proof = int(snap["pipeline_proof"] or 0)
    if evaluable != 1:
        kind = "pipeline_proof" if pipeline_proof else "non-evaluable"
        status = snap["validation_status"] if "validation_status" in snap.keys() else None
        reason = snap["validation_reason"] if "validation_reason" in snap.keys() else None
        extra = ""
        if status or reason:
            extra = f" status={status!r} reason={reason!r}."
        raise SnapshotNotEvaluable(
            f"snapshot {snapshot_id!r} is not evaluable "
            f"(pipeline_proof={pipeline_proof}, evaluable={evaluable}). "
            f"This is a {kind} freeze — use a historical snapshot with "
            f"realized outcomes (evaluable=1).{extra} Refusing evaluation."
        )
    return snap


def set_snapshot_flags(
    conn: sqlite3.Connection,
    snapshot_id: str,
    *,
    pipeline_proof: bool,
    evaluable: bool,
    outcome_season: int | None = None,
    validation_status: str | None = None,
    validation_reason: str | None = None,
) -> None:
    """Update classification flags on an existing snapshot row."""
    migrate_eval_schema(conn)
    cur = conn.execute(
        """
        UPDATE eval_snapshots
        SET pipeline_proof = ?, evaluable = ?, outcome_season = ?,
            validation_status = COALESCE(?, validation_status),
            validation_reason = COALESCE(?, validation_reason)
        WHERE snapshot_id = ?
        """,
        (
            1 if pipeline_proof else 0,
            1 if evaluable else 0,
            outcome_season,
            validation_status,
            validation_reason,
            snapshot_id,
        ),
    )
    if cur.rowcount != 1:
        raise LookupError(f"unknown snapshot_id={snapshot_id!r}")
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assert a snapshot is evaluable (exit 1 if not)"
    )
    parser.add_argument("snapshot_id", type=str)
    parser.add_argument("--eval-db", type=Path, default=None)
    args = parser.parse_args()
    path = args.eval_db or EVAL_DB_PATH
    conn = _connect(path)
    try:
        snap = require_evaluable(conn, args.snapshot_id)
    except SnapshotNotEvaluable as e:
        print(f"REFUSE: {e}")
        raise SystemExit(1) from e
    finally:
        conn.close()
    print(
        f"OK evaluable={snap['evaluable']} "
        f"pipeline_proof={snap['pipeline_proof']} "
        f"outcome_season={snap['outcome_season']}"
    )


if __name__ == "__main__":
    main()
