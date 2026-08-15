"""Set pipeline_proof / evaluable flags on an existing eval snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt.config import EVAL_DB_PATH
from draftopt.phase2.evaluable import get_snapshot_meta, set_snapshot_flags
from draftopt.phase2.schema import migrate_eval_schema
import sqlite3


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mark a Phase 2 snapshot as pipeline_proof and/or evaluable"
    )
    parser.add_argument("snapshot_id", type=str)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument(
        "--pipeline-proof",
        type=int,
        choices=(0, 1),
        required=True,
        help="1 = ingest/leakage proof only; not for actual-points claims",
    )
    parser.add_argument(
        "--evaluable",
        type=int,
        choices=(0, 1),
        required=True,
        help="1 = may be used by replay/scoring runners",
    )
    parser.add_argument(
        "--outcome-season",
        type=int,
        default=None,
        help="Season year whose actual PPR will score this snapshot",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
    )
    args = parser.parse_args()
    if args.evaluable == 1 and args.pipeline_proof == 1:
        raise SystemExit(
            "refuse: a snapshot cannot be both pipeline_proof=1 and evaluable=1"
        )
    if args.evaluable == 1 and args.outcome_season is None:
        raise SystemExit("--outcome-season is required when --evaluable 1")

    path = args.eval_db or EVAL_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate_eval_schema(conn)
    set_snapshot_flags(
        conn,
        args.snapshot_id,
        pipeline_proof=bool(args.pipeline_proof),
        evaluable=bool(args.evaluable),
        outcome_season=args.outcome_season,
    )
    snap = get_snapshot_meta(conn, args.snapshot_id)
    conn.close()
    assert snap is not None
    meta = {
        "snapshot_id": snap["snapshot_id"],
        "season": snap["season"],
        "snapshot_date": snap["snapshot_date"],
        "pipeline_proof": int(snap["pipeline_proof"]),
        "evaluable": int(snap["evaluable"]),
        "outcome_season": snap["outcome_season"],
    }
    print(json.dumps(meta, indent=2))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
