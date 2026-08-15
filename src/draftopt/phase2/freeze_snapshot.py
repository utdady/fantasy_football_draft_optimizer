"""Freeze a decision-time snapshot from the live ingest DB into the eval DB.

P2.1 MVP: one boring preseason cut. Default freezes the current live ESPN
ADP/proj pull (with pulled_at as as_of). Prefer data/draftopt_eval.db.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.config import DB_PATH, EVAL_DB_PATH, SKILL_POSITIONS
from draftopt.phase2.leakage import assert_snapshot_clean
from draftopt.phase2.schema import migrate_eval_schema
import sqlite3


def _connect_eval(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_eval(conn: sqlite3.Connection) -> None:
    migrate_eval_schema(conn)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_only(iso: str) -> str:
    return (iso or "").strip()[:10]


def freeze_from_live(
    *,
    live_path: Path | None = None,
    eval_path: Path | None = None,
    snapshot_id: str | None = None,
    snapshot_date: str | None = None,
    season: int | None = None,
    label: str | None = None,
    notes: str | None = None,
    adp_source: str = "espn",
    proj_source: str = "espn",
    pipeline_proof: bool = True,
    evaluable: bool = False,
    outcome_season: int | None = None,
) -> dict:
    """
    Copy latest ADP + projections from live DB into eval_snapshot_* tables.

    as_of timestamps come from pulled_at on the source snapshot rows.

    Live freezes default to pipeline_proof=True, evaluable=False (current
    season has no realized outcomes yet). Do not flip evaluable without a
    completed outcome season and honest historical as_of stamps.
    """
    if evaluable and pipeline_proof:
        raise ValueError("snapshot cannot be both pipeline_proof and evaluable")
    if evaluable and outcome_season is None:
        raise ValueError("outcome_season required when evaluable=True")
    live = live_db.connect(live_path or DB_PATH)
    live_db.init(live)
    eval_conn = _connect_eval(eval_path or EVAL_DB_PATH)
    _init_eval(eval_conn)

    adp_pull = live.execute(
        "SELECT MAX(pulled_at) AS t FROM adp_snapshots WHERE source = ?",
        (adp_source,),
    ).fetchone()["t"]
    proj_pull = live.execute(
        "SELECT MAX(pulled_at) AS t FROM projections_snapshots WHERE source = ?",
        (proj_source,),
    ).fetchone()["t"]
    if not adp_pull or not proj_pull:
        live.close()
        eval_conn.close()
        raise RuntimeError(
            f"missing {adp_source} ADP or {proj_source} projections in live DB; "
            "run: python -m draftopt.ingest"
        )

    # Snapshot cutoff = later of the two pull dates (decision world as-of).
    snap_ts = max(adp_pull, proj_pull)
    snap_date = snapshot_date or _date_only(snap_ts)
    year = season or int(snap_date[:4])
    sid = snapshot_id or f"{year}-preseason-{snap_date}"
    snap_label = label or sid
    snap_notes = notes or (
        f"Frozen from live ingest DB. ADP {adp_source}@{adp_pull}; "
        f"proj {proj_source}@{proj_pull}. "
        + (
            "PIPELINE PROOF only — not evaluable (no realized outcomes)."
            if pipeline_proof
            else "Evaluation snapshot."
        )
    )

    # Latest ADP / proj per player for those pulls
    rows = live.execute(
        """
        SELECT
            p.player_id,
            p.name,
            p.position,
            p.team,
            a.adp,
            a.pulled_at AS adp_as_of,
            pr.season_points AS proj_ppr,
            pr.pulled_at AS proj_as_of
        FROM players p
        LEFT JOIN adp_snapshots a
            ON a.player_id = p.player_id
            AND a.source = ?
            AND a.pulled_at = ?
        LEFT JOIN projections_snapshots pr
            ON pr.player_id = p.player_id
            AND pr.source = ?
            AND pr.pulled_at = ?
        WHERE p.position IN ({pos})
        """.format(pos=",".join("?" * len(SKILL_POSITIONS))),
        (adp_source, adp_pull, proj_source, proj_pull, *SKILL_POSITIONS),
    ).fetchall()

    players: list[dict] = []
    for r in rows:
        # Keep players with at least ADP or projection (draftable signal).
        if r["adp"] is None and r["proj_ppr"] is None:
            continue
        # Leakage fields required — if one source missing, stamp as_of with
        # the available pull but leave value NULL (coverage validator will note).
        adp_as_of = r["adp_as_of"] or adp_pull
        proj_as_of = r["proj_as_of"] or proj_pull
        players.append(
            {
                "player_id": r["player_id"],
                "name": r["name"],
                "position": r["position"],
                "team": r["team"],
                "adp": r["adp"],
                "adp_source": adp_source if r["adp"] is not None else None,
                "adp_as_of": adp_as_of,
                "proj_ppr": r["proj_ppr"],
                "proj_source": proj_source if r["proj_ppr"] is not None else None,
                "proj_as_of": proj_as_of,
            }
        )

    assert_snapshot_clean(players, snapshot_id=sid, snapshot_date=snap_date)

    # Replace if re-freezing same id
    eval_conn.execute(
        "DELETE FROM eval_snapshot_players WHERE snapshot_id = ?", (sid,)
    )
    eval_conn.execute("DELETE FROM eval_snapshots WHERE snapshot_id = ?", (sid,))
    eval_conn.execute(
        """
        INSERT INTO eval_snapshots (
            snapshot_id, season, snapshot_date, label, notes, created_at,
            pipeline_proof, evaluable, outcome_season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sid,
            year,
            snap_date,
            snap_label,
            snap_notes,
            _utcnow(),
            1 if pipeline_proof else 0,
            1 if evaluable else 0,
            outcome_season,
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
                sid,
                p["player_id"],
                p["name"],
                p["position"],
                p["team"],
                p["adp"],
                p["adp_source"],
                p["adp_as_of"],
                p["proj_ppr"],
                p["proj_source"],
                p["proj_as_of"],
            )
            for p in players
        ],
    )
    eval_conn.commit()
    n = len(players)
    live.close()
    eval_conn.close()
    return {
        "snapshot_id": sid,
        "season": year,
        "snapshot_date": snap_date,
        "label": snap_label,
        "n_players": n,
        "pipeline_proof": bool(pipeline_proof),
        "evaluable": bool(evaluable),
        "outcome_season": outcome_season,
        "adp_pulled_at": adp_pull,
        "proj_pulled_at": proj_pull,
        "eval_db": str(eval_path or EVAL_DB_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P2.1: freeze a decision-time snapshot into draftopt_eval.db"
    )
    parser.add_argument("--live-db", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--snapshot-id", type=str, default=None)
    parser.add_argument("--snapshot-date", type=str, default=None)
    parser.add_argument("--season", type=int, default=None)
    parser.add_argument("--label", type=str, default=None)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("results/phase2_snapshot_p21.json"),
    )
    args = parser.parse_args()
    meta = freeze_from_live(
        live_path=args.live_db,
        eval_path=args.eval_db,
        snapshot_id=args.snapshot_id,
        snapshot_date=args.snapshot_date,
        season=args.season,
        label=args.label,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Froze snapshot {meta['snapshot_id']}: {meta['n_players']} players")
    print(f"  date={meta['snapshot_date']} season={meta['season']}")
    print(
        f"  pipeline_proof={meta['pipeline_proof']} "
        f"evaluable={meta['evaluable']}"
    )
    print(f"  eval_db={meta['eval_db']}")
    print(f"  wrote {args.out_json}")


if __name__ == "__main__":
    main()
