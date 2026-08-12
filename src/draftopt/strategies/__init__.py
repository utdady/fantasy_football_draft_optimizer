from __future__ import annotations

from draftopt.strategies.adp import ADPStrategy
from draftopt.strategies.base import DraftStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


def get_strategy(name: str = "marginal") -> DraftStrategy:
    key = (name or "marginal").strip().lower()
    if key in {"adp", "baseline"}:
        return ADPStrategy()
    if key in {"marginal", "v1", "marginal_value"}:
        return MarginalValueStrategy()
    raise ValueError(f"unknown strategy: {name}")


__all__ = ["ADPStrategy", "DraftStrategy", "MarginalValueStrategy", "get_strategy"]
