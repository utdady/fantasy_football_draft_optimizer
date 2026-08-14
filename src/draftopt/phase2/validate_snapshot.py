"""Validate a Phase 2 decision-time snapshot (P2.1 / P2.3 gate)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from draftopt.config import EVAL_DB_PATH, SKILL_POSITIONS
from draftopt.phase2.leakage import validate_snapshot_table
from draftopt.phase2.schema import EVAL_SCHEMA
import sqlite3


def _connect_eval(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_eval(conn: sqlite3.Connection) -> None:
    conn.executescript(EVAL_SCHEMA)
    conn.commit()

# Coverage bars for a usable draft pool (skill positions with signal).
MIN_PLAYERS = 200
MIN_ADP_COVERAGE = 0.70  # fraction of snapshot rows with ADP
MIN_PROJ_COVERAGE = 0.70
MIN_BOTH_COVERAGE = 0.60
REQUIRED_POS = ("QB", "RB", "WR", "TE", "DST")


def validate_snapshot(
    snapshot_id: str,
    *,
    eval_path: Path | None = None,
) -> dict:
    conn = _connect_eval(eval_path or EVAL_DB_PATH)
    _init_eval(conn)
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})

    snap = conn.execute(
        "SELECT * FROM eval_snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if snap is None:
        conn.close()
        return {
            "snapshot_id": snapshot_id,
            "ok": False,
            "checks": [
                {
                    "check": "snapshot_exists",
                    "ok": False,
                    "detail": f"unknown snapshot_id={snapshot_id}",
                }
            ],
        }

    add(
        "snapshot_date_valid",
        bool(snap["snapshot_date"] and len(snap["snapshot_date"]) >= 10),
        f"snapshot_date={snap['snapshot_date']} season={snap['season']}",
    )

    rows = conn.execute(
        "SELECT * FROM eval_snapshot_players WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchall()
    n = len(rows)
    add("player_count", n >= MIN_PLAYERS, f"n={n} (min {MIN_PLAYERS})")

    ids = [r["player_id"] for r in rows]
    add(
        "player_ids_unique",
        len(ids) == len(set(ids)),
        f"n={n} unique={len(set(ids))}",
    )

    bad_pos = [
        r["player_id"]
        for r in rows
        if (r["position"] or "") not in SKILL_POSITIONS
    ]
    add(
        "positions_valid",
        len(bad_pos) == 0,
        f"invalid={len(bad_pos)}" + (f" e.g. {bad_pos[:3]}" if bad_pos else ""),
    )

    pos_counts = Counter(r["position"] for r in rows)
    missing_pos = [p for p in REQUIRED_POS if pos_counts.get(p, 0) == 0]
    add(
        "required_positions_present",
        len(missing_pos) == 0,
        f"counts={dict(pos_counts)} missing={missing_pos}",
    )

    n_adp = sum(1 for r in rows if r["adp"] is not None)
    n_proj = sum(1 for r in rows if r["proj_ppr"] is not None)
    n_both = sum(
        1 for r in rows if r["adp"] is not None and r["proj_ppr"] is not None
    )
    adp_cov = n_adp / n if n else 0.0
    proj_cov = n_proj / n if n else 0.0
    both_cov = n_both / n if n else 0.0
    add(
        "adp_coverage",
        adp_cov >= MIN_ADP_COVERAGE,
        f"{adp_cov:.1%} ({n_adp}/{n}; min {MIN_ADP_COVERAGE:.0%})",
    )
    add(
        "projection_coverage",
        proj_cov >= MIN_PROJ_COVERAGE,
        f"{proj_cov:.1%} ({n_proj}/{n}; min {MIN_PROJ_COVERAGE:.0%})",
    )
    add(
        "adp_and_proj_coverage",
        both_cov >= MIN_BOTH_COVERAGE,
        f"{both_cov:.1%} ({n_both}/{n}; min {MIN_BOTH_COVERAGE:.0%})",
    )

    findings = validate_snapshot_table(conn, snapshot_id)
    add(
        "no_post_snapshot_records",
        len(findings) == 0,
        f"leakage_findings={len(findings)}"
        + (
            f" e.g. {findings[0].player_id}/{findings[0].field}"
            if findings
            else ""
        ),
    )

    # Provenance: every row has as_of stamps
    missing_as_of = sum(
        1
        for r in rows
        if not r["adp_as_of"] or not r["proj_as_of"]
    )
    add(
        "provenance_as_of_present",
        missing_as_of == 0,
        f"missing_as_of_rows={missing_as_of}",
    )

    # Reproducibility: metadata present
    add(
        "snapshot_reproducible_meta",
        bool(snap["label"] and snap["created_at"] and snap["notes"]),
        f"label={snap['label']!r} created_at={snap['created_at']}",
    )

    conn.close()
    ok = all(c["ok"] for c in checks)
    return {
        "snapshot_id": snapshot_id,
        "season": snap["season"],
        "snapshot_date": snap["snapshot_date"],
        "label": snap["label"],
        "n_players": n,
        "ok": ok,
        "checks": checks,
    }


def to_markdown(report: dict) -> str:
    lines = [
        f"# Snapshot validation: `{report['snapshot_id']}`",
        "",
        f"- season: **{report.get('season')}**",
        f"- snapshot_date: **{report.get('snapshot_date')}**",
        f"- players: **{report.get('n_players')}**",
        f"- overall: **{'PASS' if report.get('ok') else 'FAIL'}**",
        "",
        "| check | ok | detail |",
        "| --- | --- | --- |",
    ]
    for c in report.get("checks") or []:
        mark = "✓" if c["ok"] else "✗"
        lines.append(f"| {c['check']} | {mark} | {c['detail']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a Phase 2 decision-time snapshot"
    )
    parser.add_argument("snapshot_id", type=str)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write markdown report (default results/phase2_validate_<id>.md)",
    )
    args = parser.parse_args()
    report = validate_snapshot(args.snapshot_id, eval_path=args.eval_db)
    out = args.out or Path(f"results/phase2_validate_{args.snapshot_id}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for c in report["checks"]:
        mark = "✓" if c["ok"] else "✗"
        print(f"{mark} {c['check']}: {c['detail']}")
    print(f"Wrote {out}")
    if not report["ok"]:
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
