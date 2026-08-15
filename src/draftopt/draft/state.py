from __future__ import annotations

import json
import random
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


def _clean_name(name: str | None, fallback: str = "") -> str:
    text = (name or "").strip()[:40]
    return text or fallback


def _parse_team_names_json(raw: str | None, n_teams: int, user_slot: int, user_name: str) -> dict[int, str]:
    labels = {i: f"CPU {i}" for i in range(1, n_teams + 1)}
    labels[user_slot] = user_name
    if not raw:
        return labels
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return labels
    if not isinstance(data, dict):
        return labels
    for key, val in data.items():
        try:
            slot = int(key)
        except (TypeError, ValueError):
            continue
        if 1 <= slot <= n_teams:
            labels[slot] = _clean_name(str(val), f"CPU {slot}")
    labels[user_slot] = user_name
    return labels


def resolve_draft_seating(
    *,
    n_teams: int = N_TEAMS,
    user_name: str = "You",
    order_mode: str = "pick_slot",
    user_slot: int | None = None,
    opponent_names: list[str] | None = None,
    team_names: dict | None = None,
    rng: random.Random | None = None,
) -> tuple[int, dict[int, str]]:
    """
    Resolve (user_slot, slot->display name).

    Modes:
    - pick_slot: use user_slot; optional opponent_names fill other seats in order
    - random_slot: random user_slot; optional opponent_names fill remaining seats randomly
    - random_all: user + (n_teams-1) opponents shuffled into all seats
    - fixed: team_names maps every slot 1..n_teams; exactly one seat is the user
    """
    rng = rng or random.Random()
    me = _clean_name(user_name, "You")
    mode = (order_mode or "pick_slot").strip().lower()
    opponents = [_clean_name(n) for n in (opponent_names or []) if _clean_name(n)]

    if mode == "fixed":
        if not team_names:
            raise DraftError("fixed order requires team_names for every slot")
        seating: dict[int, str] = {}
        for key, val in team_names.items():
            try:
                slot = int(key)
            except (TypeError, ValueError) as e:
                raise DraftError(f"invalid slot key {key!r}") from e
            if not 1 <= slot <= n_teams:
                raise DraftError(f"slot must be 1..{n_teams}")
            name = _clean_name(str(val))
            if not name:
                raise DraftError(f"empty name for slot {slot}")
            if slot in seating:
                raise DraftError(f"duplicate slot {slot}")
            seating[slot] = name
        if len(seating) != n_teams:
            missing = sorted(set(range(1, n_teams + 1)) - set(seating))
            raise DraftError(f"fixed order missing slots: {missing}")
        # User seat: prefer explicit user_slot if name matches; else unique name match
        user_seats = [s for s, n in seating.items() if fold(n) == fold(me)]
        if user_slot is not None:
            if not 1 <= int(user_slot) <= n_teams:
                raise DraftError(f"user_slot must be 1..{n_teams}")
            if fold(seating[int(user_slot)]) != fold(me):
                raise DraftError("user_slot name must match your name in fixed order")
            slot = int(user_slot)
        else:
            if len(user_seats) != 1:
                raise DraftError(
                    "fixed order needs your name on exactly one slot "
                    f"(found {len(user_seats)})"
                )
            slot = user_seats[0]
        seating[slot] = me
        return slot, seating

    if mode == "random_all":
        if len(opponents) != n_teams - 1:
            raise DraftError(
                f"random_all needs exactly {n_teams - 1} opponent names "
                f"(got {len(opponents)})"
            )
        if any(fold(n) == fold(me) for n in opponents):
            raise DraftError("opponent names must not match your name")
        if len({fold(n) for n in opponents}) != len(opponents):
            raise DraftError("opponent names must be unique")
        names = [me, *opponents]
        rng.shuffle(names)
        seating = {i + 1: names[i] for i in range(n_teams)}
        slot = next(s for s, n in seating.items() if fold(n) == fold(me))
        seating[slot] = me
        return slot, seating

    # pick_slot / random_slot
    if mode == "random_slot":
        slot = rng.randint(1, n_teams)
    else:
        slot = int(user_slot if user_slot is not None else USER_SLOT_DEFAULT)
        if not 1 <= slot <= n_teams:
            raise DraftError(f"user_slot must be 1..{n_teams}")

    seating = {i: f"CPU {i}" for i in range(1, n_teams + 1)}
    other_slots = [i for i in range(1, n_teams + 1) if i != slot]
    if opponents:
        if len(opponents) > n_teams - 1:
            raise DraftError(f"at most {n_teams - 1} opponent names")
        if any(fold(n) == fold(me) for n in opponents):
            raise DraftError("opponent names must not match your name")
        if len({fold(n) for n in opponents}) != len(opponents):
            raise DraftError("opponent names must be unique")
        fill = list(other_slots)
        if mode == "random_slot":
            rng.shuffle(fill)
        for i, name in enumerate(opponents):
            seating[fill[i]] = name
    seating[slot] = me
    return slot, seating


PICK_MODES = frozenset({"user_only", "live_sim"})


def normalize_pick_mode(pick_mode: str | None) -> str:
    mode = (pick_mode or "user_only").strip().lower()
    if mode not in PICK_MODES:
        raise DraftError(f"pick_mode must be one of {sorted(PICK_MODES)}")
    return mode


def draft_pick_mode(draft) -> str:
    try:
        raw = draft["pick_mode"]
    except (KeyError, IndexError):
        return "user_only"
    mode = (raw or "user_only").strip().lower()
    return mode if mode in PICK_MODES else "user_only"


def create_draft(
    conn,
    user_slot: int = USER_SLOT_DEFAULT,
    user_name: str = "You",
    n_teams: int = N_TEAMS,
    roster_preset: str | None = None,
    n_rounds: int | None = None,
    *,
    order_mode: str = "pick_slot",
    opponent_names: list[str] | None = None,
    team_names: dict | None = None,
    pick_mode: str = "user_only",
    rng: random.Random | None = None,
) -> str:
    me = _clean_name(user_name, "You")
    mode = normalize_pick_mode(pick_mode)
    slot, seating = resolve_draft_seating(
        n_teams=n_teams,
        user_name=me,
        order_mode=order_mode,
        user_slot=user_slot,
        opponent_names=opponent_names,
        team_names=team_names,
        rng=rng,
    )
    roster = get_roster_preset(roster_preset)
    rounds = n_rounds or roster["n_rounds"]
    draft_id = uuid4().hex[:12]
    names_json = json.dumps({str(k): v for k, v in sorted(seating.items())})
    conn.execute(
        """
        INSERT INTO drafts (
            draft_id, created_at, current_pick, user_slot, user_name,
            n_teams, n_rounds, roster_json, team_names_json, pick_mode
        ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            draft_id,
            _utcnow(),
            slot,
            me,
            n_teams,
            rounds,
            json.dumps(roster),
            names_json,
            mode,
        ),
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


def record_human_pick(conn, draft_id: str, player_id: str, made_by: str | None = None) -> dict:
    """
    Human-entered pick for the seat currently on the clock.

    - user_only: only your slot (same as record_user_pick)
    - live_sim: any seat; friends are tagged made_by='proxy'
    """
    draft = _draft_row(conn, draft_id)
    if draft_pick_mode(draft) == "live_sim":
        total = draft["n_teams"] * draft["n_rounds"]
        overall = draft["current_pick"]
        if overall > total:
            raise DraftError("draft is complete")
        team_slot = team_for_pick(overall, draft["n_teams"])
        tag = made_by
        if tag is None:
            tag = "user" if team_slot == draft["user_slot"] else "proxy"
        return record_pick(conn, draft_id, player_id, made_by=tag)
    return record_user_pick(conn, draft_id, player_id, made_by=made_by or "user")


def undo_last_pick(conn, draft_id: str) -> dict:
    """Undo only the most recent pick (any seat)."""
    _draft_row(conn, draft_id)
    last = conn.execute(
        """
        SELECT overall FROM picks
        WHERE draft_id = ?
        ORDER BY overall DESC LIMIT 1
        """,
        (draft_id,),
    ).fetchone()
    if last is None:
        raise DraftError("no picks to undo")
    conn.execute(
        "DELETE FROM picks WHERE draft_id = ? AND overall = ?",
        (draft_id, last["overall"]),
    )
    conn.execute(
        "UPDATE drafts SET current_pick = ? WHERE draft_id = ?",
        (last["overall"], draft_id),
    )
    conn.commit()
    return snapshot(conn, draft_id)


def undo_pick(conn, draft_id: str) -> dict:
    """Undo the user's last pick and any CPU picks after it (or last pick in live_sim)."""
    draft = _draft_row(conn, draft_id)
    if draft_pick_mode(draft) == "live_sim":
        return undo_last_pick(conn, draft_id)
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
    raw_names = None
    try:
        raw_names = draft["team_names_json"]
    except (KeyError, IndexError):
        raw_names = None
    labels_map = _parse_team_names_json(raw_names, n_teams, draft["user_slot"], user_name)
    labels = [labels_map[i] for i in range(1, n_teams + 1)]
    current_team = None if complete else team_for_pick(overall, n_teams)
    pick_mode = draft_pick_mode(draft)
    is_user = (not complete) and current_team == draft["user_slot"]
    return {
        "draft_id": draft_id,
        "user_slot": draft["user_slot"],
        "user_name": user_name,
        "team_labels": labels,
        "team_names": {str(k): v for k, v in labels_map.items()},
        "n_teams": n_teams,
        "n_rounds": n_rounds,
        "roster": roster,
        "current_pick": overall if not complete else total,
        "current_team": current_team,
        "current_round": None if complete else round_for_pick(overall, n_teams),
        "is_user_turn": is_user,
        "pick_mode": pick_mode,
        "can_human_pick": (not complete) and (is_user or pick_mode == "live_sim"),
        "complete": complete,
        "pick_clock_seconds": PICK_CLOCK_SECONDS,
        "picks": [dict(p) for p in picks],
        "board": board,
    }
