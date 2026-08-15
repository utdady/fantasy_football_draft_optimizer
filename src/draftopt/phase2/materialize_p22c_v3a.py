"""Materialize P2.2C V3-A decision DB: same FFC ADP, calibrated season_points.

Separate from draftopt_p22c.db so adp_structural (linear curve) stays frozen.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.config import DATA_DIR, EVAL_DB_PATH
from draftopt.phase2 import connect_eval
from draftopt.phase2.leakage import assert_snapshot_clean
from draftopt.phase2.map_players import load_id_crosswalk, map_ffc_players, persist_mapping
from draftopt.phase2.schema import migrate_eval_schema
from draftopt.phase2.v3a_calibration import (
    CURVE_ID,
    DEFAULT_ARTIFACT,
    CalibrationMap,
    curve_meta,
)
from draftopt.sources import ffc

P22C_V3A_DB_PATH = DATA_DIR / "draftopt_p22c_v3a.db"
SNAPSHOT_ID = "2024-preseason-2024-09-01-ffc12-v3a"
DEFAULT_RAW = Path("data/raw/ffc_adp_ppr_12tm_2024.json")


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def materialize(
    *,
    raw_json: Path | None = None,
    eval_path: Path | None = None,
    draft_db: Path | None = None,
    calibration_path: Path | None = None,
) -> dict:
    raw_path = raw_json or DEFAULT_RAW
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"missing FFC JSON {raw_path}; save 2024 ADP JSON under data/raw/"
        )
    cal = CalibrationMap.load(calibration_path or DEFAULT_ARTIFACT)
    if cal.curve_id != CURVE_ID:
        raise RuntimeError(f"unexpected curve_id {cal.curve_id}")

    payload = ffc.load_adp_json(raw_path)
    provenance = ffc.extract_provenance(
        payload, requested_year=2024, requested_teams=12
    )
    if provenance["gate"] != "pass":
        raise RuntimeError(
            f"FFC provenance gate failed: {provenance.get('reason')} ({provenance})"
        )
    as_of = provenance["as_of"]
    assert as_of

    players = ffc.parse_adp_players(payload)
    crosswalk = load_id_crosswalk()
    mapping = map_ffc_players(players, crosswalk)
    by_ffc = {m["source_player_id"]: m for m in mapping["mapped"]}

    eval_path = eval_path or EVAL_DB_PATH
    eval_conn = connect_eval(eval_path)
    migrate_eval_schema(eval_conn)
    persist_mapping(eval_conn, mapping)

    snap_rows: list[dict] = []
    n_valued = 0
    for p in players:
        m = by_ffc.get(str(p["ffc_player_id"]))
        pid = m["player_id"] if m else f"ffc:{p['ffc_player_id']}"
        adp = p.get("adp")
        pos = p.get("position")
        v = cal.value(adp, pos)
        if v is not None:
            n_valued += 1
        snap_rows.append(
            {
                "player_id": pid,
                "name": p.get("name"),
                "position": pos,
                "team": p.get("team"),
                "adp": adp,
                "adp_source": "ffc",
                "adp_as_of": as_of,
                "proj_ppr": v,
                "proj_source": CURVE_ID,
                "proj_as_of": as_of,
            }
        )
    assert_snapshot_clean(snap_rows, snapshot_id=SNAPSHOT_ID, snapshot_date=as_of)

    notes = (
        f"P2.2C V3-A calibrated decision world. FFC 12-team PPR; as_of={as_of}; "
        f"curve={CURVE_ID}. Same ADP as structural; values = train 2021–2023 map. "
        f"evaluable=0. Raw={raw_path}"
    )
    eval_conn.execute(
        "DELETE FROM eval_snapshot_players WHERE snapshot_id = ?", (SNAPSHOT_ID,)
    )
    eval_conn.execute("DELETE FROM eval_snapshots WHERE snapshot_id = ?", (SNAPSHOT_ID,))
    eval_conn.execute(
        """
        INSERT INTO eval_snapshots (
            snapshot_id, season, snapshot_date, label, notes, created_at,
            pipeline_proof, evaluable, outcome_season,
            validation_status, validation_reason
        ) VALUES (?, 2024, ?, ?, ?, ?, 0, 0, 2024, ?, ?)
        """,
        (
            SNAPSHOT_ID,
            as_of,
            SNAPSHOT_ID,
            notes,
            _utcnow(),
            "source_validation",
            "historical_projection_missing",
        ),
    )
    eval_conn.executemany(
        """
        INSERT INTO eval_snapshot_players (
            snapshot_id, player_id, name, position, team,
            adp, adp_source, adp_as_of,
            proj_ppr, proj_source, proj_as_of
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                SNAPSHOT_ID,
                r["player_id"],
                r["name"],
                r["position"],
                r["team"],
                r["adp"],
                r["adp_source"],
                r["adp_as_of"],
                r["proj_ppr"],
                r["proj_source"],
                r["proj_as_of"],
            )
            for r in snap_rows
        ],
    )
    eval_conn.commit()

    draft_path = draft_db or P22C_V3A_DB_PATH
    if draft_path.exists():
        draft_path.unlink()
    conn = live_db.connect(draft_path)
    live_db.init(conn)
    pulled = as_of + "T00:00:00Z"
    for r in snap_rows:
        conn.execute(
            """
            INSERT INTO players (
                player_id, name, position, team, bye, status, injury_status,
                sleeper_id, espn_id, fantasypros_id, updated_at
            ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, ?)
            """,
            (
                r["player_id"],
                r["name"] or r["player_id"],
                r["position"],
                r["team"],
                pulled,
            ),
        )
        if r["adp"] is not None:
            conn.execute(
                "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES (?, 'espn', ?, ?)",
                (r["player_id"], r["adp"], pulled),
            )
        if r["proj_ppr"] is not None:
            conn.execute(
                """
                INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at)
                VALUES (?, 'espn', ?, ?)
                """,
                (r["player_id"], r["proj_ppr"], pulled),
            )
    conn.commit()
    n = len(snap_rows)
    conn.close()
    eval_conn.close()

    return {
        "snapshot_id": SNAPSHOT_ID,
        "evaluable": 0,
        "pipeline_proof": 0,
        "validation_status": "source_validation",
        "validation_reason": "historical_projection_missing",
        "as_of": as_of,
        "n_players": n,
        "n_valued": n_valued,
        "n_mapped": mapping["n_mapped"],
        "n_unresolved": mapping["n_unresolved"],
        "mapping_coverage": mapping["coverage"],
        "curve": curve_meta(cal.artifact),
        "calibration_path": str(calibration_path or DEFAULT_ARTIFACT),
        "provenance": provenance,
        "eval_db": str(eval_path),
        "draft_db": str(draft_path),
        "raw_json": str(raw_path),
        "alias_note": (
            "draft_db adp_snapshots/projections_snapshots use source='espn' as a "
            "plumbing alias for FFC ADP + V3-A calibrated values; reports must label FFC."
        ),
        "parent_structural_db": "data/draftopt_p22c.db (unchanged)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C V3-A materialize")
    parser.add_argument("--raw-json", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--calibration", type=Path, default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_v3a_materialize.md"),
    )
    args = parser.parse_args()
    report = materialize(
        raw_json=args.raw_json,
        eval_path=args.eval_db,
        draft_db=args.draft_db,
        calibration_path=args.calibration,
    )
    md = [
        "# P2.2C V3-A materialize",
        "",
        f"- snapshot_id: `{report['snapshot_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- as_of: `{report['as_of']}`",
        f"- players: {report['n_players']} (valued: {report['n_valued']})",
        f"- mapped: {report['n_mapped']} ({report['mapping_coverage']:.1%})",
        f"- curve: `{report['curve']['curve_id']}`",
        f"- calibration: `{report['calibration_path']}`",
        f"- draft_db: `{report['draft_db']}`",
        f"- parent structural DB: `{report['parent_structural_db']}`",
        "",
        report["alias_note"],
        "",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n".join(md))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
