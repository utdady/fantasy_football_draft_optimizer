from __future__ import annotations

from draftopt.pool import remaining_ranked
from draftopt.strategies.base import DraftStrategy


class ADPStrategy:
    """Baseline: lowest remaining ESPN ADP, ECR fallback."""

    name = "adp"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        out: list[dict] = []
        for rec in remaining_ranked(conn, draft_id):
            item = dict(rec)
            item["why"] = (
                "Lowest remaining ESPN ADP"
                if item.get("adp_espn") is not None
                else "Best remaining ECR"
            )
            item["strategy"] = self.name
            out.append(item)
            if len(out) >= n:
                break
        return out


def get_adp_strategy() -> DraftStrategy:
    return ADPStrategy()
