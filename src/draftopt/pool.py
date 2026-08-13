from __future__ import annotations

from draftopt.draft.state import _drafted_ids, _draft_row, draft_roster

# Default windows for strategy-independent candidate generation.
ADP_CANDIDATE_N = 40
PROJ_CANDIDATE_N = 40


def allowed_positions(roster: dict) -> set[str]:
    slots = roster.get("slots") or {}
    allowed = {"QB", "RB", "WR", "TE", "DST"}
    if int(slots.get("K") or 0) > 0:
        allowed.add("K")
    return allowed


def remaining_ranked(conn, draft_id: str) -> list[dict]:
    draft = _draft_row(conn, draft_id)
    drafted = _drafted_ids(conn, draft_id)
    allowed = allowed_positions(draft_roster(draft))
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


def candidate_pool(
    conn,
    draft_id: str,
    *,
    n_adp: int = ADP_CANDIDATE_N,
    n_proj: int = PROJ_CANDIDATE_N,
) -> list[dict]:
    """
    Strategy-independent shortlist: top ADP ∪ top ESPN projection.

    Avoids evaluating only market-ranked names so high-proj / low-ADP players
    can still enter the optimizer.
    """
    remaining = remaining_ranked(conn, draft_id)
    by_id = {p["player_id"]: p for p in remaining}
    chosen: dict[str, dict] = {}

    for p in remaining[: max(0, n_adp)]:
        chosen[p["player_id"]] = p

    by_proj = sorted(
        (p for p in remaining if p.get("proj_espn") is not None),
        key=lambda p: float(p["proj_espn"]),
        reverse=True,
    )
    for p in by_proj[: max(0, n_proj)]:
        chosen[p["player_id"]] = by_id[p["player_id"]]

    # Stable-ish order: ADP first, then projection-only additions by proj desc.
    adp_ids = {p["player_id"] for p in remaining[: max(0, n_adp)]}
    out = [p for p in remaining if p["player_id"] in chosen and p["player_id"] in adp_ids]
    proj_only = [
        chosen[p["player_id"]]
        for p in by_proj
        if p["player_id"] in chosen and p["player_id"] not in adp_ids
    ]
    out.extend(proj_only)
    return out
