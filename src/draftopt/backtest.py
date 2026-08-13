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

DEFAULT_STRATEGIES = ("adp", "greedy", "marginal")


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

    Strategies share the same opponent policy/environment. Boards may still diverge
    after different user picks — not a locked identical draft path.
    """
    return random.Random((base_seed * 1_000_003) ^ (overall * 97_411))


def parse_slots(spec: str) -> list[int]:
    """Parse '1,5,10' or '1-10' into slot list."""
    spec = (spec or "").strip()
    if not spec:
        return [1]
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            if lo > hi:
                lo, hi = hi, lo
            out.extend(range(lo, hi + 1))
        else:
            out.append(int(part))
    # unique, stable order
    seen: set[int] = set()
    ordered: list[int] = []
    for s in out:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered or [1]


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
    n_teams: int = 10,
) -> SimResult:
    strategy = get_strategy(strategy_name)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"Bot-{strategy_name}",
        roster_preset=roster_preset,
        n_rounds=n_rounds,
        n_teams=n_teams,
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
        "median_starter_pts": statistics.median(starters) if starters else 0.0,
        "std_starter_pts": statistics.pstdev(starters) if len(starters) > 1 else 0.0,
        "mean_roster_proj": statistics.mean(projs) if projs else 0.0,
        "mean_starter_rank": statistics.mean(starter_ranks) if starter_ranks else 0.0,
        "mean_roster_rank": statistics.mean(roster_ranks) if roster_ranks else 0.0,
        "mean_rank": statistics.mean(starter_ranks) if starter_ranks else 0.0,
    }


def _pairwise(by_strategy: dict[str, list[SimResult]], challenger: str, baseline: str) -> dict:
    a = by_strategy.get(baseline) or []
    b = by_strategy.get(challenger) or []
    n = min(len(a), len(b))
    if n == 0:
        return {
            "baseline": baseline,
            "challenger": challenger,
            "mean_delta": 0.0,
            "median_delta": 0.0,
            "win_rate": 0.0,
            "tie_rate": 0.0,
        }
    deltas = [b[i].starter_pts - a[i].starter_pts for i in range(n)]
    wins = sum(1 for d in deltas if d > 1e-6)
    ties = sum(1 for d in deltas if abs(d) <= 1e-6)
    return {
        "baseline": baseline,
        "challenger": challenger,
        "mean_delta": statistics.mean(deltas),
        "median_delta": statistics.median(deltas),
        "win_rate": wins / n,
        "tie_rate": ties / n,
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
    n_teams: int = 10,
    strategies: tuple[str, ...] | list[str] = DEFAULT_STRATEGIES,
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

    names = tuple(strategies) or DEFAULT_STRATEGIES
    try:
        by_strategy: dict[str, list[SimResult]] = {name: [] for name in names}
        for i in range(n):
            if n >= 20 and (i == 0 or (i + 1) % max(1, n // 5) == 0 or i + 1 == n):
                print(f"    sim {i + 1}/{n}", flush=True)
            sim_seed = seed + i * 1009
            for name in names:
                result = run_one(
                    conn,
                    strategy_name=name,
                    user_slot=slot,
                    roster_preset=preset,
                    seed=sim_seed,
                    n_rounds=n_rounds,
                    n_teams=n_teams,
                )
                by_strategy[name].append(result)

        summaries = {k: summarize(k, v) for k, v in by_strategy.items()}
        comparisons: dict[str, dict] = {}
        if "adp" in by_strategy and "marginal" in by_strategy:
            comparisons["marginal_vs_adp"] = _pairwise(by_strategy, "marginal", "adp")
        if "greedy" in by_strategy and "marginal" in by_strategy:
            comparisons["marginal_vs_greedy"] = _pairwise(by_strategy, "marginal", "greedy")
        if "adp" in by_strategy and "greedy" in by_strategy:
            comparisons["greedy_vs_adp"] = _pairwise(by_strategy, "greedy", "adp")

        # Back-compat keys when both adp and marginal present.
        m_vs_a = comparisons.get("marginal_vs_adp") or {}
        return {
            "n": n,
            "slot": slot,
            "preset": preset,
            "seed": seed,
            "n_teams": n_teams,
            "strategies": list(names),
            "paired": True,
            "summaries": summaries,
            "comparisons": comparisons,
            "marginal_minus_adp": m_vs_a.get("mean_delta", 0.0),
            "marginal_win_rate": m_vs_a.get("win_rate", 0.0),
            "tie_rate": m_vs_a.get("tie_rate", 0.0),
        }
    finally:
        if own:
            conn.close()


def run_matrix(
    *,
    n: int = 50,
    slots: list[int] | None = None,
    preset: str = "league_default",
    seed: int = 0,
    db_path=None,
    conn=None,
    n_rounds: int | None = None,
    n_teams: int = 10,
    strategies: tuple[str, ...] | list[str] = DEFAULT_STRATEGIES,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    slot_list = slots or list(range(1, n_teams + 1))
    try:
        rows = []
        for slot in slot_list:
            print(f"... slot {slot} ({n} sims × {len(strategies)} strategies)", flush=True)
            report = run_backtest(
                n=n,
                slot=slot,
                preset=preset,
                seed=seed,
                conn=conn,
                n_rounds=n_rounds,
                n_teams=n_teams,
                strategies=strategies,
            )
            rows.append(report)
        return {
            "n": n,
            "slots": slot_list,
            "preset": preset,
            "seed": seed,
            "n_teams": n_teams,
            "strategies": list(strategies),
            "paired": True,
            "rows": rows,
        }
    finally:
        if own:
            conn.close()


def _print_report(report: dict) -> None:
    print(
        f"Backtest n={report['n']} slot={report['slot']} teams={report.get('n_teams', 10)} "
        f"preset={report['preset']} seed={report['seed']} paired={report.get('paired', False)}"
    )
    print(
        f"{'strategy':<12} {'mean_starter':>12} {'median':>8} {'std':>8} "
        f"{'starter_rk':>10} {'roster_rk':>9}"
    )
    for name in report.get("strategies") or report["summaries"].keys():
        s = report["summaries"][name]
        print(
            f"{name:<12} {s['mean_starter_pts']:12.1f} {s.get('median_starter_pts', 0):8.1f} "
            f"{s['std_starter_pts']:8.1f} {s['mean_starter_rank']:10.2f} "
            f"{s['mean_roster_rank']:9.2f}"
        )
    for key, cmp_ in (report.get("comparisons") or {}).items():
        print(
            f"{key}: mean Δ={cmp_['mean_delta']:+.1f} median Δ={cmp_['median_delta']:+.1f} "
            f"win={cmp_['win_rate']:.1%} ties={cmp_['tie_rate']:.1%}"
        )


def _print_matrix(matrix: dict) -> None:
    strats = matrix["strategies"]
    print(
        f"Matrix n={matrix['n']} teams={matrix['n_teams']} preset={matrix['preset']} "
        f"seed={matrix['seed']} slots={matrix['slots']}"
    )
    header = f"{'slot':>4}"
    for name in strats:
        header += f" {name:>10}"
    if "marginal" in strats and "adp" in strats:
        header += f" {'m-adp':>8} {'m>adp':>7}"
    if "marginal" in strats and "greedy" in strats:
        header += f" {'m-greed':>8} {'m>greed':>8}"
    print(header)
    for report in matrix["rows"]:
        line = f"{report['slot']:4d}"
        for name in strats:
            line += f" {report['summaries'][name]['mean_starter_pts']:10.1f}"
        comps = report.get("comparisons") or {}
        if "marginal_vs_adp" in comps:
            c = comps["marginal_vs_adp"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        if "marginal_vs_greedy" in comps:
            c = comps["marginal_vs_greedy"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:8.1%}"
        print(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paired strategy backtest / slot matrix (shared CPU RNG per pick#)"
    )
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--slot", type=int, default=None, help="Single slot (default 1 if no --slots)")
    parser.add_argument(
        "--slots",
        type=str,
        default=None,
        help="Matrix mode: e.g. 1,5,10 or 1-10",
    )
    parser.add_argument("--preset", default="league_default")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--teams", type=int, default=10)
    parser.add_argument(
        "--strategies",
        type=str,
        default="adp,greedy,marginal",
        help="Comma-separated: adp,greedy,marginal",
    )
    args = parser.parse_args()
    strategies = tuple(s.strip() for s in args.strategies.split(",") if s.strip())
    if args.slots is not None:
        matrix = run_matrix(
            n=args.n,
            slots=parse_slots(args.slots),
            preset=args.preset,
            seed=args.seed,
            n_teams=args.teams,
            strategies=strategies,
        )
        _print_matrix(matrix)
        return
    slot = args.slot if args.slot is not None else 1
    report = run_backtest(
        n=args.n,
        slot=slot,
        preset=args.preset,
        seed=args.seed,
        n_teams=args.teams,
        strategies=strategies,
    )
    _print_report(report)


if __name__ == "__main__":
    main()
