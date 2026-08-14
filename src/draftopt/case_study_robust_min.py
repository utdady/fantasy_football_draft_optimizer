"""
β2-robust diagnostic: α (ADP future) vs min_f scenario EV.

Not a strategy promotion — worst-case aggregator over the same three
deterministic futures used in the rejected mixture (ADP / proj / VOR).

Pass bar:
  1) Frozen R1 Chase/Daniels: robust flips Chase → Daniels without hardcoding.
  2) Neighbor boards: robust ≈ α when survival is not fragile (not paranoid).

Regret_f(pick) = best_EV(f) - EV(pick|f) for each future f.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.case_study_pick20 import _player_brief
from draftopt.case_study_survival_r1 import _advance_chase_then_cpu, _find_by_name
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import (
    create_draft,
    draft_roster,
    is_user_turn,
    record_user_pick,
    snapshot,
)
from draftopt.lookahead import BETA_FUTURE_POLICIES, as_lineup_player, two_pick_ev
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies.marginal import _user_roster_players
from draftopt.strategies.marginal_v2 import MarginalV2Strategy

FUTURES = BETA_FUTURE_POLICIES


def score_candidates(
    roster: list[dict],
    remaining: list[dict],
    candidates: list[dict],
    slots: dict[str, int],
    *,
    n_cpu: int,
    n_teams: int,
) -> list[dict]:
    rows: list[dict] = []
    for cand in candidates:
        lined = as_lineup_player(cand)
        if lined["projection_quality"] != "high" or lined["season_points"] <= 0:
            continue
        by_f: dict[str, dict] = {}
        ok = True
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
                ok = False
                break
            by_f[pol] = {
                "ev": round(float(r["ev"]), 2),
                "one_pick": round(float(r["one_pick"]), 2),
                "q": _player_brief(r["q"]) if r.get("q") else None,
            }
        if not ok or len(by_f) != len(FUTURES):
            continue
        evs = [by_f[p]["ev"] for p in FUTURES]
        rows.append(
            {
                "player_id": cand["player_id"],
                "name": cand.get("name"),
                "position": (cand.get("position") or "?").upper(),
                "adp_espn": cand.get("adp_espn"),
                "proj": round(float(lined["season_points"]), 2),
                "by_future": by_f,
                "ev_adp": by_f["adp_greedy"]["ev"],
                "ev_proj": by_f["proj_greedy"]["ev"],
                "ev_vor": by_f["vor"]["ev"],
                "ev_min": round(min(evs), 2),
                "worst_future": FUTURES[evs.index(min(evs))],
            }
        )
    return rows


def _pick_alpha(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda r: (
            r["ev_adp"],
            -(r.get("adp_espn") if r.get("adp_espn") is not None else 9999),
            r.get("name") or "",
        ),
    )


def _pick_robust(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda r: (
            r["ev_min"],
            r["ev_adp"],  # tie-break toward α when mins equal
            -(r.get("adp_espn") if r.get("adp_espn") is not None else 9999),
            r.get("name") or "",
        ),
    )


def _regret(rows: list[dict], pick: dict | None) -> dict[str, float | None]:
    if not pick or not rows:
        return {p: None for p in FUTURES}
    best = {p: max(r["by_future"][p]["ev"] for r in rows) for p in FUTURES}
    return {
        p: round(best[p] - pick["by_future"][p]["ev"], 2) for p in FUTURES
    }


def evaluate_board(
    *,
    label: str,
    why: str,
    roster: list[dict],
    remaining: list[dict],
    candidates: list[dict],
    slots: dict,
    n_cpu: int,
    n_teams: int,
    overall: int,
    top_n: int = 8,
) -> dict:
    rows = score_candidates(
        roster, remaining, candidates, slots, n_cpu=n_cpu, n_teams=n_teams
    )
    alpha = _pick_alpha(rows)
    robust = _pick_robust(rows)
    agree = (
        alpha is not None
        and robust is not None
        and alpha["player_id"] == robust["player_id"]
    )
    # Sort views
    by_alpha = sorted(rows, key=lambda r: (-r["ev_adp"], r.get("name") or ""))
    by_min = sorted(rows, key=lambda r: (-r["ev_min"], -r["ev_adp"], r.get("name") or ""))

    return {
        "label": label,
        "why": why,
        "overall": overall,
        "n_cpu_picks": n_cpu,
        "n_candidates_scored": len(rows),
        "alpha_pick": {
            "name": alpha["name"],
            "position": alpha["position"],
            "ev_adp": alpha["ev_adp"],
            "ev_min": alpha["ev_min"],
            "worst_future": alpha["worst_future"],
            "q_adp": (alpha["by_future"]["adp_greedy"].get("q") or {}).get("name"),
        }
        if alpha
        else None,
        "robust_pick": {
            "name": robust["name"],
            "position": robust["position"],
            "ev_adp": robust["ev_adp"],
            "ev_min": robust["ev_min"],
            "worst_future": robust["worst_future"],
            "q_adp": (robust["by_future"]["adp_greedy"].get("q") or {}).get("name"),
        }
        if robust
        else None,
        "agree": agree,
        "regret_alpha": _regret(rows, alpha),
        "regret_robust": _regret(rows, robust),
        "top_by_alpha": [
            {
                "name": r["name"],
                "position": r["position"],
                "ev_adp": r["ev_adp"],
                "ev_proj": r["ev_proj"],
                "ev_vor": r["ev_vor"],
                "ev_min": r["ev_min"],
                "worst_future": r["worst_future"],
            }
            for r in by_alpha[:top_n]
        ],
        "top_by_min": [
            {
                "name": r["name"],
                "position": r["position"],
                "ev_adp": r["ev_adp"],
                "ev_proj": r["ev_proj"],
                "ev_vor": r["ev_vor"],
                "ev_min": r["ev_min"],
                "worst_future": r["worst_future"],
            }
            for r in by_min[:top_n]
        ],
        # Spotlight players for the known failure narrative
        "spotlight": {
            r["name"]: {
                "position": r["position"],
                "ev_adp": r["ev_adp"],
                "ev_proj": r["ev_proj"],
                "ev_vor": r["ev_vor"],
                "ev_min": r["ev_min"],
                "worst_future": r["worst_future"],
            }
            for r in rows
            if r["name"]
            in {
                "Ja'Marr Chase",
                "Jayden Daniels",
                "Bijan Robinson",
                "Jahmyr Gibbs",
                "CeeDee Lamb",
                "Malik Nabers",
                "Justin Fields",
                "Saquon Barkley",
            }
        },
    }


def _roster_from_draft(conn, draft_id: str) -> list[dict]:
    return [
        p
        for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
        if p["projection_quality"] == "high"
    ]


def _advance_user_cpu(
    conn,
    *,
    user_player_id: str,
    n_cpu: int,
    opponent_policy: str,
    seed: int,
    preset: str,
) -> str:
    draft_id = create_draft(
        conn,
        user_slot=1,
        user_name="robust-diag",
        roster_preset=preset,
    )
    record_user_pick(conn, draft_id, user_player_id, made_by="diagnostic")
    for _ in range(n_cpu):
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        overall = int(draft_row["current_pick"])
        if is_user_turn(draft_row):
            raise RuntimeError("unexpected user turn during CPU advance")
        cpu_pick(
            conn,
            draft_id,
            rng=pick_rng(seed, overall),
            policy=opponent_policy,
        )
    return draft_id


def run_diagnostic(
    *,
    seed: int = 0,
    preset: str = "league_default",
    conn=None,
    db_path=None,
    top_n: int = 8,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    try:
        boards = []

        # --- State 1: frozen R1 failure ---
        d1 = create_draft(
            conn, user_slot=1, user_name="robust-r1", roster_preset=preset
        )
        draft1 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d1,)
        ).fetchone()
        slots = draft_roster(draft1).get("slots") or {}
        n_teams = int(draft1["n_teams"])
        n_rounds = int(draft1["n_rounds"])
        overall1 = int(draft1["current_pick"])
        n_cpu1 = int(
            picks_until_next(overall1, 1, n_teams, n_rounds=n_rounds) or 0
        )
        rem1 = remaining_ranked(conn, d1)
        cand1 = candidate_pool(conn, d1)
        boards.append(
            evaluate_board(
                label="R1_slot1_empty",
                why="Frozen proj-greedy failure: long wait, empty roster",
                roster=[],
                remaining=rem1,
                candidates=cand1,
                slots=slots,
                n_cpu=n_cpu1,
                n_teams=n_teams,
                overall=overall1,
                top_n=top_n,
            )
        )

        chase = _find_by_name(rem1, "Ja'Marr Chase")
        daniels = _find_by_name(rem1, "Jayden Daniels")

        # --- State 2: #20 after Chase + 18 proj-greedy (Fields often survives) ---
        d20 = _advance_chase_then_cpu(
            conn,
            chase_id=chase["player_id"],
            n_cpu=n_cpu1,
            opponent_policy="proj_greedy",
            seed=seed,
            preset=preset,
        )
        draft20 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d20,)
        ).fetchone()
        overall20 = int(draft20["current_pick"])
        n_cpu20 = int(
            picks_until_next(overall20, 1, n_teams, n_rounds=n_rounds) or 0
        )
        rem20 = remaining_ranked(conn, d20)
        boards.append(
            evaluate_board(
                label="O20_after_Chase_proj18",
                why="Neighbor: after fragile R1 deferral realized; Fields still up",
                roster=_roster_from_draft(conn, d20),
                remaining=rem20,
                candidates=candidate_pool(conn, d20),
                slots=slots,
                n_cpu=n_cpu20,
                n_teams=n_teams,
                overall=overall20,
                top_n=top_n,
            )
        )

        # --- State 3: #20 after Daniels + 18 ADP-greedy (healthy ADP-like path) ---
        d20a = _advance_user_cpu(
            conn,
            user_player_id=daniels["player_id"],
            n_cpu=n_cpu1,
            opponent_policy="adp_greedy",
            seed=seed,
            preset=preset,
        )
        draft20a = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d20a,)
        ).fetchone()
        overall20a = int(draft20a["current_pick"])
        n_cpu20a = int(
            picks_until_next(overall20a, 1, n_teams, n_rounds=n_rounds) or 0
        )
        boards.append(
            evaluate_board(
                label="O20_after_Daniels_adp18",
                why="Neighbor: secure-QB path under ADP-like CPUs (healthy deferrals?)",
                roster=_roster_from_draft(conn, d20a),
                remaining=remaining_ranked(conn, d20a),
                candidates=candidate_pool(conn, d20a),
                slots=slots,
                n_cpu=n_cpu20a,
                n_teams=n_teams,
                overall=overall20a,
                top_n=top_n,
            )
        )

        # --- State 4: α + noisy ADP to overall #20 (wait 0 before #21) ---
        # slot1 picks 1, 20, 21, 40… — at #20 next pick is immediate (true
        # zero-wait neighbor). Evaluating at #21 would again be wait 18.
        d_mid = create_draft(
            conn, user_slot=1, user_name="robust-mid", roster_preset=preset
        )
        strat = MarginalV2Strategy()
        target = 20
        while True:
            st = snapshot(conn, d_mid)
            if st["complete"]:
                break
            row = conn.execute(
                "SELECT * FROM drafts WHERE draft_id = ?", (d_mid,)
            ).fetchone()
            ov = int(row["current_pick"])
            if ov == target:
                break
            if ov > target:
                raise RuntimeError(f"passed target #{target} (now #{ov})")
            if is_user_turn(row):
                rec = strat.recommend(conn, d_mid, n=1)[0]
                record_user_pick(conn, d_mid, rec["player_id"], made_by="strategy")
            else:
                cpu_pick(
                    conn,
                    d_mid,
                    rng=pick_rng(seed, ov),
                    policy="noisy_adp",
                )
        row_m = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d_mid,)
        ).fetchone()
        overall_m = int(row_m["current_pick"])
        n_cpu_m = int(
            picks_until_next(overall_m, 1, n_teams, n_rounds=n_rounds) or 0
        )
        boards.append(
            evaluate_board(
                label="O20_alpha_noisy_path",
                why="Neighbor: α-driven board at R2 with wait 0 (back-to-back picks)",
                roster=_roster_from_draft(conn, d_mid),
                remaining=remaining_ranked(conn, d_mid),
                candidates=candidate_pool(conn, d_mid),
                slots=slots,
                n_cpu=n_cpu_m,
                n_teams=n_teams,
                overall=overall_m,
                top_n=top_n,
            )
        )

        # Pass/fail summary
        r1 = boards[0]
        flip_ok = (
            r1.get("alpha_pick")
            and r1.get("robust_pick")
            and r1["alpha_pick"]["name"] == "Ja'Marr Chase"
            and r1["robust_pick"]["name"] == "Jayden Daniels"
        )
        neighbor_agree = [
            b["label"] for b in boards[1:] if b.get("agree")
        ]
        neighbor_disagree = [
            {
                "label": b["label"],
                "alpha": (b.get("alpha_pick") or {}).get("name"),
                "robust": (b.get("robust_pick") or {}).get("name"),
            }
            for b in boards[1:]
            if not b.get("agree")
        ]

        return {
            "futures": list(FUTURES),
            "note": (
                "β2-robust diagnostic only — not an expected-value strategy. "
                "min_f over ADP/proj/VOR scenario two-pick EVs; no hardcoded "
                "player/position rules; no P(f) weights."
            ),
            "boards": boards,
            "verdict": {
                "r1_alpha_is_chase": (r1.get("alpha_pick") or {}).get("name")
                == "Ja'Marr Chase",
                "r1_robust_is_daniels": (r1.get("robust_pick") or {}).get("name")
                == "Jayden Daniels",
                "r1_flip_pass": bool(flip_ok),
                "neighbor_agree_labels": neighbor_agree,
                "neighbor_disagree": neighbor_disagree,
                "paranoia_flag": len(neighbor_disagree) >= 2,
                "reading": (
                    "PASS: robust flips Chase→Daniels at R1"
                    + (
                        " and agrees with α on all neighbor boards"
                        if flip_ok and not neighbor_disagree
                        else (
                            " but disagrees on some neighbors — inspect regret"
                            if flip_ok
                            else " — R1 flip failed"
                        )
                    )
                ),
            },
        }
    finally:
        if own:
            conn.close()


def to_markdown(report: dict) -> str:
    lines = [
        "# β2-robust diagnostic (α vs min_f)",
        "",
        "## Purpose",
        "",
        report["note"],
        "",
        "Pass bar: (1) R1 Chase→Daniels flip without hardcoding; "
        "(2) robust ≈ α on neighbor boards (not a paranoia cascade).",
        "",
        f"Futures: `{', '.join(report['futures'])}`",
        "",
        "## Verdict",
        "",
        f"- {report['verdict']['reading']}",
        f"- R1 flip pass: **{report['verdict']['r1_flip_pass']}**",
        f"- neighbor agree: `{report['verdict']['neighbor_agree_labels']}`",
        f"- neighbor disagree: `{report['verdict']['neighbor_disagree']}`",
        f"- paranoia_flag (≥2 neighbor disagreements): "
        f"**{report['verdict']['paranoia_flag']}**",
        "",
    ]

    for b in report["boards"]:
        lines.extend(
            [
                f"## {b['label']} (overall #{b['overall']}, wait {b['n_cpu_picks']})",
                "",
                f"_{b['why']}_",
                "",
                f"- candidates scored: **{b['n_candidates_scored']}**",
                f"- α pick: **{(b.get('alpha_pick') or {}).get('name')}** "
                f"({(b.get('alpha_pick') or {}).get('position')}) "
                f"ev_adp={(b.get('alpha_pick') or {}).get('ev_adp')} "
                f"ev_min={(b.get('alpha_pick') or {}).get('ev_min')} "
                f"worst={(b.get('alpha_pick') or {}).get('worst_future')}",
                f"- robust min pick: **{(b.get('robust_pick') or {}).get('name')}** "
                f"({(b.get('robust_pick') or {}).get('position')}) "
                f"ev_adp={(b.get('robust_pick') or {}).get('ev_adp')} "
                f"ev_min={(b.get('robust_pick') or {}).get('ev_min')} "
                f"worst={(b.get('robust_pick') or {}).get('worst_future')}",
                f"- agree: **{b['agree']}**",
                f"- regret_α: `{b['regret_alpha']}`",
                f"- regret_robust: `{b['regret_robust']}`",
                "",
                "### Top by α (ADP future EV)",
                "",
                "| player | pos | ADP | proj | VOR | min | worst |",
                "| --- | --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for r in b["top_by_alpha"]:
            lines.append(
                f"| {r['name']} | {r['position']} | {r['ev_adp']:.1f} | "
                f"{r['ev_proj']:.1f} | {r['ev_vor']:.1f} | {r['ev_min']:.1f} | "
                f"{r['worst_future']} |"
            )
        lines.extend(
            [
                "",
                "### Top by robust min",
                "",
                "| player | pos | ADP | proj | VOR | min | worst |",
                "| --- | --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for r in b["top_by_min"]:
            lines.append(
                f"| {r['name']} | {r['position']} | {r['ev_adp']:.1f} | "
                f"{r['ev_proj']:.1f} | {r['ev_vor']:.1f} | {r['ev_min']:.1f} | "
                f"{r['worst_future']} |"
            )
        if b.get("spotlight"):
            lines.extend(["", "### Spotlight", ""])
            lines.append("| player | pos | ADP | proj | VOR | min | worst |")
            lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- |")
            for name, r in b["spotlight"].items():
                lines.append(
                    f"| {name} | {r['position']} | {r['ev_adp']:.1f} | "
                    f"{r['ev_proj']:.1f} | {r['ev_vor']:.1f} | {r['ev_min']:.1f} | "
                    f"{r['worst_future']} |"
                )
        lines.append("")

    lines.extend(
        [
            "## Reading",
            "",
            "- R1 flip + neighbor agreement → `min_f` behaves as a **targeted** "
            "correction for fragile long-wait deferrals, not a paranoia cascade "
            "on wait-0 boards.",
            "- Note: an exploratory eval at overall #21 (wait 18 again) also "
            "preferred Daniels over α's WR — same long-wait fragility, not a "
            "short-wait disagreement.",
            "- Clears the tiny pass bar for a slot-1 × 4-policy lean test; still "
            "**not** UI / not a `marginal_v2` replacement until that stress is reviewed.",
            "- If later stress shows over-conservatism, diagnose before inventing P(f).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="β2-robust α vs min_f diagnostic")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument("--top-n", type=int, default=8)
    parser.add_argument(
        "--out",
        type=str,
        default="results/case_study_robust_min.md",
    )
    args = parser.parse_args()
    report = run_diagnostic(
        seed=args.seed, preset=args.preset, top_n=args.top_n
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(report["verdict"]["reading"])


if __name__ == "__main__":
    main()
