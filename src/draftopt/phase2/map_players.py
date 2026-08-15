"""Map FFC source players → canonical player_id + gsis_id.

Uses DynastyProcess / nflverse ff_playerids crosswalk. Auto-match is
name+position+team only (never name-alone). Unresolved rows are retained.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from draftopt.names import fold
from draftopt.sources import dynastyprocess


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", "NA", "na", "None", "null"}:
        return None
    if text.endswith(".0"):
        text = text[:-2]
    return text


def _norm_pos(pos: str | None) -> str | None:
    if not pos:
        return None
    p = pos.upper()
    if p in {"DEF", "D/ST"}:
        return "DST"
    if p == "PK":
        return "K"
    return p


def load_id_crosswalk(csv_text: str | None = None) -> list[dict[str, Any]]:
    """Load dynastyprocess-style IDs including gsis_id."""
    if csv_text is None:
        csv_text = dynastyprocess.fetch_ids()
    import csv
    import io

    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for raw in reader:
        sleeper_id = _clean(raw.get("sleeper_id"))
        espn_id = _clean(raw.get("espn_id"))
        fp_id = _clean(raw.get("fantasypros_id"))
        gsis_id = _clean(raw.get("gsis_id"))
        if not (sleeper_id or espn_id or fp_id or gsis_id):
            continue
        name = (raw.get("name") or "").strip()
        if not name:
            continue
        pos = _norm_pos(raw.get("position"))
        team = _clean(raw.get("team"))
        if sleeper_id:
            player_id = sleeper_id
        elif espn_id:
            player_id = f"espn:{espn_id}"
        elif fp_id:
            player_id = f"fp:{fp_id}"
        else:
            player_id = f"gsis:{gsis_id}"
        rows.append(
            {
                "player_id": player_id,
                "name": name,
                "name_fold": fold(name),
                "position": pos,
                "team": team,
                "sleeper_id": sleeper_id,
                "espn_id": espn_id,
                "fantasypros_id": fp_id,
                "gsis_id": gsis_id,
            }
        )
    return rows


def _index_crosswalk(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], list[dict]]:
    idx: dict[tuple[str, str, str], list[dict]] = {}
    for r in rows:
        if not r.get("position"):
            continue
        key = (r["name_fold"], r["position"], (r.get("team") or "").upper())
        idx.setdefault(key, []).append(r)
        # Also index without team for unique name+pos fallbacks that are unique globally
        soft = (r["name_fold"], r["position"], "")
        idx.setdefault(soft, []).append(r)
    return idx


def map_ffc_players(
    ffc_players: list[dict[str, Any]],
    crosswalk: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Returns mapped / unresolved lists. method is never 'name_only'.
    """
    idx = _index_crosswalk(crosswalk)
    mapped: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    name_only = 0

    for p in ffc_players:
        ffc_id = str(p["ffc_player_id"])
        name = p.get("name") or ""
        pos = _norm_pos(p.get("position"))
        team = (p.get("team") or "").upper() or None
        if not name or not pos:
            unresolved.append(
                {
                    "source": "ffc",
                    "source_player_id": ffc_id,
                    "name": name,
                    "position": pos,
                    "team": team,
                    "reason": "missing_name_or_position",
                }
            )
            continue

        nf = fold(name)
        method = "name_pos_team"
        hits: list[dict] = []
        if team:
            hits = idx.get((nf, pos, team), [])
        if not hits:
            soft = idx.get((nf, pos, ""), [])
            by_id = {h["player_id"]: h for h in soft}
            if len(by_id) == 1:
                hits = list(by_id.values())
                method = "name_pos_unique"
            else:
                # Missing/mismatched team and non-unique name+pos → unresolved later
                hits = list(by_id.values()) if not team and len(by_id) > 1 else []

        if len(hits) == 1:
            h = hits[0]
            mapped.append(
                {
                    "source": "ffc",
                    "source_player_id": ffc_id,
                    "player_id": h["player_id"],
                    "gsis_id": h.get("gsis_id"),
                    "sleeper_id": h.get("sleeper_id"),
                    "espn_id": h.get("espn_id"),
                    "method": method,
                    "notes": None,
                    "name": name,
                    "position": pos,
                    "team": team,
                }
            )
        elif len(hits) > 1:
            unresolved.append(
                {
                    "source": "ffc",
                    "source_player_id": ffc_id,
                    "name": name,
                    "position": pos,
                    "team": team,
                    "reason": "ambiguous_name_pos_team",
                }
            )
        else:
            unresolved.append(
                {
                    "source": "ffc",
                    "source_player_id": ffc_id,
                    "name": name,
                    "position": pos,
                    "team": team,
                    "reason": "no_crosswalk_match",
                }
            )

    n = len(ffc_players)
    n_map = len(mapped)
    return {
        "n_ffc": n,
        "n_mapped": n_map,
        "n_unresolved": len(unresolved),
        "n_manual": 0,
        "coverage": (n_map / n) if n else 0.0,
        "name_only_joins": name_only,
        "mapped": mapped,
        "unresolved": unresolved,
    }


def persist_mapping(conn: sqlite3.Connection, report: dict[str, Any]) -> None:
    conn.execute("DELETE FROM eval_player_map WHERE source = 'ffc'")
    conn.execute("DELETE FROM eval_player_unresolved WHERE source = 'ffc'")
    conn.executemany(
        """
        INSERT INTO eval_player_map (
            source, source_player_id, player_id, gsis_id, sleeper_id, espn_id, method, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                m["source"],
                m["source_player_id"],
                m["player_id"],
                m.get("gsis_id"),
                m.get("sleeper_id"),
                m.get("espn_id"),
                m["method"],
                m.get("notes"),
            )
            for m in report["mapped"]
        ],
    )
    conn.executemany(
        """
        INSERT INTO eval_player_unresolved (
            source, source_player_id, name, position, team, reason
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                u["source"],
                u["source_player_id"],
                u.get("name"),
                u.get("position"),
                u.get("team"),
                u["reason"],
            )
            for u in report["unresolved"]
        ],
    )
    conn.commit()
