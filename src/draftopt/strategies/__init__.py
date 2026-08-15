from __future__ import annotations

from draftopt.strategies.adp import ADPStrategy
from draftopt.strategies.adp_feasible import AdpFeasibleStrategy
from draftopt.strategies.adp_structural import (
    AdpBaselineStrategy,
    AdpStructuralStrategy,
    AdpV3aStrategy,
)
from draftopt.strategies.adp_v3b import AdpV3bStrategy
from draftopt.strategies.base import DraftStrategy
from draftopt.strategies.greedy import GreedyProjectionStrategy
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.strategies.marginal_no_qb_r1 import MarginalNoQBR1Strategy
from draftopt.strategies.marginal_v2 import MarginalV2Strategy
from draftopt.strategies.marginal_v2_beta import MarginalV2BetaStrategy
from draftopt.strategies.marginal_robust_min import MarginalRobustMinStrategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy


def get_strategy(name: str = "marginal") -> DraftStrategy:
    key = (name or "marginal").strip().lower()
    if key in {"adp", "baseline"}:
        return ADPStrategy()
    if key in {"adp_baseline"}:
        return AdpBaselineStrategy()
    if key in {"adp_feasible"}:
        return AdpFeasibleStrategy()
    if key in {"adp_structural"}:
        return AdpStructuralStrategy()
    if key in {"adp_v3a", "v3a"}:
        return AdpV3aStrategy()
    if key in {"adp_v3b", "v3b"}:
        return AdpV3bStrategy()
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
    if key in {"marginal_v2_beta", "v2_beta", "v2b", "lookahead_mix"}:
        return MarginalV2BetaStrategy()
    if key in {"robust_min", "marginal_robust_min", "v2_robust", "beta2_robust"}:
        return MarginalRobustMinStrategy()
    raise ValueError(f"unknown strategy: {name}")


__all__ = [
    "ADPStrategy",
    "AdpBaselineStrategy",
    "AdpFeasibleStrategy",
    "AdpStructuralStrategy",
    "AdpV3aStrategy",
    "AdpV3bStrategy",
    "DraftStrategy",
    "GreedyProjectionStrategy",
    "MarginalNoQBR1Strategy",
    "MarginalValueStrategy",
    "MarginalV2Strategy",
    "MarginalV2BetaStrategy",
    "MarginalRobustMinStrategy",
    "MarginalVorStrategy",
    "get_strategy",
]
