"""FantasyPros public API (live consensus + projections).

Free-tier responses are capped (~10 players per request). Used as an
information overlay beside TAKE — never as the `marginal` value source.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from draftopt.config import RAW_DIR, SEASON
from draftopt.envfile import load_dotenv

RANKINGS_URL = "https://api.fantasypros.com/public/v2/json/nfl/{season}/consensus-rankings"
PROJECTIONS_URL = "https://api.fantasypros.com/public/v2/json/nfl/{season}/projections"

RANK_POSITIONS = ("ALL", "QB", "RB", "WR", "TE", "DST", "K")
PROJ_POSITIONS = ("QB", "RB", "WR", "TE", "DST", "K")

SOURCE_RANKINGS = "fantasypros_api"
SOURCE_PROJECTIONS = "fantasypros"


def api_key() -> str:
    load_dotenv()
    return (os.environ.get("FANTASYPROS_API_KEY") or os.environ.get("FP_API_KEY") or "").strip()


def _headers(key: str) -> dict[str, str]:
    return {
        "x-api-key": key,
        "Accept": "application/json",
        "User-Agent": "draftopt/0.1 (personal; FP overlay)",
    }


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_raw(payload: Any, kind: str, pulled_at: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = pulled_at.replace(":", "").replace("-", "")
    path = RAW_DIR / f"fantasypros_{kind}_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def fetch_consensus_bundle(
    client: httpx.Client,
    *,
    api_key: str,
    season: int = SEASON,
    scoring: str = "PPR",
) -> dict[str, Any]:
    """Fetch ALL (overall ECR) plus per-position pages. Free tier ≈10 each."""
    pages: dict[str, Any] = {}
    for pos in RANK_POSITIONS:
        url = RANKINGS_URL.format(season=season)
        r = client.get(
            url,
            headers=_headers(api_key),
            params={"type": "draft", "scoring": scoring, "position": pos},
            timeout=60,
        )
        r.raise_for_status()
        pages[pos] = r.json()
    return {
        "season": season,
        "scoring": scoring,
        "pulled_at": _utcnow(),
        "pages": pages,
    }


def fetch_projections_bundle(
    client: httpx.Client,
    *,
    api_key: str,
    season: int = SEASON,
    scoring: str = "PPR",
) -> dict[str, Any]:
    pages: dict[str, Any] = {}
    for pos in PROJ_POSITIONS:
        url = PROJECTIONS_URL.format(season=season)
        r = client.get(
            url,
            headers=_headers(api_key),
            params={"week": 0, "scoring": scoring, "position": pos},
            timeout=60,
        )
        r.raise_for_status()
        pages[pos] = r.json()
    return {
        "season": season,
        "scoring": scoring,
        "pulled_at": _utcnow(),
        "pages": pages,
    }


def parse_overall_rankings(bundle: dict[str, Any]) -> list[dict]:
    """Overall ECR from the ALL page only (do not mix with positional ECR)."""
    page = (bundle.get("pages") or {}).get("ALL") or {}
    out: list[dict] = []
    for p in page.get("players") or []:
        fp_id = p.get("player_id")
        if fp_id is None:
            continue
        ecr = p.get("rank_ecr")
        if ecr is None:
            continue
        try:
            ecr_f = float(ecr)
        except (TypeError, ValueError):
            continue
        sd = _float_or_none(p.get("rank_std"))
        best = _int_or_none(p.get("rank_min"))
        worst = _int_or_none(p.get("rank_max"))
        out.append(
            {
                "fantasypros_id": str(fp_id),
                "name": p.get("player_name"),
                "position": _norm_pos(p.get("player_position_id")),
                "team": p.get("player_team_id"),
                "ecr": ecr_f,
                "ecr_sd": sd,
                "ecr_best": best,
                "ecr_worst": worst,
                "tier": p.get("tier"),
                "pos_rank": p.get("pos_rank"),
                "last_updated": page.get("last_updated"),
                "last_updated_ts": page.get("last_updated_ts"),
            }
        )
    return out


def parse_projections(bundle: dict[str, Any]) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for pos, page in (bundle.get("pages") or {}).items():
        players = page.get("players") or page.get("projections") or []
        if not players and isinstance(page, dict):
            for v in page.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and (
                    "fpid" in v[0] or "name" in v[0]
                ):
                    players = v
                    break
        for p in players:
            fp_id = p.get("fpid") or p.get("player_id")
            if fp_id is None:
                continue
            key = str(fp_id)
            if key in seen:
                continue
            stats = p.get("stats") or {}
            pts = stats.get("points_ppr")
            if pts is None:
                pts = stats.get("points")
            if pts is None:
                continue
            try:
                pts_f = float(pts)
            except (TypeError, ValueError):
                continue
            seen.add(key)
            out.append(
                {
                    "fantasypros_id": key,
                    "name": p.get("name") or p.get("player_name"),
                    "position": _norm_pos(p.get("position_id") or p.get("player_position_id") or pos),
                    "team": p.get("team_id") or p.get("player_team_id"),
                    "season_points": pts_f,
                }
            )
    return out


def _norm_pos(pos: str | None) -> str | None:
    if not pos:
        return None
    p = str(pos).upper()
    if p in {"DEF", "D/ST"}:
        return "DST"
    if p == "PK":
        return "K"
    return p


def _float_or_none(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _int_or_none(v: Any) -> int | None:
    f = _float_or_none(v)
    return int(f) if f is not None else None
