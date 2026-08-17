"""FantasyPros live overlay — information beside TAKE, not into M.

Writes:
  rankings_snapshots source=fantasypros_api  (overall ECR from ALL page)
  projections_snapshots source=fantasypros   (PPR season points)

Does not modify ESPN projections used by `marginal`.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

import httpx

from draftopt import db
from draftopt.config import SEASON
from draftopt.draft.state import _drafted_ids
from draftopt.sources import fantasypros as fp


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def refresh_fp_overlay(conn=None, *, season: int = SEASON) -> dict[str, Any]:
    """Pull FP API rankings + projections into the live DB."""
    key = fp.api_key()
    if not key:
        return {"ok": False, "reason": "api_key_missing", "rankings": 0, "projections": 0}

    own = conn is None
    conn = conn or db.connect()
    db.init(conn)
    pulled_at = _utcnow()
    client = httpx.Client(timeout=60, follow_redirects=True)
    try:
        rank_bundle = fp.fetch_consensus_bundle(client, api_key=key, season=season)
        proj_bundle = fp.fetch_projections_bundle(client, api_key=key, season=season)
        rank_path = fp.save_raw(rank_bundle, "rankings", pulled_at)
        proj_path = fp.save_raw(proj_bundle, "projections", pulled_at)

        rankings = fp.parse_overall_rankings(rank_bundle)
        projections = fp.parse_projections(proj_bundle)

        by_fp = {
            str(r["fantasypros_id"]): r["player_id"]
            for r in conn.execute(
                "SELECT player_id, fantasypros_id FROM players WHERE fantasypros_id IS NOT NULL"
            ).fetchall()
        }

        conn.execute(
            "DELETE FROM rankings_snapshots WHERE source = ?",
            (fp.SOURCE_RANKINGS,),
        )
        conn.execute(
            "DELETE FROM projections_snapshots WHERE source = ?",
            (fp.SOURCE_PROJECTIONS,),
        )

        n_rank = 0
        unmatched_rank = 0
        for row in rankings:
            pid = by_fp.get(row["fantasypros_id"])
            if not pid:
                unmatched_rank += 1
                continue
            conn.execute(
                """
                INSERT INTO rankings_snapshots (
                    player_id, source, ecr, sd, best, worst, pulled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    fp.SOURCE_RANKINGS,
                    row["ecr"],
                    row.get("ecr_sd"),
                    row.get("ecr_best"),
                    row.get("ecr_worst"),
                    pulled_at,
                ),
            )
            n_rank += 1

        n_proj = 0
        unmatched_proj = 0
        for row in projections:
            pid = by_fp.get(row["fantasypros_id"])
            if not pid:
                unmatched_proj += 1
                continue
            conn.execute(
                """
                INSERT INTO projections_snapshots (
                    player_id, source, season_points, pulled_at
                ) VALUES (?, ?, ?, ?)
                """,
                (pid, fp.SOURCE_PROJECTIONS, row["season_points"], pulled_at),
            )
            n_proj += 1

        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("fantasypros_rankings", pulled_at, str(rank_path), n_rank),
        )
        conn.execute(
            "INSERT INTO ingest_runs (source, pulled_at, raw_path, n_rows) VALUES (?, ?, ?, ?)",
            ("fantasypros_projections", pulled_at, str(proj_path), n_proj),
        )
        conn.commit()

        all_page = (rank_bundle.get("pages") or {}).get("ALL") or {}
        return {
            "ok": True,
            "pulled_at": pulled_at,
            "season": season,
            "rankings": n_rank,
            "projections": n_proj,
            "unmatched_rankings": unmatched_rank,
            "unmatched_projections": unmatched_proj,
            "fp_last_updated": all_page.get("last_updated"),
            "public_api_limited": bool(all_page.get("public_api_limited")),
            "disclaimer": "Overlay only — does not change TAKE / marginal.",
        }
    finally:
        client.close()
        if own:
            conn.close()


def build_overlay(conn, draft_id: str, recommend: list[dict] | None = None) -> dict[str, Any]:
    """Attach FP API consensus + proj next to recommendations (read-only)."""
    drafted = _drafted_ids(conn, draft_id)
    meta = conn.execute(
        """
        SELECT pulled_at FROM rankings_snapshots
        WHERE source = ?
        ORDER BY id DESC LIMIT 1
        """,
        (fp.SOURCE_RANKINGS,),
    ).fetchone()
    pulled_at = meta["pulled_at"] if meta else None

    fp_map: dict[str, dict] = {}
    rows = conn.execute(
        """
        SELECT p.player_id, p.name, p.position, p.team,
               r.ecr AS fp_ecr, r.sd AS fp_sd, r.best AS fp_best, r.worst AS fp_worst,
               pr.season_points AS fp_proj
        FROM players p
        LEFT JOIN rankings_snapshots r
            ON r.player_id = p.player_id AND r.source = ?
        LEFT JOIN projections_snapshots pr
            ON pr.player_id = p.player_id AND pr.source = ?
        WHERE r.ecr IS NOT NULL OR pr.season_points IS NOT NULL
        """,
        (fp.SOURCE_RANKINGS, fp.SOURCE_PROJECTIONS),
    ).fetchall()
    for row in rows:
        fp_map[row["player_id"]] = dict(row)

    remaining_fp = [
        {
            "player_id": r["player_id"],
            "name": r["name"],
            "position": r["position"],
            "team": r["team"],
            "fp_ecr": r["fp_ecr"],
            "fp_proj": r["fp_proj"],
        }
        for r in fp_map.values()
        if r["player_id"] not in drafted and r.get("fp_ecr") is not None
    ]
    remaining_fp.sort(key=lambda x: (x["fp_ecr"] is None, x["fp_ecr"] if x["fp_ecr"] is not None else 9999))

    enriched = []
    for rec in recommend or []:
        pid = rec.get("player_id")
        info = fp_map.get(pid) or {}
        enriched.append(
            {
                "player_id": pid,
                "name": rec.get("name"),
                "marginal": rec.get("marginal"),
                "adp_espn": rec.get("adp_espn"),
                "ecr_fp_ppr": rec.get("ecr_fp_ppr"),
                "proj_espn": rec.get("proj_espn") or rec.get("season_points"),
                "fp_ecr": info.get("fp_ecr"),
                "fp_proj": info.get("fp_proj"),
                "fp_sd": info.get("fp_sd"),
            }
        )

    take_id = (recommend or [{}])[0].get("player_id") if recommend else None
    fp_top_id = remaining_fp[0]["player_id"] if remaining_fp else None
    diverge = bool(take_id and fp_top_id and take_id != fp_top_id)

    return {
        "source": "fantasypros_api",
        "role": "overlay",
        "pulled_at": pulled_at,
        "available": bool(fp_map),
        "n_ranked_remaining": len(remaining_fp),
        "top_remaining": remaining_fp[:5],
        "recommend": enriched,
        "take_vs_fp": {
            "diverge": diverge,
            "take_player_id": take_id,
            "fp_top_player_id": fp_top_id,
            "fp_top_name": remaining_fp[0]["name"] if remaining_fp else None,
            "note": (
                f"FP consensus prefers {remaining_fp[0]['name']} among remaining (ECR {remaining_fp[0]['fp_ecr']})"
                if diverge and remaining_fp
                else None
            ),
        },
        "disclaimer": (
            "FantasyPros live overlay (free-tier top overall). "
            "Does not change TAKE. marginal still uses ESPN projections only."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh FantasyPros overlay (not TAKE)")
    parser.add_argument("--season", type=int, default=SEASON)
    args = parser.parse_args()
    stats = refresh_fp_overlay(season=args.season)
    print(json.dumps(stats, indent=2))
    return 0 if stats.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
