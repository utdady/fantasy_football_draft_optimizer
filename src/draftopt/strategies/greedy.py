from __future__ import annotations

from draftopt.pool import remaining_ranked
from draftopt.projection import resolve_projection


class GreedyProjectionStrategy:
    """Ablation baseline: always take highest remaining ESPN projection."""

    name = "greedy"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        scored: list[dict] = []
        for rec in remaining_ranked(conn, draft_id):
            proj = resolve_projection(rec, allow_proxy=False)
            if proj.quality != "high":
                continue
            item = dict(rec)
            item["proj_espn"] = proj.value
            item["season_points"] = proj.value
            item["projection_source"] = proj.source
            item["projection_quality"] = proj.quality
            item["why"] = f"Highest remaining ESPN projection ({proj.value:.1f})"
            item["strategy"] = self.name
            scored.append(item)
        scored.sort(
            key=lambda r: (
                -(r.get("season_points") or 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("name") or "",
            )
        )
        return scored[:n]
