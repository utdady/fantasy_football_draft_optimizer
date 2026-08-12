from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

import httpx

from draftopt import db
from draftopt.config import HTTP_HEADERS, RAW_DIR, SKILL_POSITIONS
from draftopt.names import aliases_for
from draftopt.sources import dynastyprocess, espn, sleeper


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_pos(pos: str | None) -> str | None:
    if not pos:
        return None
    p = pos.upper()
    if p in {"DEF", "D/ST"}:
        return "DST"
    if p == "PK":
        return "K"
    return p


def _index(rows: list[dict], key: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        val = row.get(key)
        if val:
            out[str(val)] = row
    return out


def _pick(*vals: Any) -> Any:
    for v in vals:
        if v not in (None, ""):
            return v
    return None


def build_catalog(
    conn,
    sleeper_players: list[dict],
    dp_ids: list[dict],
    ecr_rows: list[dict],
    espn_players: list[dict],
    pulled_at: str,
) -> dict[str, int]:
    sleeper_by_id = _index(sleeper_players, "sleeper_id")
    sleeper_by_espn = _index(sleeper_players, "espn_id")
    dp_by_sleeper = _index(dp_ids, "sleeper_id")
    dp_by_espn = _index(dp_ids, "espn_id")
    dp_by_fp = _index(dp_ids, "fantasypros_id")
    ecr_by_fp = _index(ecr_rows, "fantasypros_id")
    espn_by_id = _index(espn_players, "espn_id")

    seeds: list[tuple[str | None, str | None, str | None]] = []
    seen_seed: set[tuple] = set()

    def add_seed(sleeper_id, espn_id, fp_id):
        key = (sleeper_id, espn_id, fp_id)
        if key in seen_seed:
            return
        seen_seed.add(key)
        seeds.append(key)

    for row in espn_players:
        dp = dp_by_espn.get(row["espn_id"], {})
        sl = sleeper_by_espn.get(row["espn_id"], {})
        add_seed(
            _pick(dp.get("sleeper_id"), sl.get("sleeper_id")),
            row["espn_id"],
            dp.get("fantasypros_id"),
        )
    for row in ecr_rows:
        dp = dp_by_fp.get(row.get("fantasypros_id") or "", {})
        add_seed(dp.get("sleeper_id"), dp.get("espn_id"), row.get("fantasypros_id"))

    merged: dict[str, dict] = {}
    for sleeper_id, espn_id, fp_id in seeds:
        sl = sleeper_by_id.get(sleeper_id or "") or sleeper_by_espn.get(espn_id or "") or {}
        dp = (
            dp_by_sleeper.get(sleeper_id or "")
            or dp_by_espn.get(espn_id or "")
            or dp_by_fp.get(fp_id or "")
            or {}
        )
        es = espn_by_id.get(espn_id or dp.get("espn_id") or sl.get("espn_id") or "") or {}
        ecr = ecr_by_fp.get(fp_id or dp.get("fantasypros_id") or "") or {}

        sleeper_id = _pick(sleeper_id, sl.get("sleeper_id"), dp.get("sleeper_id"))
        espn_id = _pick(espn_id, es.get("espn_id"), dp.get("espn_id"), sl.get("espn_id"))
        fp_id = _pick(fp_id, dp.get("fantasypros_id"), ecr.get("fantasypros_id"))

        if sleeper_id:
            player_id = str(sleeper_id)
        elif espn_id:
            player_id = f"espn:{espn_id}"
        elif fp_id:
            player_id = f"fp:{fp_id}"
        else:
            continue

        name = _pick(sl.get("name"), es.get("name"), ecr.get("name"), dp.get("name"))
        if not name:
            continue
        position = _norm_pos(
            _pick(sl.get("position"), es.get("position"), ecr.get("position"), dp.get("position"))
        )
        if position not in SKILL_POSITIONS:
            continue

        rec = {
            "player_id": player_id,
            "name": name,
            "position": position,
            "team": _pick(sl.get("team"), ecr.get("team"), dp.get("team"), es.get("team")),
            "bye": ecr.get("bye"),
            "status": sl.get("status"),
            "injury_status": _pick(sl.get("injury_status"), es.get("injury_status")),
            "sleeper_id": sleeper_id,
            "espn_id": espn_id,
            "fantasypros_id": fp_id,
            "adp_espn": es.get("adp"),
            "proj_espn": es.get("season_points"),
            "ecr": ecr.get("ecr"),
            "ecr_sd": ecr.get("sd"),
            "ecr_best": ecr.get("best"),
            "ecr_worst": ecr.get("worst"),
        }
        prev = merged.get(player_id)
        if prev:
            for k, v in rec.items():
                if prev.get(k) in (None, "") and v not in (None, ""):
                    prev[k] = v
        else:
            merged[player_id] = rec

    keep = {
        pid: rec
        for pid, rec in merged.items()
        if rec.get("adp_espn") is not None
        or rec.get("proj_espn") is not None
        or rec.get("ecr") is not None
    }

    conn.execute("DELETE FROM player_aliases")
    conn.execute("DELETE FROM adp_snapshots")
    conn.execute("DELETE FROM projections_snapshots")
    conn.execute("DELETE FROM rankings_snapshots")
    # Keep players that appear on existing drafts; upsert the rest.
    for rec in keep.values():
        conn.execute(
            """
            INSERT INTO players (
                player_id, name, position, team, bye, status, injury_status,
                sleeper_id, espn_id, fantasypros_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_id) DO UPDATE SET
                name=excluded.name,
                position=excluded.position,
                team=excluded.team,
                bye=excluded.bye,
                status=excluded.status,
                injury_status=excluded.injury_status,
                sleeper_id=excluded.sleeper_id,
                espn_id=excluded.espn_id,
                fantasypros_id=excluded.fantasypros_id,
                updated_at=excluded.updated_at
            """,
            (
                rec["player_id"],
                rec["name"],
                rec["position"],
                rec["team"],
                rec["bye"],
                rec["status"],
                rec["injury_status"],
                rec["sleeper_id"],
                rec["espn_id"],
                rec["fantasypros_id"],
                pulled_at,
            ),
        )
        for alias in aliases_for(rec["name"], rec["position"], rec["team"]):
            conn.execute(
                "INSERT OR IGNORE INTO player_aliases (player_id, alias) VALUES (?, ?)",
                (rec["player_id"], alias),
            )
        if rec.get("adp_espn") is not None:
            conn.execute(
                "INSERT INTO adp_snapshots (player_id, source, adp, pulled_at) VALUES (?, ?, ?, ?)",
                (rec["player_id"], "espn", rec["adp_espn"], pulled_at),
            )
        if rec.get("proj_espn") is not None:
            conn.execute(
                "INSERT INTO projections_snapshots (player_id, source, season_points, pulled_at) VALUES (?, ?, ?, ?)",
                (rec["player_id"], "espn", rec["proj_espn"], pulled_at),
            )
        if rec.get("ecr") is not None:
            conn.execute(
                """
                INSERT INTO rankings_snapshots (
                    player_id, source, ecr, sd, best, worst, pulled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec["player_id"],
                    "fantasypros",
                    rec["ecr"],
                    rec["ecr_sd"],
                    rec["ecr_best"],
                    rec["ecr_worst"],
                    pulled_at,
                ),
            )

    conn.commit()
    return {
        "players": len(keep),
        "adp": sum(1 for r in keep.values() if r.get("adp_espn") is not None),
        "proj": sum(1 for r in keep.values() if r.get("proj_espn") is not None),
        "ecr": sum(1 for r in keep.values() if r.get("ecr") is not None),
    }


def run_ingest(conn=None) -> dict[str, Any]:
    own = conn is None
    conn = conn or db.connect()
    db.init(conn)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pulled_at = _utcnow()
    client = httpx.Client(headers=HTTP_HEADERS, timeout=120, follow_redirects=True)
    stats: dict[str, Any] = {"pulled_at": pulled_at}
    try:
        sleeper_raw = sleeper.fetch(client)
        sleeper_path = sleeper.save_raw(sleeper_raw, pulled_at)
        sleeper_rows = sleeper.parse(sleeper_raw)
        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("sleeper", pulled_at, str(sleeper_path), len(sleeper_rows)),
        )

        ids_text = dynastyprocess.fetch_ids(client)
        ids_path = dynastyprocess.save_raw(ids_text, "ids", pulled_at)
        dp_ids = dynastyprocess.parse_ids(ids_text)
        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("dynastyprocess_ids", pulled_at, str(ids_path), len(dp_ids)),
        )

        ecr_text = dynastyprocess.fetch_ecr(client)
        ecr_path = dynastyprocess.save_raw(ecr_text, "ecr", pulled_at)
        ecr_rows = dynastyprocess.parse_ecr(ecr_text)
        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("dynastyprocess_ecr", pulled_at, str(ecr_path), len(ecr_rows)),
        )

        espn_raw = espn.fetch(client)
        espn_path = espn.save_raw(espn_raw, pulled_at)
        espn_rows = espn.parse(espn_raw)
        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("espn", pulled_at, str(espn_path), len(espn_rows)),
        )

        stats["join"] = build_catalog(conn, sleeper_rows, dp_ids, ecr_rows, espn_rows, pulled_at)
        stats["fetched"] = {
            "sleeper": len(sleeper_rows),
            "dp_ids": len(dp_ids),
            "ecr": len(ecr_rows),
            "espn": len(espn_rows),
        }
        conn.commit()
        return stats
    finally:
        client.close()
        if own:
            conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh V0 player snapshots")
    parser.parse_args()
    print("Ingesting Sleeper + DynastyProcess + ESPN...")
    stats = run_ingest()
    print(stats)


if __name__ == "__main__":
    main()
