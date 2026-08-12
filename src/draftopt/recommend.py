from __future__ import annotations

from draftopt.pool import remaining_ranked
from draftopt.strategies import get_strategy

DEFAULT_STRATEGY = "marginal"

# Re-export for CPU and older imports.
__all__ = ["DEFAULT_STRATEGY", "recommend", "remaining_ranked"]


def recommend(conn, draft_id: str, n: int = 3, strategy: str = DEFAULT_STRATEGY) -> list[dict]:
    """Default product recommendation (marginal V1). Use strategy='adp' for baseline."""
    return get_strategy(strategy).recommend(conn, draft_id, n=n)
