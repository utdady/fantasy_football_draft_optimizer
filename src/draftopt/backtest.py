from __future__ import annotations

import argparse
import random
import statistics
from dataclasses import dataclass

from draftopt import db
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import create_draft, draft_roster, is_user_turn, record_user_pick, snapshot
from draftopt.lineup import starter_points
from draftopt.strategies import get_strategy
from draftopt.strategies.marginal import _user_roster_players


@dataclass
class SimResult:
    strategy: str
    starter_pts: float
    roster_proj: float
    rank: int
    adp_value: float


def _score_user_starters(conn, draft_id: str) -> float:
    draft = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
    slots = (draft_roster(draft).get("slots") or {})
    roster = []
    for p in _user_roster_players(conn, draft_id):
        roster.append(
            {
                "player_id": p["player_id"],
                "name": p["name"],
                "position": p["position"],
                "season_points": float(p["season_points"] or 0.0),
            }
        )
    return starter_points(roster, slots)


def run_one(
    conn,
    *,
    strategy_name: str,
    user_slot: int,
    roster_preset: str,
    seed: int,
    n_rounds: int | None = None,
) -> SimResult:
    rng = random.Random(seed)
    strategy = get_strategy(strategy_name)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"Bot-{strategy_name}",
        roster_preset=roster_preset,
        n_rounds=n_rounds,
    )
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
        if is_user_turn(draft_row):
            recs = strategy.recommend(conn, draft_id, n=1)
            if not recs:
                break
            record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")
        else:
            cpu_pick(conn, draft_id, rng=rng)

    grade = grade_draft(conn, draft_id)
    user = grade["user"]
    return SimResult(
        strategy=strategy_name,
        starter_pts=_score_user_starters(conn, draft_id),
        roster_proj=float(user["projected_points"]),
        rank=int(user["rank"]),
        adp_value=float(user["adp_value"]),
    )


def summarize(name: str, results: list[SimResult]) -> dict:
    starters = [r.starter_pts for r in results]
    projs = [r.roster_proj for r in results]
    ranks = [r.rank for r in results]
    return {
        "strategy": name,
        "n": len(results),
        "mean_starter_pts": statistics.mean(starters) if starters else 0.0,
        "std_starter_pts": statistics.pstdev(starters) if len(starters) > 1 else 0.0,
        "mean_roster_proj": statistics.mean(projs) if projs else 0.0,
        "mean_rank": statistics.mean(ranks) if ranks else 0.0,
    }


def run_backtest(
    *,
    n: int = 50,
    slot: int = 1,
    preset: str = "league_default",
    seed: int = 0,
    db_path=None,
    conn=None,
    n_rounds: int | None = None,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    player_n = conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"]
    if player_n == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    try:
        by_strategy: dict[str, list[SimResult]] = {"adp": [], "marginal": []}
        for i in range(n):
            for name in ("adp", "marginal"):
                result = run_one(
                    conn,
                    strategy_name=name,
                    user_slot=slot,
                    roster_preset=preset,
                    seed=seed + i * 1009,
                    n_rounds=n_rounds,
                )
                by_strategy[name].append(result)

        summaries = {k: summarize(k, v) for k, v in by_strategy.items()}
        adp_mean = summaries["adp"]["mean_starter_pts"]
        marg_mean = summaries["marginal"]["mean_starter_pts"]
        wins = sum(
            1
            for a, m in zip(by_strategy["adp"], by_strategy["marginal"])
            if m.starter_pts > a.starter_pts
        )
        ties = sum(
            1
            for a, m in zip(by_strategy["adp"], by_strategy["marginal"])
            if abs(m.starter_pts - a.starter_pts) < 1e-6
        )
        return {
            "n": n,
            "slot": slot,
            "preset": preset,
            "seed": seed,
            "summaries": summaries,
            "marginal_minus_adp": marg_mean - adp_mean,
            "marginal_win_rate": wins / n if n else 0.0,
            "tie_rate": ties / n if n else 0.0,
        }
    finally:
        if own:
            conn.close()


def _print_report(report: dict) -> None:
    print(f"Backtest n={report['n']} slot={report['slot']} preset={report['preset']} seed={report['seed']}")
    print(f"{'strategy':<12} {'mean_starter':>12} {'std':>8} {'mean_proj':>10} {'mean_rank':>9}")
    for name in ("adp", "marginal"):
        s = report["summaries"][name]
        print(
            f"{name:<12} {s['mean_starter_pts']:12.1f} {s['std_starter_pts']:8.1f} "
            f"{s['mean_roster_proj']:10.1f} {s['mean_rank']:9.2f}"
        )
    print(f"marginal − adp starter pts: {report['marginal_minus_adp']:+.1f}")
    print(f"marginal win rate (starter pts): {report['marginal_win_rate']:.1%} (ties {report['tie_rate']:.1%})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ADP vs marginal strategies in synthetic drafts")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    report = run_backtest(n=args.n, slot=args.slot, preset=args.preset, seed=args.seed)
    _print_report(report)


if __name__ == "__main__":
    main()
