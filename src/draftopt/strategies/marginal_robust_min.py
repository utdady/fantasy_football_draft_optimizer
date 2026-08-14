"""β2-robust diagnostic: min over ADP / proj / VOR two-pick scenario EVs.

Not an expected-value strategy and not UI-default. Worst-case aggregator over
the same deterministic futures used in rejected mixture-β.
"""

from __future__ import annotations

from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import _draft_row, draft_roster
from draftopt.lookahead import BETA_FUTURE_POLICIES, as_lineup_player, two_pick_ev
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies.marginal import _user_roster_players

FUTURES = BETA_FUTURE_POLICIES


class MarginalRobustMinStrategy:
    """
    Experimental β2-robust diagnostic.

    Score each candidate p by:
      EV_robust(p) = min_f two_pick_ev(p | future_policy=f)
    for f in {adp_greedy, proj_greedy, vor}.

    UI default remains raw marginal; opt-in only.
    """

    name = "robust_min"

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
                item["ev_min"] = round(ev, 2)
                item["one_pick_ev"] = round(ev, 2)
                item["ev_by_future"] = None
                item["scenario_spread"] = 0.0
                item["worst_future"] = None
                item["next_user_pick"] = None
                item["picks_until_next"] = None
                item["q_player"] = None
                item["why"] = (
                    f"last pick window; raw starter EV {ev:.1f} (no next user pick)"
                )
                item["strategy"] = self.name
                scored.append(item)
                continue

            by_future: dict[str, dict] = {}
            ok_all = True
            for pol in FUTURES:
                r = two_pick_ev(
                    roster,
                    cand,
                    remaining,
                    slots,
                    n_cpu_picks=n_cpu,
                    future_policy=pol,
                    n_teams=n_teams,
                )
                if not r.get("ok"):
                    ok_all = False
                    break
                by_future[pol] = r
            if not ok_all:
                continue

            evs = {pol: float(r["ev"]) for pol, r in by_future.items()}
            ev_min = min(evs.values())
            ev_max = max(evs.values())
            worst = min(evs, key=evs.get)
            # Representative q from ADP future (diagnostics).
            q = by_future["adp_greedy"].get("q")
            q_name = q.get("name") if q else None
            q_pos = (q.get("position") or "?") if q else None
            one_pick = float(by_future["adp_greedy"]["one_pick"])

            item = dict(cand)
            item["proj_espn"] = lined["season_points"]
            item["season_points"] = lined["season_points"]
            item["projection_source"] = lined["projection_source"]
            item["projection_quality"] = lined["projection_quality"]
            item["marginal"] = round(ev_min, 2)
            item["ev_two_pick"] = round(ev_min, 2)
            item["ev_min"] = round(ev_min, 2)
            item["ev_max"] = round(ev_max, 2)
            item["one_pick_ev"] = round(one_pick, 2)
            item["ev_by_future"] = {pol: round(v, 2) for pol, v in evs.items()}
            item["scenario_spread"] = round(ev_max - ev_min, 2)
            item["worst_future"] = worst
            item["next_user_pick"] = nxt
            item["picks_until_next"] = n_cpu
            item["q_player"] = q_name
            item["q_position"] = q_pos
            fut_txt = ", ".join(f"{k}={v:.0f}" for k, v in sorted(evs.items()))
            item["why"] = (
                f"robust min EV {ev_min:.1f} [{fut_txt}] "
                f"spread={ev_max - ev_min:.1f} worst={worst}"
            )
            item["strategy"] = self.name
            scored.append(item)

        scored.sort(
            key=lambda r: (
                -(r.get("marginal") or 0.0),
                -(r.get("ev_by_future") or {}).get("adp_greedy", 0.0),
                r.get("adp_espn") is None,
                r.get("adp_espn") if r.get("adp_espn") is not None else 9999,
                r.get("name") or "",
            )
        )
        return scored[:n]
