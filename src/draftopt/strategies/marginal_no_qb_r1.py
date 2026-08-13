from __future__ import annotations

from draftopt.draft.state import _draft_row, round_for_pick
from draftopt.strategies.marginal import MarginalValueStrategy


class MarginalNoQBR1Strategy:
    """
    Diagnostic control: raw marginal, but never recommend QB in round 1.

    Not a product strategy — isolates how much of the raw-marginal edge is
    the R1-QB / ESPN-projection artifact.
    """

    name = "marginal_no_qb_r1"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        rnd = round_for_pick(int(draft["current_pick"]), int(draft["n_teams"]))
        # Pull extra so filtering still yields n recs.
        want = n if rnd != 1 else max(n * 5, 15)
        raw = MarginalValueStrategy().recommend(conn, draft_id, n=want)
        if rnd == 1:
            raw = [r for r in raw if (r.get("position") or "").upper() != "QB"]
        for item in raw:
            item["strategy"] = self.name
            why = item.get("why") or ""
            if rnd == 1 and "no-QB R1" not in why:
                item["why"] = f"{why} [no-QB R1 control]"
        return raw[:n]
