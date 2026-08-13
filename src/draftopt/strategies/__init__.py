from __future__ import annotations

from draftopt.strategies.adp import ADPStrategy
from draftopt.strategies.base import DraftStrategy
from draftopt.strategies.greedy import GreedyProjectionStrategy
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.strategies.marginal_no_qb_r1 import MarginalNoQBR1Strategy
from draftopt.strategies.marginal_v2 import MarginalV2Strategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy


def get_strategy(name: str = "marginal") -> DraftStrategy:
    key = (name or "marginal").strip().lower()
    if key in {"adp", "baseline"}:
        return ADPStrategy()
    if key in {"greedy", "greedy_proj", "projection"}:
        return GreedyProjectionStrategy()
    if key in {"marginal", "v1", "marginal_value", "raw_marginal"}:
        return MarginalValueStrategy()
    if key in {"marginal_no_qb_r1", "no_qb_r1", "marginal_noqb"}:
        return MarginalNoQBR1Strategy()
    if key in {"marginal_vor", "vor", "vor_lite", "marginal_value_vor"}:
        return MarginalVorStrategy()
    if key in {"marginal_v2", "v2", "v2_alpha", "lookahead_adp"}:
        return MarginalV2Strategy()
    raise ValueError(f"unknown strategy: {name}")


__all__ = [
    "ADPStrategy",
    "DraftStrategy",
    "GreedyProjectionStrategy",
    "MarginalNoQBR1Strategy",
    "MarginalValueStrategy",
    "MarginalV2Strategy",
    "MarginalVorStrategy",
    "get_strategy",
]
