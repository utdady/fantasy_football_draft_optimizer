"""Real-DB latency: board state → strategy.recommend()."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import create_draft, is_user_turn, record_user_pick, snapshot
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies import get_strategy


def _advance_to_user_pick(conn, draft_id: str, seed: int, target_user_picks: int = 1) -> dict:
    """Advance until the Nth user turn (1-indexed), stopping before the pick."""
    seen = 0
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            raise RuntimeError("draft completed before target user pick")
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            seen += 1
            if seen >= target_user_picks:
                return {
                    "overall": int(draft_row["current_pick"]),
                    "n_remaining": len(remaining_ranked(conn, draft_id)),
                    "n_candidates": len(candidate_pool(conn, draft_id)),
                }
            # autodraft previous user picks with marginal so we land on later boards
            recs = get_strategy("marginal").recommend(conn, draft_id, n=1)
            record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")
        else:
            overall = int(draft_row["current_pick"])
            cpu_pick(conn, draft_id, rng=pick_rng(seed, overall), policy="noisy_adp")


def _percentile(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    if len(ys) == 1:
        return ys[0]
    k = (len(ys) - 1) * p
    f = int(k)
    c = min(f + 1, len(ys) - 1)
    if f == c:
        return ys[f]
    return ys[f] + (ys[c] - ys[f]) * (k - f)


def bench_strategy(
    conn,
    *,
    strategy: str,
    slot: int = 1,
    seed: int = 0,
    user_pick_index: int = 1,
    warmup: int = 2,
    repeats: int = 30,
    preset: str = "league_default",
) -> dict:
    draft_id = create_draft(
        conn, user_slot=slot, user_name="latency", roster_preset=preset
    )
    meta = _advance_to_user_pick(conn, draft_id, seed, target_user_picks=user_pick_index)
    strat = get_strategy(strategy)

    # cold
    t0 = time.perf_counter()
    strat.recommend(conn, draft_id, n=1)
    cold_ms = (time.perf_counter() - t0) * 1000.0

    for _ in range(max(0, warmup)):
        strat.recommend(conn, draft_id, n=1)

    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        recs = strat.recommend(conn, draft_id, n=1)
        samples.append((time.perf_counter() - t0) * 1000.0)
    rec = recs[0] if recs else {}
    return {
        "strategy": strategy,
        "slot": slot,
        "user_pick_index": user_pick_index,
        "overall": meta["overall"],
        "n_remaining": meta["n_remaining"],
        "n_candidates": meta["n_candidates"],
        "picks_until_next": rec.get("picks_until_next"),
        "cold_ms": round(cold_ms, 2),
        "warm_p50_ms": round(_percentile(samples, 0.50), 2),
        "warm_p95_ms": round(_percentile(samples, 0.95), 2),
        "warm_p99_ms": round(_percentile(samples, 0.99), 2),
        "warm_mean_ms": round(statistics.mean(samples), 2) if samples else 0.0,
        "warmup": warmup,
        "repeats": repeats,
    }


def run_latency_suite(
    *,
    strategies: list[str] | None = None,
    slot: int = 1,
    seed: int = 0,
    boards: list[int] | None = None,
    repeats: int = 25,
    conn=None,
    db_path=None,
) -> dict:
    strategies = strategies or ["marginal", "marginal_vor", "marginal_v2"]
    boards = boards or [1, 2, 3]  # R1, R2-ish, R3-ish user picks at slot 1
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    n_players = conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"]
    if n_players == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")
    rows = []
    try:
        for strat in strategies:
            for upi in boards:
                print(f"... latency {strat} user_pick={upi}", flush=True)
                rows.append(
                    bench_strategy(
                        conn,
                        strategy=strat,
                        slot=slot,
                        seed=seed,
                        user_pick_index=upi,
                        repeats=repeats,
                    )
                )
        return {
            "n_players_db": n_players,
            "slot": slot,
            "seed": seed,
            "repeats": repeats,
            "rows": rows,
        }
    finally:
        if own:
            conn.close()


def to_markdown(report: dict) -> str:
    lines = [
        "# Real-DB recommendation latency",
        "",
        f"- players in DB: **{report['n_players_db']}**",
        f"- slot: **{report['slot']}**",
        f"- warm repeats: **{report['repeats']}**",
        f"- seed: `{report['seed']}`",
        "",
        "| strategy | user pick # | overall | remaining | candidates | wait | cold ms | p50 | p95 | p99 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in report["rows"]:
        lines.append(
            f"| {r['strategy']} | {r['user_pick_index']} | {r['overall']} | "
            f"{r['n_remaining']} | {r['n_candidates']} | {r.get('picks_until_next')} | "
            f"{r['cold_ms']:.1f} | {r['warm_p50_ms']:.1f} | {r['warm_p95_ms']:.1f} | "
            f"{r['warm_p99_ms']:.1f} |"
        )
    lines.extend(
        [
            "",
            "Threshold: should feel near-instant on a ~90s draft clock "
            "(comfortable if warm p95 ≪ 1–2s).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Real-DB strategy recommend latency")
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--repeats", type=int, default=25)
    parser.add_argument("--boards", type=str, default="1,2,3")
    parser.add_argument(
        "--strategies",
        type=str,
        default="marginal,marginal_vor,marginal_v2",
    )
    parser.add_argument("--out", type=str, default="results/latency_real_db.md")
    args = parser.parse_args()
    boards = [int(x.strip()) for x in args.boards.split(",") if x.strip()]
    strategies = [s.strip() for s in args.strategies.split(",") if s.strip()]
    report = run_latency_suite(
        strategies=strategies,
        slot=args.slot,
        seed=args.seed,
        boards=boards,
        repeats=args.repeats,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    for r in report["rows"]:
        if r["strategy"] == "marginal_v2":
            print(
                f"v2 pick#{r['user_pick_index']}: p50={r['warm_p50_ms']:.0f}ms "
                f"p95={r['warm_p95_ms']:.0f}ms remaining={r['n_remaining']}"
            )


if __name__ == "__main__":
    main()
