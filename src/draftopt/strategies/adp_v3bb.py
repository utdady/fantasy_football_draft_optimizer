"""V3-B Branch B: D's marginal plus one-step continuation C(R∪{p})."""

from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster
from draftopt.phase2.onestep_continuation import (
    CONSTRUCTION_ID,
    score_one_step,
)
from draftopt.strategies.adp_structural import AdpV3aStrategy
from draftopt.strategies.marginal import (
    MarginalValueStrategy,
    _as_lineup_player,
    _user_roster_players,
)


class AdpV3bbStrategy(AdpV3aStrategy):
    """
    B = D + one transformation: M_B = M_D(p|R) + C(R∪{p}).

    Reuses MarginalValueStrategy path for M_D; continuation is one-step only.
    """

    name = "adp_v3bb"
    construction_id = CONSTRUCTION_ID

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = draft_roster(draft).get("slots") or {}
        roster = [_as_lineup_player(p) for p in _user_roster_players(conn, draft_id)]

        d_scored = MarginalValueStrategy.recommend(self, conn, draft_id, n=10_000)
        remaining = [
            {
                "player_id": str(item["player_id"]),
                "name": item.get("name"),
                "position": (item.get("position") or "").upper(),
                "team": item.get("team"),
                "season_points": (
                    float(item["season_points"])
                    if item.get("season_points") is not None
                    else (
                        float(item["proj_espn"])
                        if item.get("proj_espn") is not None
                        else 0.0
                    )
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
            cand = {
                "player_id": str(item["player_id"]),
                "name": item.get("name"),
                "position": item.get("position"),
                "team": item.get("team"),
                "season_points": item.get("season_points") or item.get("proj_espn"),
                "adp_espn": item.get("adp_espn"),
                "ecr_fp_ppr": item.get("ecr_fp_ppr"),
            }
            s = score_one_step(
                roster=roster,
                candidate=cand,
                remaining=remaining,
                slots=slots,
            )
            # Sanity: M_D from helper should match D's scored marginal closely
            row = dict(item)
            row["marginal_d"] = float(md)
            row["continuation"] = s["continuation"]
            row["continuation_missing"] = s["continuation_missing"]
            row["continuation_player_id"] = s["continuation_player_id"]
            row["continuation_name"] = s["continuation_name"]
            row["continuation_position"] = s["continuation_position"]
            row["construction_id"] = self.construction_id
            mb = round(float(md) + float(s["continuation"]), 2)
            row["marginal"] = mb
            row["marginal_b"] = mb
            row["strategy"] = self.name
            row["why"] = (
                f"V3-B B: M_B={mb:.1f} (M_D={float(md):.1f} + C={s['continuation']:.1f}"
                f"{' missing' if s['continuation_missing'] else ''}) "
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
