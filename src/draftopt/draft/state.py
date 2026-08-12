from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from draftopt.config import (
    N_TEAMS,
    PICK_CLOCK_SECONDS,
    USER_SLOT_DEFAULT,
    get_roster_preset,
)
from draftopt.names import fold


class DraftError(Exception):
    pass


def team_for_pick(overall: int, n_teams: int = N_TEAMS) -> int:
    if overall < 1:
        raise DraftError("overall pick must be >= 1")
    round_num = (overall - 1) // n_teams + 1
    pos = (overall - 1) % n_teams
    if round_num % 2 == 1:
        return pos + 1
    return n_teams - pos


def round_for_pick(overall: int, n_teams: int = N_TEAMS) -> int:
    if overall < 1:
        raise DraftError("overall pick must be >= 1")
    return (overall - 1) // n_teams + 1


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def draft_roster(draft) -> dict:
    raw = draft["roster_json"] if "roster_json" in draft.keys() else None
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and data.get("slots"):
                return data
        except json.JSONDecodeError:
            pass
    return get_roster_preset()


def create_draft(
    conn,
    user_slot: int = USER_SLOT_DEFAULT,
    user_name: str = "You",
    n_teams: int = N_TEAMS,
    roster_preset: str | None = None,
    n_rounds: int | None = None,
) -> str:
    if not 1 <= user_slot <= n_teams:
        raise DraftError(f"user_slot must be 1..{n_teams}")
    roster = get_roster_preset(roster_preset)
    rounds = n_rounds or roster["n_rounds"]
    name = (user_name or "You").strip()[:40] or "You"
    draft_id = uuid4().hex[:12]
    conn.execute(
        """
        INSERT INTO drafts (
            draft_id, created_at, current_pick, user_slot, user_name,
            n_teams, n_rounds, roster_json
        ) VALUES (?, ?, 1, ?, ?, ?, ?, ?)
        """,
        (draft_id, _utcnow(), user_slot, name, n_teams, rounds, json.dumps(roster)),
    )
    conn.commit()
    return draft_id


def _draft_row(conn, draft_id: str):
    row = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
    if row is None:
        raise DraftError(f"unknown draft {draft_id}")
    return row


def _drafted_ids(conn, draft_id: str) -> set[str]:
    rows = conn.execute("SELECT player_id FROM picks WHERE draft_id = ?", (draft_id,)).fetchall()
    return {r["player_id"] for r in rows}


def is_user_turn(draft) -> bool:
    total = draft["n_teams"] * draft["n_rounds"]
    overall = draft["current_pick"]
    if overall > total:
        return False
    return team_for_pick(overall, draft["n_teams"]) == draft["user_slot"]


def record_pick(conn, draft_id: str, player_id: str, made_by: str = "user") -> dict:
    draft = _draft_row(conn, draft_id)
    total = draft["n_teams"] * draft["n_rounds"]
    overall = draft["current_pick"]
    if overall > total:
        raise DraftError("draft is complete")
    player = conn.execute("SELECT * FROM players WHERE player_id = ?", (player_id,)).fetchone()
    if player is None:
        raise DraftError("unknown player")
    if player_id in _drafted_ids(conn, draft_id):
        raise DraftError("player already drafted")
    team_slot = team_for_pick(overall, draft["n_teams"])
    rnd = round_for_pick(overall, draft["n_teams"])
    conn.execute(
        """
        INSERT INTO picks (draft_id, overall, team_slot, round, player_id, picked_at, made_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (draft_id, overall, team_slot, rnd, player_id, _utcnow(), made_by),
    )
    conn.execute(
        "UPDATE drafts SET current_pick = ? WHERE draft_id = ?",
        (overall + 1, draft_id),
    )
    conn.commit()
    return snapshot(conn, draft_id)


def record_user_pick(conn, draft_id: str, player_id: str, made_by: str = "user") -> dict:
    draft = _draft_row(conn, draft_id)
    if not is_user_turn(draft):
        raise DraftError("not your pick")
    return record_pick(conn, draft_id, player_id, made_by=made_by)


def undo_pick(conn, draft_id: str) -> dict:
    """Undo the user's last pick and any CPU picks after it."""
    _draft_row(conn, draft_id)
    last_user = conn.execute(
        """
        SELECT overall FROM picks
        WHERE draft_id = ? AND team_slot = (SELECT user_slot FROM drafts WHERE draft_id = ?)
        ORDER BY overall DESC LIMIT 1
        """,
        (draft_id, draft_id),
    ).fetchone()
    if last_user is None:
        raise DraftError("no picks to undo")
    conn.execute(
        "DELETE FROM picks WHERE draft_id = ? AND overall >= ?",
        (draft_id, last_user["overall"]),
    )
    conn.execute(
        "UPDATE drafts SET current_pick = ? WHERE draft_id = ?",
        (last_user["overall"], draft_id),
    )
    conn.commit()
    return snapshot(conn, draft_id)


def resolve_player(conn, draft_id: str, query: str) -> str:
    q = fold(query)
    if not q:
        raise DraftError("empty query")
    drafted = _drafted_ids(conn, draft_id)
    exact = conn.execute(
        """
        SELECT p.player_id, p.name FROM players p
        JOIN player_aliases a ON a.player_id = p.player_id
        WHERE a.alias = ?
        """,
        (q,),
    ).fetchall()
    candidates = [r for r in exact if r["player_id"] not in drafted]
    if len(candidates) == 1:
        return candidates[0]["player_id"]
    if len(candidates) > 1:
        names = ", ".join(r["name"] for r in candidates[:5])
        raise DraftError(f"ambiguous: {names}")
    prefix = conn.execute(
        """
        SELECT DISTINCT p.player_id, p.name FROM players p
        JOIN player_aliases a ON a.player_id = p.player_id
        WHERE a.alias LIKE ?
        """,
        (q + "%",),
    ).fetchall()
    candidates = [r for r in prefix if r["player_id"] not in drafted]
    if len(candidates) == 1:
        return candidates[0]["player_id"]
    if len(candidates) > 1:
        names = ", ".join(r["name"] for r in candidates[:5])
        raise DraftError(f"ambiguous: {names}")
    raise DraftError("no matching remaining player")


def search_remaining(
    conn,
    draft_id: str,
    query: str = "",
    position: str | None = None,
    team: str | None = None,
    sort: str = "adp",
    limit: int = 50,
) -> list[dict]:
    draft = _draft_row(conn, draft_id)
    roster = draft_roster(draft)
    slots = roster.get("slots") or {}
    allow_k = int(slots.get("K") or 0) > 0
    q = fold(query)
    drafted = _drafted_ids(conn, draft_id)
    pos = (position or "").upper().strip()
    team_code = (team or "").upper().strip()
    if pos == "K" and not allow_k:
        return []

    order = {
        "adp": "CASE WHEN a.adp IS NULL THEN 1 ELSE 0 END, a.adp, r.ecr, p.name",
        "ecr": "CASE WHEN r.ecr IS NULL THEN 1 ELSE 0 END, r.ecr, a.adp, p.name",
        "proj": "CASE WHEN pr.season_points IS NULL THEN 1 ELSE 0 END, pr.season_points DESC, a.adp, p.name",
        "name": "p.name",
    }.get(sort, "CASE WHEN a.adp IS NULL THEN 1 ELSE 0 END, a.adp, r.ecr, p.name")

    if q:
        sql = f"""
            SELECT DISTINCT p.player_id, p.name, p.position, p.team, p.injury_status,
                   a.adp, r.ecr, pr.season_points
            FROM players p
            JOIN player_aliases al ON al.player_id = p.player_id
            LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
            LEFT JOIN rankings_snapshots r ON r.player_id = p.player_id AND r.source = 'fantasypros'
            LEFT JOIN projections_snapshots pr ON pr.player_id = p.player_id AND pr.source = 'espn'
            WHERE al.alias LIKE ?
            ORDER BY {order}
        """
        rows = conn.execute(sql, (q + "%",)).fetchall()
    else:
        sql = f"""
            SELECT p.player_id, p.name, p.position, p.team, p.injury_status,
                   a.adp, r.ecr, pr.season_points
            FROM players p
            LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
            LEFT JOIN rankings_snapshots r ON r.player_id = p.player_id AND r.source = 'fantasypros'
            LEFT JOIN projections_snapshots pr ON pr.player_id = p.player_id AND pr.source = 'espn'
            ORDER BY {order}
        """
        rows = conn.execute(sql).fetchall()

    out = []
    seen: set[str] = set()
    for row in rows:
        if row["player_id"] in drafted or row["player_id"] in seen:
            continue
        row_pos = (row["position"] or "").upper()
        if not allow_k and row_pos == "K":
            continue
        if pos and pos != "ALL" and row_pos != pos:
            continue
        if team_code and (row["team"] or "").upper() != team_code:
            continue
        seen.add(row["player_id"])
        out.append(dict(row))
        if len(out) >= limit:
            break
    return out


def snapshot(conn, draft_id: str) -> dict:
    draft = _draft_row(conn, draft_id)
    roster = draft_roster(draft)
    picks = conn.execute(
        """
        SELECT pk.overall, pk.team_slot, pk.round, pk.player_id, pk.made_by,
               p.name, p.position, p.team
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        WHERE pk.draft_id = ?
        ORDER BY pk.overall
        """,
        (draft_id,),
    ).fetchall()
    n_teams = draft["n_teams"]
    n_rounds = draft["n_rounds"]
    total = n_teams * n_rounds
    overall = draft["current_pick"]
    board = [[None for _ in range(n_teams)] for _ in range(n_rounds)]
    for pk in picks:
        board[pk["round"] - 1][pk["team_slot"] - 1] = {
            "overall": pk["overall"],
            "player_id": pk["player_id"],
            "name": pk["name"],
            "position": pk["position"],
            "team": pk["team"],
            "made_by": pk["made_by"],
        }
    complete = overall > total
    user_name = draft["user_name"] or "You"
    labels = []
    for slot in range(1, n_teams + 1):
        labels.append(user_name if slot == draft["user_slot"] else f"CPU {slot}")
    current_team = None if complete else team_for_pick(overall, n_teams)
    return {
        "draft_id": draft_id,
        "user_slot": draft["user_slot"],
        "user_name": user_name,
        "team_labels": labels,
        "n_teams": n_teams,
        "n_rounds": n_rounds,
        "roster": roster,
        "current_pick": overall if not complete else total,
        "current_team": current_team,
        "current_round": None if complete else round_for_pick(overall, n_teams),
        "is_user_turn": (not complete) and current_team == draft["user_slot"],
        "complete": complete,
        "pick_clock_seconds": PICK_CLOCK_SECONDS,
        "picks": [dict(p) for p in picks],
        "board": board,
    }
