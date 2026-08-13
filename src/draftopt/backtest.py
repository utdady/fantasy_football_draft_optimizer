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


@dataclass
class SimResult:
    strategy: str
    starter_pts: float
    roster_proj: float
    starter_rank: int
    roster_rank: int
    adp_value: float


def pick_rng(base_seed: int, overall: int) -> random.Random:
    """
    Deterministic RNG keyed by (sim seed, overall pick#).

    Both strategies in a paired sim use the same stream at the same pick number,
    so CPU decisions only differ when the remaining board differs (user treatment).
    """
    return random.Random((base_seed * 1_000_003) ^ (overall * 97_411))


def _team_rosters(conn, draft_id: str) -> dict[int, list[dict]]:
    rows = conn.execute(
        """
        SELECT pk.team_slot, p.player_id, p.name, p.position,
               pr.season_points AS season_points
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        LEFT JOIN projections_snapshots pr
            ON pr.player_id = p.player_id AND pr.source = 'espn'
        WHERE pk.draft_id = ?
        ORDER BY pk.overall
        """,
        (draft_id,),
    ).fetchall()
    by_team: dict[int, list[dict]] = {}
    for row in rows:
        slot = int(row["team_slot"])
        by_team.setdefault(slot, []).append(
            {
                "player_id": row["player_id"],
                "name": row["name"],
                "position": row["position"],
                # Evaluation uses ESPN projections only (not ECR proxy).
                "season_points": float(row["season_points"] or 0.0),
            }
        )
    return by_team


def _starter_ranks(conn, draft_id: str) -> dict[int, tuple[float, int]]:
    """team_slot -> (starter_pts, rank by starter pts)."""
    draft = conn.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
    slots = (draft_roster(draft).get("slots") or {})
    scored = [
        (team_slot, starter_points(roster, slots))
        for team_slot, roster in _team_rosters(conn, draft_id).items()
    ]
    scored.sort(key=lambda t: t[1], reverse=True)
    out: dict[int, tuple[float, int]] = {}
    for rank, (team_slot, pts) in enumerate(scored, start=1):
        out[team_slot] = (pts, rank)
    return out


def run_one(
    conn,
    *,
    strategy_name: str,
    user_slot: int,
    roster_preset: str,
    seed: int,
    n_rounds: int | None = None,
) -> SimResult:
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
            overall = int(draft_row["current_pick"])
            cpu_pick(conn, draft_id, rng=pick_rng(seed, overall))

    grade = grade_draft(conn, draft_id)
    user = grade["user"]
    user_slot = int(
        conn.execute("SELECT user_slot FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()[
            "user_slot"
        ]
    )
    starter_map = _starter_ranks(conn, draft_id)
    starter_pts, starter_rank = starter_map[user_slot]
    return SimResult(
        strategy=strategy_name,
        starter_pts=starter_pts,
        roster_proj=float(user["projected_points"]),
        starter_rank=starter_rank,
        roster_rank=int(user["rank"]),
        adp_value=float(user["adp_value"]),
    )


def summarize(name: str, results: list[SimResult]) -> dict:
    starters = [r.starter_pts for r in results]
    projs = [r.roster_proj for r in results]
    starter_ranks = [r.starter_rank for r in results]
    roster_ranks = [r.roster_rank for r in results]
    return {
        "strategy": name,
        "n": len(results),
        "mean_starter_pts": statistics.mean(starters) if starters else 0.0,
        "std_starter_pts": statistics.pstdev(starters) if len(starters) > 1 else 0.0,
        "mean_roster_proj": statistics.mean(projs) if projs else 0.0,
        "mean_starter_rank": statistics.mean(starter_ranks) if starter_ranks else 0.0,
        "mean_roster_rank": statistics.mean(roster_ranks) if roster_ranks else 0.0,
        # Back-compat alias: rank means starter rank (the metric we care about).
        "mean_rank": statistics.mean(starter_ranks) if starter_ranks else 0.0,
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
            sim_seed = seed + i * 1009
            for name in ("adp", "marginal"):
                result = run_one(
                    conn,
                    strategy_name=name,
                    user_slot=slot,
                    roster_preset=preset,
                    seed=sim_seed,
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
            "paired": True,
            "summaries": summaries,
            "marginal_minus_adp": marg_mean - adp_mean,
            "marginal_win_rate": wins / n if n else 0.0,
            "tie_rate": ties / n if n else 0.0,
        }
    finally:
        if own:
            conn.close()


def _print_report(report: dict) -> None:
    print(
        f"Backtest n={report['n']} slot={report['slot']} preset={report['preset']} "
        f"seed={report['seed']} paired={report.get('paired', False)}"
    )
    print(
        f"{'strategy':<12} {'mean_starter':>12} {'std':>8} {'mean_proj':>10} "
        f"{'starter_rk':>10} {'roster_rk':>9}"
    )
    for name in ("adp", "marginal"):
        s = report["summaries"][name]
        print(
            f"{name:<12} {s['mean_starter_pts']:12.1f} {s['std_starter_pts']:8.1f} "
            f"{s['mean_roster_proj']:10.1f} {s['mean_starter_rank']:10.2f} "
            f"{s['mean_roster_rank']:9.2f}"
        )
    print(f"marginal − adp starter pts: {report['marginal_minus_adp']:+.1f}")
    print(f"marginal win rate (starter pts): {report['marginal_win_rate']:.1%} (ties {report['tie_rate']:.1%})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paired ADP vs marginal backtest (shared CPU RNG per pick#)"
    )
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    report = run_backtest(n=args.n, slot=args.slot, preset=args.preset, seed=args.seed)
    _print_report(report)


if __name__ == "__main__":
    main()
