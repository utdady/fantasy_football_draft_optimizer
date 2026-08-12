from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from draftopt.config import HTTP_HEADERS, RAW_DIR, SLEEPER_PLAYERS_URL

FANTASY_POS = {"QB", "RB", "WR", "TE", "K", "DEF", "DST"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(client: httpx.Client | None = None) -> dict:
    own = client is None
    client = client or httpx.Client(headers=HTTP_HEADERS, timeout=120)
    try:
        resp = client.get(SLEEPER_PLAYERS_URL)
        resp.raise_for_status()
        return resp.json()
    finally:
        if own:
            client.close()


def save_raw(payload: dict, pulled_at: str | None = None) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = (pulled_at or _utcnow()).replace(":", "")
    path = RAW_DIR / f"sleeper_players_{stamp}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def parse(payload: dict) -> list[dict]:
    rows = []
    for sleeper_id, p in payload.items():
        if not isinstance(p, dict):
            continue
        pos = (p.get("position") or "").upper()
        fantasy = {(x or "").upper() for x in (p.get("fantasy_positions") or [])}
        if pos not in FANTASY_POS and not (fantasy & FANTASY_POS):
            continue
        if pos == "DEF":
            pos = "DST"
        first = p.get("first_name") or ""
        last = p.get("last_name") or ""
        name = f"{first} {last}".strip() or p.get("full_name") or sleeper_id
        espn_id = p.get("espn_id")
        rows.append(
            {
                "sleeper_id": str(sleeper_id),
                "espn_id": str(espn_id) if espn_id not in (None, "") else None,
                "name": name,
                "first_name": first,
                "last_name": last,
                "position": pos if pos in FANTASY_POS or pos == "DST" else next(iter(fantasy), None),
                "team": p.get("team"),
                "status": p.get("status"),
                "injury_status": p.get("injury_status"),
                "active": bool(p.get("active", p.get("status") == "Active")),
            }
        )
    return rows
