"""V2-alpha: raw two-pick starter EV under one deterministic ADP-greedy future."""

from __future__ import annotations

from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import _draft_row, draft_roster
from draftopt.lookahead import as_lineup_player, two_pick_ev
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies.marginal import _user_roster_players


class MarginalV2Strategy:
    """
    Experimental V2-alpha.

    For each candidate p at overall t, with next user pick t':
      take p → ADP-greedy CPU for (t'−t−1) picks → q = best raw marginal →
      EV = lineup_ev(R+p+q) (raw ESPN starter points).

    UI default remains raw marginal; this is opt-in via strategy name.
    """

    name = "marginal_v2"

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        draft = _draft_row(conn, draft_id)
        slots = (draft_roster(draft).get("slots") or {})
        n_teams = int(draft["n_teams"])
        n_rounds = int(draft["n_rounds"])
        user_slot = int(draft["user_slot"])
        overall = int(draft["current_pick"])

        roster = [
            p
            for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
            if p["projection_quality"] == "high"
        ]
        remaining = remaining_ranked(conn, draft_id)

        nxt = next_user_overall(
            overall, user_slot, n_teams, n_rounds=n_rounds
        )
        until = picks_until_next(
            overall, user_slot, n_teams, n_rounds=n_rounds
        )
        n_cpu = int(until) if until is not None else 0
        has_next = nxt is not None

        scored: list[dict] = []
        for cand in candidate_pool(conn, draft_id):
            lined = as_lineup_player(cand)
            if lined["projection_quality"] != "high" or lined["season_points"] <= 0:
                continue

            if not has_next:
                ev = lineup_ev(roster + [lined], slots).total
                item = dict(cand)
                item["proj_espn"] = lined["season_points"]
                item["season_points"] = lined["season_points"]
                item["projection_source"] = lined["projection_source"]
                item["projection_quality"] = lined["projection_quality"]
                item["marginal"] = round(ev, 2)
                item["ev_two_pick"] = round(ev, 2)
                item["one_pick_ev"] = round(ev, 2)
                item["next_user_pick"] = None
                item["picks_until_next"] = None
                item["q_player"] = None
                item["why"] = (
                    f"last pick window; raw starter EV {ev:.1f} (no next user pick)"
                )
                item["strategy"] = self.name
                scored.append(item)
                continue

            result = two_pick_ev(
                roster,
                cand,
                remaining,
                slots,
                n_cpu_picks=n_cpu,
            )
            if not result["ok"]:
                continue
            q = result.get("q")
            q_name = q.get("name") if q else None
            q_pos = (q.get("position") or "?") if q else None
            item = dict(cand)
            item["proj_espn"] = lined["season_points"]
            item["season_points"] = lined["season_points"]
            item["projection_source"] = lined["projection_source"]
            item["projection_quality"] = lined["projection_quality"]
            item["marginal"] = round(float(result["ev"]), 2)
            item["ev_two_pick"] = round(float(result["ev"]), 2)
            item["one_pick_ev"] = round(float(result["one_pick"]), 2)
            item["next_user_pick"] = nxt
            item["picks_until_next"] = n_cpu
            item["q_player"] = q_name
            item["q_position"] = q_pos
            if q_name:
                item["why"] = (
                    f"two-pick EV {result['ev']:.1f} "
                    f"(take now → ADP×{n_cpu} → {q_name} {q_pos} at #{nxt})"
                )
            else:
                item["why"] = (
                    f"two-pick EV {result['ev']:.1f} "
                    f"(no survivor q after ADP×{n_cpu}; one-pick fallback)"
                )
            item["strategy"] = self.name
            scored.append(item)

        scored.sort(
            key=lambda r: (
                -(r.get("marginal") or 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("name") or "",
            )
        )
        return scored[:n]
