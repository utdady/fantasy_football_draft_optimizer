from __future__ import annotations

from draftopt.draft.state import _drafted_ids, _draft_row, draft_roster


def _allowed_positions(roster: dict) -> set[str]:
    slots = roster.get("slots") or {}
    allowed = {"QB", "RB", "WR", "TE", "DST"}
    if int(slots.get("K") or 0) > 0:
        allowed.add("K")
    return allowed


def remaining_ranked(conn, draft_id: str) -> list[dict]:
    draft = _draft_row(conn, draft_id)
    drafted = _drafted_ids(conn, draft_id)
    allowed = _allowed_positions(draft_roster(draft))
    rows = conn.execute(
        """
        SELECT p.player_id, p.name, p.position, p.team, p.injury_status,
               a.adp AS adp_espn, r.ecr AS ecr_fp_ppr, r.sd AS ecr_sd,
               pr.season_points AS proj_espn
        FROM players p
        LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
        LEFT JOIN rankings_snapshots r ON r.player_id = p.player_id AND r.source = 'fantasypros'
        LEFT JOIN projections_snapshots pr ON pr.player_id = p.player_id AND pr.source = 'espn'
        ORDER BY
            CASE WHEN a.adp IS NULL THEN 1 ELSE 0 END,
            a.adp,
            CASE WHEN r.ecr IS NULL THEN 1 ELSE 0 END,
            r.ecr,
            p.name
        """
    ).fetchall()
    out = []
    for row in rows:
        if row["player_id"] in drafted:
            continue
        pos = (row["position"] or "").upper()
        if pos not in allowed:
            continue
        out.append(dict(row))
    return out


def recommend(conn, draft_id: str, n: int = 3) -> list[dict]:
    out = []
    for rec in remaining_ranked(conn, draft_id):
        rec["why"] = (
            "Lowest remaining ESPN ADP" if rec.get("adp_espn") is not None else "Best remaining ECR"
        )
        out.append(rec)
        if len(out) >= n:
            break
    return out
