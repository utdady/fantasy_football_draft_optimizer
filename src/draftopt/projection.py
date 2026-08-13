from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Projection:
    """Resolved fantasy points with explicit lineage (never silent proxies)."""

    value: float
    source: str  # espn | ecr_proxy | none
    quality: str  # high | low | none


def resolve_projection(player: dict, *, allow_proxy: bool = False) -> Projection:
    """
    Prefer ESPN season projection.

    ECR→points is not fantasy points. Default allow_proxy=False so strategies and
    official runs do not silently treat rank as projection. Pass allow_proxy=True
    only for exploratory / UI fallback labeling.
    """
    for key in ("proj_espn", "season_points"):
        val = player.get(key)
        if val is not None:
            return Projection(value=float(val), source="espn", quality="high")
    if allow_proxy:
        ecr = player.get("ecr_fp_ppr")
        if ecr is not None:
            return Projection(value=max(0.0, 350.0 - float(ecr)), source="ecr_proxy", quality="low")
    return Projection(value=0.0, source="none", quality="none")
