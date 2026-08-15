"""V3-B.1: D's marginal minus cross-position empty-need alternative."""

from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.phase2.crosspos_empty_need import (
    CONSTRUCTION_ID,
    crosspos_empty_need_nextbest,
)
from draftopt.strategies.adp_feasible import _counts_from_rows
from draftopt.strategies.adp_structural import AdpV3aStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


class AdpV3b1Strategy(AdpV3aStrategy):
    """
    B.1 = D + one transformation: M_B1 = M_D - a*.

    Reuses MarginalValueStrategy.recommend() for M_D (same path as adp_v3a).
    Values remain frozen V3-A projections in the decision DB.
    """

    name = "adp_v3b1"
    construction_id = CONSTRUCTION_ID

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = draft_roster(draft).get("slots") or {}
        user_slot = int(draft["user_slot"])
        rows = conn.execute(
            """
            SELECT p.position FROM picks pk
            JOIN players p ON p.player_id = pk.player_id
            WHERE pk.draft_id = ? AND pk.team_slot = ?
            """,
            (draft_id, user_slot),
        ).fetchall()
        counts = _counts_from_rows([dict(r) for r in rows])

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
            ainfo = crosspos_empty_need_nextbest(
                player_id=str(item["player_id"]),
                position=item.get("position"),
                remaining=remaining,
                counts=counts,
                slots=slots,
            )
            mb1 = round(float(md) - float(ainfo["cross_alt"]), 2)
            row = dict(item)
            row["marginal_d"] = float(md)
            row["cross_alt"] = ainfo["cross_alt"]
            row["cross_alt_missing"] = ainfo["cross_alt_missing"]
            row["cross_alt_player_id"] = ainfo["cross_alt_player_id"]
            row["cross_alt_name"] = ainfo["cross_alt_name"]
            row["cross_alt_position"] = ainfo["cross_alt_position"]
            row["empty_capacity_positions"] = ainfo["empty_capacity_positions"]
            row["construction_id"] = self.construction_id
            row["marginal"] = mb1
            row["marginal_b1"] = mb1
            row["strategy"] = self.name
            row["why"] = (
                f"V3-B.1: M_B1={mb1:.1f} (M_D={float(md):.1f} − a*={ainfo['cross_alt']:.1f}"
                f"{' missing' if ainfo['cross_alt_missing'] else ''}) "
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
