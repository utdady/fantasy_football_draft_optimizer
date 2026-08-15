"""P2.2C labeled strategies: ADP baseline vs ADP-structural (not production marginal)."""

from __future__ import annotations

from draftopt.strategies.adp import ADPStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


class AdpBaselineStrategy(ADPStrategy):
    """Always pick best remaining ADP. Labeled experiment name."""

    name = "adp_baseline"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        out = super().recommend(conn, draft_id, n=n)
        for item in out:
            item["strategy"] = self.name
            item["why"] = "P2.2C: lowest remaining FFC ADP (aliased in draft DB)"
        return out


class AdpStructuralStrategy(MarginalValueStrategy):
    """
    Same FLEX-aware marginal construction as V1, but season_points come from the
    frozen ADP→value curve (materialized as projections source=espn in P2.2C DB).
    """

    name = "adp_structural"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        out = super().recommend(conn, draft_id, n=n)
        for item in out:
            item["strategy"] = self.name
            item["why"] = (
                f"P2.2C ADP-structural: {item.get('why', '')} "
                f"[value=ADP-curve, not ESPN proj]"
            )
        return out
