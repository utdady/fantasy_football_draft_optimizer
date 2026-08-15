"""V3-B: D's marginal minus next-best positional replacement (construction only)."""

from __future__ import annotations

from draftopt.phase2.replacement_nextbest import CONSTRUCTION_ID, replacement_nextbest
from draftopt.strategies.adp_structural import AdpV3aStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


class AdpV3bStrategy(AdpV3aStrategy):
    """
    E = D + one transformation: M_E = M_D - r*.

    Reuses MarginalValueStrategy.recommend() for M_D (same path as adp_v3a).
    Values remain frozen V3-A projections in the decision DB.
    """

    name = "adp_v3b"
    construction_id = CONSTRUCTION_ID

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        # Byte-for-behavior M_D: identical scoring loop as D / structural / marginal.
        d_scored = MarginalValueStrategy.recommend(self, conn, draft_id, n=10_000)
        remaining = [
            {
                "player_id": str(item["player_id"]),
                "name": item.get("name"),
                "position": (item.get("position") or "").upper(),
                "calibrated_value": (
                    float(item["season_points"])
                    if item.get("season_points") is not None
                    else (
                        float(item["proj_espn"])
                        if item.get("proj_espn") is not None
                        else None
                    )
                ),
            }
            for item in d_scored
        ]

        out: list[dict] = []
        for item in d_scored:
            md = item.get("marginal")
            if md is None:
                continue
            rinfo = replacement_nextbest(
                player_id=str(item["player_id"]),
                position=item.get("position"),
                remaining=remaining,
            )
            me = round(float(md) - float(rinfo["replacement"]), 2)
            row = dict(item)
            row["marginal_d"] = float(md)
            row["replacement"] = rinfo["replacement"]
            row["replacement_missing"] = rinfo["replacement_missing"]
            row["replacement_player_id"] = rinfo["replacement_player_id"]
            row["replacement_name"] = rinfo["replacement_name"]
            row["construction_id"] = self.construction_id
            row["marginal"] = me
            row["marginal_e"] = me
            row["strategy"] = self.name
            row["why"] = (
                f"V3-B: M_E={me:.1f} (M_D={float(md):.1f} − r*={rinfo['replacement']:.1f}"
                f"{'; missing' if rinfo['replacement_missing'] else ''}) "
                f"[{self.construction_id}]"
            )
            out.append(row)

        out.sort(
            key=lambda r: (
                -(r.get("marginal") or 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("ecr_fp_ppr") is None,
                r.get("ecr_fp_ppr") if r.get("ecr_fp_ppr") is not None else 9999,
                r.get("name") or "",
            )
        )
        return out[:n]
