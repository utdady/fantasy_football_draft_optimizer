from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool
from draftopt.projection import resolve_projection


def _user_roster_players(conn, draft_id: str) -> list[dict]:
    draft = _draft_row(conn, draft_id)
    rows = conn.execute(
        """
        SELECT p.player_id, p.name, p.position, p.team,
               pr.season_points AS season_points,
               a.adp AS adp_espn, r.ecr AS ecr_fp_ppr
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        LEFT JOIN projections_snapshots pr
            ON pr.player_id = p.player_id AND pr.source = 'espn'
        LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
        LEFT JOIN rankings_snapshots r
            ON r.player_id = p.player_id AND r.source = 'fantasypros'
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        ORDER BY pk.overall
        """,
        (draft_id, draft["user_slot"]),
    ).fetchall()
    return [dict(r) for r in rows]


def _as_lineup_player(player: dict) -> dict:
    # Official path: ESPN projections only (no ECR→points).
    proj = resolve_projection(player, allow_proxy=False)
    return {
        "player_id": player.get("player_id"),
        "name": player.get("name"),
        "position": player.get("position"),
        "team": player.get("team"),
        "season_points": proj.value,
        "projection_source": proj.source,
        "projection_quality": proj.quality,
        "adp_espn": player.get("adp_espn"),
        "ecr_fp_ppr": player.get("ecr_fp_ppr"),
    }


def _why(marginal: float, before: float, after: float, candidate: dict) -> str:
    pos = (candidate.get("position") or "?").upper()
    if before <= 0.01 and marginal > 0:
        return f"+{marginal:.1f} starter pts (fills {pos})"
    if marginal > 0.05:
        return f"+{marginal:.1f} starter pts ({before:.1f} → {after:.1f})"
    if abs(marginal) <= 0.05:
        return f"~0 starter lift; best ADP/ECR among near-ties ({pos})"
    return f"{marginal:.1f} starter pts ({before:.1f} → {after:.1f})"


class MarginalValueStrategy:
    """V1: maximize expected starting-lineup points (FLEX-aware)."""

    name = "marginal"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = (draft_roster(draft).get("slots") or {})
        roster = [_as_lineup_player(p) for p in _user_roster_players(conn, draft_id)]
        base = lineup_ev(roster, slots)
        base_total = base.total

        scored: list[dict] = []
        for cand in candidate_pool(conn, draft_id):
            lined = _as_lineup_player(cand)
            # Skip anyone without a real ESPN projection (DST included).
            if lined["projection_quality"] != "high" or lined["season_points"] <= 0:
                continue
            after = lineup_ev(roster + [lined], slots)
            marginal = after.total - base_total
            item = dict(cand)
            item["proj_espn"] = lined["season_points"]
            item["season_points"] = lined["season_points"]
            item["projection_source"] = lined["projection_source"]
            item["projection_quality"] = lined["projection_quality"]
            item["marginal"] = round(marginal, 2)
            item["lineup_before"] = round(base_total, 2)
            item["lineup_after"] = round(after.total, 2)
            item["why"] = _why(marginal, base_total, after.total, cand)
            item["strategy"] = self.name
            scored.append(item)

        scored.sort(
            key=lambda r: (
                -(r.get("marginal") or 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("ecr_fp_ppr") is None,
                r.get("ecr_fp_ppr") if r.get("ecr_fp_ppr") is not None else 9999,
                r.get("name") or "",
            )
        )
        return scored[:n]
