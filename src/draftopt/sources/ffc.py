"""Fantasy Football Calculator ADP API (historical + current).

Attribution: https://fantasyfootballcalculator.com/ (free API; link back).

Cloudflare may 403 automated clients — prefer a saved raw JSON for reproducibility.
Historical responses include meta.start_date / meta.end_date (draft window), not
always a single freeze timestamp. Provenance helpers refuse undated payloads.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from draftopt.config import HTTP_HEADERS, RAW_DIR

FFC_ADP_URL = "https://fantasyfootballcalculator.com/api/v1/adp/{scoring}"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def adp_url(
    *,
    year: int,
    teams: int = 10,
    scoring: str = "ppr",
    position: str = "all",
) -> str:
    return (
        f"{FFC_ADP_URL.format(scoring=scoring)}"
        f"?teams={teams}&year={year}&position={position}"
    )


def fetch_adp(
    *,
    year: int,
    teams: int = 10,
    scoring: str = "ppr",
    position: str = "all",
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    url = adp_url(year=year, teams=teams, scoring=scoring, position=position)
    headers = {
        **HTTP_HEADERS,
        "User-Agent": (
            "draftopt/0.1 (personal redraft research; "
            "+https://github.com/utdady/fantasy_football_draft_optimizer)"
        ),
        "Referer": "https://fantasyfootballcalculator.com/",
    }
    own = client is None
    client = client or httpx.Client(headers=headers, timeout=60, follow_redirects=True)
    try:
        resp = client.get(url)
        if resp.status_code == 403:
            raise RuntimeError(
                "FFC ADP API returned 403 (likely Cloudflare). "
                "Save JSON via browser and pass --raw-json."
            )
        resp.raise_for_status()
        return resp.json()
    finally:
        if own:
            client.close()


def load_adp_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_raw(payload: dict[str, Any], *, year: int, teams: int, pulled_at: str | None = None) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = (pulled_at or _utcnow()).replace(":", "")
    path = RAW_DIR / f"ffc_adp_ppr_{teams}tm_{year}_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _norm_pos(pos: str | None) -> str | None:
    if not pos:
        return None
    p = pos.upper()
    if p in {"DEF", "D/ST", "DST"}:
        return "DST"
    if p in {"PK", "K"}:
        return "K"
    return p


def parse_adp_players(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in payload.get("players") or []:
        ffc_id = raw.get("player_id")
        if ffc_id is None:
            continue
        rows.append(
            {
                "ffc_player_id": str(ffc_id),
                "name": (raw.get("name") or "").strip(),
                "position": _norm_pos(raw.get("position")),
                "team": (raw.get("team") or "").strip() or None,
                "adp": float(raw["adp"]) if raw.get("adp") is not None else None,
                "times_drafted": raw.get("times_drafted"),
                "bye": raw.get("bye"),
            }
        )
    return rows


def extract_provenance(
    payload: dict[str, Any],
    *,
    requested_year: int,
    requested_teams: int,
) -> dict[str, Any]:
    """
    Interpret FFC meta for leakage-safe as_of.

    FFC exposes a draft window (start_date/end_date), not a single freeze clock.
    We treat end_date as the conservative as_of (latest day contributing to ADP).
    """
    meta = payload.get("meta") or {}
    start = (meta.get("start_date") or "").strip()[:10] or None
    end = (meta.get("end_date") or "").strip()[:10] or None
    meta_teams = meta.get("teams")
    try:
        meta_teams_i = int(meta_teams) if meta_teams is not None else None
    except (TypeError, ValueError):
        meta_teams_i = None

    dated = bool(start and end and len(start) == 10 and len(end) == 10)
    teams_ok = meta_teams_i == requested_teams
    as_of = end if dated else None

    if not dated:
        gate = "fail"
        reason = "adp_as_of_unverified"
    elif not teams_ok:
        gate = "fail"
        reason = "adp_league_size_mismatch"
    else:
        gate = "pass"
        reason = None

    return {
        "gate": gate,
        "reason": reason,
        "requested_year": requested_year,
        "requested_teams": requested_teams,
        "meta_type": meta.get("type"),
        "meta_teams": meta_teams_i,
        "meta_rounds": meta.get("rounds"),
        "total_drafts": meta.get("total_drafts"),
        "start_date": start,
        "end_date": end,
        "as_of": as_of,
        "as_of_interpretation": (
            "FFC meta.end_date (upper bound of draft window in meta); "
            "ADP is an aggregate over [start_date, end_date], not a single pick clock."
            if dated
            else None
        ),
        "n_players": len(payload.get("players") or []),
    }
