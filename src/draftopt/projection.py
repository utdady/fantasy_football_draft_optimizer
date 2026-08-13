from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Projection:
    """Resolved fantasy points with explicit lineage (never silent proxies)."""

    value: float
    source: str  # espn | ecr_proxy | none
    quality: str  # high | low | none


def resolve_projection(player: dict) -> Projection:
    """
    Prefer ESPN season projection; fall back to a weak ECR proxy only if needed.

    ECR proxy is ranked LOW so callers can exclude or label it in reporting.
    """
    for key in ("proj_espn", "season_points"):
        val = player.get(key)
        if val is not None:
            return Projection(value=float(val), source="espn", quality="high")
    ecr = player.get("ecr_fp_ppr")
    if ecr is not None:
        return Projection(value=max(0.0, 350.0 - float(ecr)), source="ecr_proxy", quality="low")
    return Projection(value=0.0, source="none", quality="none")
