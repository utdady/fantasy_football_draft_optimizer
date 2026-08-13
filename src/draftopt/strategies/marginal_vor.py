from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool
from draftopt.projection import resolve_projection
from draftopt.strategies.marginal import _user_roster_players
from draftopt.vor import replacement_baselines, vor_points


class MarginalVorStrategy:
    """
    VOR-lite marginal: same FLEX-aware lineup lift as raw marginal, but players
    contribute (projection − positional replacement) inside lineup_ev.

    Replacement = Nth-best remaining ESPN proj at that position (league starter demand).
    """

    name = "marginal_vor"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = (draft_roster(draft).get("slots") or {})
        baselines = replacement_baselines(
            conn, draft_id, n_teams=int(draft["n_teams"]), slots=slots
        )

        def as_vor_player(player: dict) -> dict:
            proj = resolve_projection(player, allow_proxy=False)
            return {
                "player_id": player.get("player_id"),
                "name": player.get("name"),
                "position": player.get("position"),
                "team": player.get("team"),
                "season_points": vor_points(proj.value, player.get("position"), baselines),
                "raw_proj": proj.value,
                "replacement": float(
                    baselines.get((player.get("position") or "").upper()) or 0.0
                ),
                "projection_source": proj.source,
                "projection_quality": proj.quality,
                "adp_espn": player.get("adp_espn"),
                "ecr_fp_ppr": player.get("ecr_fp_ppr"),
            }

        roster = [as_vor_player(p) for p in _user_roster_players(conn, draft_id)]
        # Only count roster players that had real ESPN proj originally.
        roster = [p for p in roster if p["projection_quality"] == "high"]
        base = lineup_ev(roster, slots)
        base_total = base.total

        scored: list[dict] = []
        for cand in candidate_pool(conn, draft_id):
            lined = as_vor_player(cand)
            if lined["projection_quality"] != "high" or lined["raw_proj"] <= 0:
                continue
            after = lineup_ev(roster + [lined], slots)
            marginal = after.total - base_total
            item = dict(cand)
            item["proj_espn"] = lined["raw_proj"]
            item["season_points"] = lined["raw_proj"]
            item["vor_points"] = round(lined["season_points"], 2)
            item["replacement"] = round(lined["replacement"], 2)
            item["projection_source"] = lined["projection_source"]
            item["projection_quality"] = lined["projection_quality"]
            item["marginal"] = round(marginal, 2)
            item["lineup_before"] = round(base_total, 2)
            item["lineup_after"] = round(after.total, 2)
            item["why"] = (
                f"+{marginal:.1f} VOR starter lift "
                f"(proj {lined['raw_proj']:.0f} − repl {lined['replacement']:.0f}; "
                f"{base_total:.1f} → {after.total:.1f})"
            )
            item["strategy"] = self.name
            scored.append(item)

        scored.sort(
            key=lambda r: (
                -(r.get("marginal") or 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("name") or "",
            )
        )
        return scored[:n]
