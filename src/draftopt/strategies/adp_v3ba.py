"""V3-B Branch A: D's marginal minus best cross-need M_D (not v)."""

from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.phase2.crosspos_empty_need_marginal import (
    CONSTRUCTION_ID,
    crosspos_empty_need_marginal,
)
from draftopt.strategies.adp_feasible import _counts_from_rows
from draftopt.strategies.adp_structural import AdpV3aStrategy
from draftopt.strategies.marginal import MarginalValueStrategy


class AdpV3baStrategy(AdpV3aStrategy):
    """
    A = D + one transformation: M_A = M_D(p) - M_D(q*).

    Reuses MarginalValueStrategy.recommend() for M_D (same path as adp_v3a).
    q* = argmax M_D on B.1 cross-need eligibility set.
    """

    name = "adp_v3ba"
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
                "marginal_d": (
                    float(item["marginal"]) if item.get("marginal") is not None else None
                ),
                "adp_espn": item.get("adp_espn"),
                "ecr_fp_ppr": item.get("ecr_fp_ppr"),
            }
            for item in d_scored
        ]

        out: list[dict] = []
        for item in d_scored:
            md = item.get("marginal")
            if md is None:
                continue
            ainfo = crosspos_empty_need_marginal(
                player_id=str(item["player_id"]),
                position=item.get("position"),
                remaining=remaining,
                counts=counts,
                slots=slots,
            )
            ma = round(float(md) - float(ainfo["cross_alt_marginal"]), 2)
            row = dict(item)
            row["marginal_d"] = float(md)
            row["cross_alt_marginal"] = ainfo["cross_alt_marginal"]
            row["cross_alt_missing"] = ainfo["cross_alt_missing"]
            row["cross_alt_player_id"] = ainfo["cross_alt_player_id"]
            row["cross_alt_name"] = ainfo["cross_alt_name"]
            row["cross_alt_position"] = ainfo["cross_alt_position"]
            row["empty_capacity_positions"] = ainfo["empty_capacity_positions"]
            row["construction_id"] = self.construction_id
            row["marginal"] = ma
            row["marginal_a"] = ma
            row["strategy"] = self.name
            row["why"] = (
                f"V3-B A: M_A={ma:.1f} (M_D={float(md):.1f} − M_D(q*)="
                f"{ainfo['cross_alt_marginal']:.1f}"
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
