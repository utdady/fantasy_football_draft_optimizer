from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from draftopt.config import (
    ESPN_PLAYER_LIMIT,
    ESPN_PLAYERS_URL,
    HTTP_HEADERS,
    RAW_DIR,
    SEASON,
)

POSITION_BY_ID = {
    1: "QB",
    2: "RB",
    3: "WR",
    4: "TE",
    5: "K",
    16: "DST",
}

PRO_TEAM_BY_ID = {
    0: None,
    1: "ATL",
    2: "BUF",
    3: "CHI",
    4: "CIN",
    5: "CLE",
    6: "DAL",
    7: "DEN",
    8: "DET",
    9: "GB",
    10: "TEN",
    11: "IND",
    12: "KC",
    13: "LV",
    14: "LAR",
    15: "MIA",
    16: "MIN",
    17: "NE",
    18: "NO",
    19: "NYG",
    20: "NYJ",
    21: "PHI",
    22: "ARI",
    23: "PIT",
    24: "LAC",
    25: "SF",
    26: "SEA",
    27: "TB",
    28: "WAS",
    29: "CAR",
    30: "JAX",
    33: "BAL",
    34: "HOU",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(client: httpx.Client | None = None, limit: int = ESPN_PLAYER_LIMIT) -> dict:
    own = client is None
    headers = {
        **HTTP_HEADERS,
        "X-Fantasy-Filter": json.dumps(
            {
                "players": {
                    "limit": limit,
                    "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
                }
            }
        ),
    }
    client = client or httpx.Client(headers=headers, timeout=120)
    try:
        # Recreate client headers if caller passed a client without the filter.
        resp = client.get(ESPN_PLAYERS_URL, headers=headers)
        resp.raise_for_status()
        return resp.json()
    finally:
        if own:
            client.close()


def save_raw(payload: dict, pulled_at: str | None = None) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = (pulled_at or _utcnow()).replace(":", "")
    path = RAW_DIR / f"espn_players_{stamp}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _season_projection(
    stats: list | None,
    *,
    season: int = SEASON,
) -> float | None:
    """Season-total projection (statSourceId=1, period 0).

    Prefer ``seasonId == season`` (config SEASON). ESPN often returns prior-year
    season totals first; taking the first match silently latches the wrong year.
    """
    fallback: float | None = None
    for st in stats or []:
        if (
            st.get("statSourceId") != 1
            or st.get("scoringPeriodId") != 0
            or st.get("statSplitTypeId") != 0
            or st.get("appliedTotal") is None
        ):
            continue
        total = float(st["appliedTotal"])
        if st.get("seasonId") == season:
            return total
        if fallback is None:
            fallback = total
    return fallback


def parse(payload: dict, *, season: int = SEASON) -> list[dict]:
    rows = []
    for entry in payload.get("players") or []:
        pl = entry.get("player") or {}
        espn_id = pl.get("id") if pl.get("id") is not None else entry.get("id")
        if espn_id is None:
            continue
        pos = POSITION_BY_ID.get(pl.get("defaultPositionId"))
        ownership = pl.get("ownership") or {}
        ranks = pl.get("draftRanksByRankType") or {}
        ppr_rank = (ranks.get("PPR") or {}).get("rank")
        adp = ownership.get("averageDraftPosition")
        rows.append(
            {
                "espn_id": str(espn_id),
                "name": pl.get("fullName") or f"{pl.get('firstName', '')} {pl.get('lastName', '')}".strip(),
                "position": pos,
                "team": PRO_TEAM_BY_ID.get(pl.get("proTeamId")),
                "pro_team_id": pl.get("proTeamId"),
                "injury_status": pl.get("injuryStatus"),
                "adp": float(adp) if adp is not None else None,
                "ppr_rank": int(ppr_rank) if ppr_rank is not None else None,
                "percent_owned": ownership.get("percentOwned"),
                "season_points": _season_projection(pl.get("stats"), season=season),
            }
        )
    return rows
