from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from draftopt import db
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import create_draft, draft_roster, is_user_turn, record_user_pick, snapshot
from draftopt.lineup import starter_points
from draftopt.strategies import get_strategy

DEFAULT_STRATEGIES = ("adp", "greedy", "marginal")
ABLATION_VOR_STRATEGIES = ("adp", "marginal", "marginal_no_qb_r1", "marginal_vor")
POS_ORDER = ("QB", "RB", "WR", "TE", "DST", "K")


@dataclass
class SimResult:
    strategy: str
    starter_pts: float
    roster_proj: float
    starter_rank: int
    roster_rank: int
    adp_value: float
    picks: list[dict] = field(default_factory=list)


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
                "season_points": float(row["season_points"] or 0.0),
            }
        )
    return by_team


def _starter_ranks(conn, draft_id: str) -> dict[int, tuple[float, int]]:
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


def _user_pick_log(conn, draft_id: str, user_slot: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT pk.round, pk.overall, p.player_id, p.name, p.position,
               pr.season_points AS proj_espn, a.adp AS adp_espn
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        LEFT JOIN projections_snapshots pr
            ON pr.player_id = p.player_id AND pr.source = 'espn'
        LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
        WHERE pk.draft_id = ? AND pk.team_slot = ?
        ORDER BY pk.overall
        """,
        (draft_id, user_slot),
    ).fetchall()
    out = []
    for row in rows:
        out.append(
            {
                "round": int(row["round"]),
                "overall": int(row["overall"]),
                "player_id": row["player_id"],
                "name": row["name"],
                "position": (row["position"] or "?").upper(),
                "proj_espn": float(row["proj_espn"]) if row["proj_espn"] is not None else None,
                "adp_espn": float(row["adp_espn"]) if row["adp_espn"] is not None else None,
            }
        )
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
    opponent_policy: str = "noisy_adp",
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
            cpu_pick(
                conn,
                draft_id,
                rng=pick_rng(seed, overall),
                policy=opponent_policy,
            )

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
        picks=_user_pick_log(conn, draft_id, user_slot),
    )


def _position_stats(results: list[SimResult]) -> dict:
    pos_counts: Counter[str] = Counter()
    by_round: dict[int, Counter[str]] = defaultdict(Counter)
    proj_by_pos: dict[str, list[float]] = defaultdict(list)
    adp_by_pos: dict[str, list[float]] = defaultdict(list)
    for r in results:
        for p in r.picks:
            pos = p["position"]
            pos_counts[pos] += 1
            by_round[int(p["round"])][pos] += 1
            if p.get("proj_espn") is not None:
                proj_by_pos[pos].append(float(p["proj_espn"]))
            if p.get("adp_espn") is not None:
                adp_by_pos[pos].append(float(p["adp_espn"]))
    total = sum(pos_counts.values()) or 1
    share = {pos: pos_counts.get(pos, 0) / total for pos in POS_ORDER if pos_counts.get(pos, 0)}
    # include any unexpected positions
    for pos, n in pos_counts.items():
        if pos not in share:
            share[pos] = n / total
    round_share: dict[str, dict[str, float]] = {}
    for rnd, counts in sorted(by_round.items()):
        t = sum(counts.values()) or 1
        round_share[str(rnd)] = {pos: counts[pos] / t for pos in sorted(counts)}
    mean_proj = {
        pos: statistics.mean(vals) for pos, vals in proj_by_pos.items() if vals
    }
    mean_adp = {pos: statistics.mean(vals) for pos, vals in adp_by_pos.items() if vals}
    return {
        "position_share": share,
        "position_counts": dict(pos_counts),
        "by_round_share": round_share,
        "mean_proj_by_pos": mean_proj,
        "mean_adp_by_pos": mean_adp,
    }


def summarize(name: str, results: list[SimResult]) -> dict:
    starters = [r.starter_pts for r in results]
    projs = [r.roster_proj for r in results]
    starter_ranks = [r.starter_rank for r in results]
    roster_ranks = [r.roster_rank for r in results]
    out = {
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
    out.update(_position_stats(results))
    return out


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
        "std_delta": statistics.pstdev(deltas) if len(deltas) > 1 else 0.0,
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
    opponent_policy: str = "noisy_adp",
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
                    opponent_policy=opponent_policy,
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
        if "adp" in by_strategy and "marginal_vor" in by_strategy:
            comparisons["marginal_vor_vs_adp"] = _pairwise(by_strategy, "marginal_vor", "adp")
        if "adp" in by_strategy and "marginal_no_qb_r1" in by_strategy:
            comparisons["marginal_no_qb_r1_vs_adp"] = _pairwise(
                by_strategy, "marginal_no_qb_r1", "adp"
            )
        if "marginal" in by_strategy and "marginal_vor" in by_strategy:
            comparisons["marginal_vor_vs_marginal"] = _pairwise(
                by_strategy, "marginal_vor", "marginal"
            )
        if "adp" in by_strategy and "marginal_v2" in by_strategy:
            comparisons["marginal_v2_vs_adp"] = _pairwise(
                by_strategy, "marginal_v2", "adp"
            )
        if "marginal" in by_strategy and "marginal_v2" in by_strategy:
            comparisons["marginal_v2_vs_marginal"] = _pairwise(
                by_strategy, "marginal_v2", "marginal"
            )
        if "marginal_vor" in by_strategy and "marginal_v2" in by_strategy:
            comparisons["marginal_v2_vs_marginal_vor"] = _pairwise(
                by_strategy, "marginal_v2", "marginal_vor"
            )
        if "marginal" in by_strategy and "marginal_v2_beta" in by_strategy:
            comparisons["marginal_v2_beta_vs_marginal"] = _pairwise(
                by_strategy, "marginal_v2_beta", "marginal"
            )
        if "marginal_v2" in by_strategy and "marginal_v2_beta" in by_strategy:
            comparisons["marginal_v2_beta_vs_marginal_v2"] = _pairwise(
                by_strategy, "marginal_v2_beta", "marginal_v2"
            )

        m_vs_a = comparisons.get("marginal_vs_adp") or {}
        return {
            "n": n,
            "slot": slot,
            "preset": preset,
            "seed": seed,
            "n_teams": n_teams,
            "opponent_policy": opponent_policy,
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
    opponent_policy: str = "noisy_adp",
    on_slot=None,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    slot_list = slots or list(range(1, n_teams + 1))
    try:
        rows = []
        for slot in slot_list:
            print(
                f"... slot {slot} ({n} sims × {len(strategies)} strategies; "
                f"cpu={opponent_policy})",
                flush=True,
            )
            report = run_backtest(
                n=n,
                slot=slot,
                preset=preset,
                seed=seed,
                conn=conn,
                n_rounds=n_rounds,
                n_teams=n_teams,
                strategies=strategies,
                opponent_policy=opponent_policy,
            )
            rows.append(report)
            if on_slot is not None:
                on_slot(report, rows)
        return {
            "n": n,
            "slots": slot_list,
            "preset": preset,
            "seed": seed,
            "n_teams": n_teams,
            "opponent_policy": opponent_policy,
            "strategies": list(strategies),
            "paired": True,
            "rows": rows,
        }
    finally:
        if own:
            conn.close()


def _fmt_share(share: dict[str, float]) -> str:
    parts = []
    for pos in POS_ORDER:
        if pos in share:
            parts.append(f"{pos} {share[pos]:.0%}")
    for pos, v in share.items():
        if pos not in POS_ORDER:
            parts.append(f"{pos} {v:.0%}")
    return ", ".join(parts) if parts else "(none)"


def _print_position_mix(report: dict) -> None:
    print("Position mix (user picks, all sims):")
    for name in report.get("strategies") or report["summaries"].keys():
        s = report["summaries"][name]
        print(f"  {name:<12} {_fmt_share(s.get('position_share') or {})}")
        early = {}
        for rnd in ("1", "2", "3"):
            early[rnd] = (s.get("by_round_share") or {}).get(rnd) or {}
        if any(early.values()):
            bits = []
            for rnd, sh in early.items():
                if sh:
                    bits.append(f"R{rnd}: {_fmt_share(sh)}")
            if bits:
                print(f"             early -> {' | '.join(bits)}")


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
            f"{key}: mean d={cmp_['mean_delta']:+.1f} median d={cmp_['median_delta']:+.1f} "
            f"win={cmp_['win_rate']:.1%} ties={cmp_['tie_rate']:.1%}"
        )
    _print_position_mix(report)


def _print_matrix(matrix: dict) -> None:
    strats = matrix["strategies"]
    print(
        f"Matrix n={matrix['n']} teams={matrix['n_teams']} preset={matrix['preset']} "
        f"seed={matrix['seed']} slots={matrix['slots']}"
    )
    header = f"{'slot':>4}"
    for name in strats:
        header += f" {name:>12}"
    if "marginal_vor" in strats and "adp" in strats:
        header += f" {'vor-adp':>8} {'v>adp':>7}"
    if "marginal_vor" in strats and "marginal" in strats:
        header += f" {'vor-raw':>8} {'v>raw':>7}"
    elif "marginal" in strats and "adp" in strats:
        header += f" {'m-adp':>8} {'win%':>7}"
    if "marginal" in strats and "greedy" in strats:
        header += f" {'m-greed':>8} {'win%':>7}"
    if "marginal_v2" in strats and "marginal" in strats:
        header += f" {'v2-raw':>8} {'v2>raw':>7}"
    if "marginal_v2" in strats and "marginal_vor" in strats:
        header += f" {'v2-vor':>8} {'v2>vor':>7}"
    print(header)
    for report in matrix["rows"]:
        line = f"{report['slot']:4d}"
        for name in strats:
            line += f" {report['summaries'][name]['mean_starter_pts']:12.1f}"
        comps = report.get("comparisons") or {}
        if "marginal_vor_vs_adp" in comps:
            c = comps["marginal_vor_vs_adp"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        if "marginal_vor_vs_marginal" in comps:
            c = comps["marginal_vor_vs_marginal"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        elif "marginal_vs_adp" in comps and "marginal_vor" not in strats:
            c = comps["marginal_vs_adp"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        if "marginal_vs_greedy" in comps:
            c = comps["marginal_vs_greedy"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        if "marginal_v2_vs_marginal" in comps:
            c = comps["marginal_v2_vs_marginal"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        if "marginal_v2_vs_marginal_vor" in comps:
            c = comps["marginal_v2_vs_marginal_vor"]
            line += f" {c['mean_delta']:+8.1f} {c['win_rate']:7.1%}"
        print(line)
    print("\nNote: win% = paired starter-points win rate (not wide-receiver rate).")
    focus = "marginal_vor" if "marginal_vor" in strats else "marginal"
    if matrix["rows"] and focus in strats:
        print(f"\nAggregate position mix across slots ({focus}):")
        totals: Counter[str] = Counter()
        for report in matrix["rows"]:
            s = report["summaries"].get(focus) or {}
            totals.update(s.get("position_counts") or {})
        t = sum(totals.values()) or 1
        share = {pos: totals[pos] / t for pos in totals}
        print(f"  {_fmt_share(share)}")


def matrix_to_markdown(matrix: dict, *, title: str, notes: list[str] | None = None) -> str:
    lines = [f"# {title}", ""]
    lines.append("## Setup")
    lines.append("")
    lines.append(f"- n_sims per slot: **{matrix['n']}**")
    lines.append(f"- teams: **{matrix['n_teams']}**")
    lines.append(f"- preset: `{matrix['preset']}`")
    lines.append(f"- seed: `{matrix['seed']}`")
    lines.append(f"- slots: `{matrix['slots']}`")
    lines.append(f"- strategies: `{', '.join(matrix['strategies'])}`")
    lines.append("- pairing: shared sim seed + CPU RNG keyed by overall pick #")
    lines.append("- scoring: ESPN season projections only (starter EV)")
    lines.append("- CPU: noisy ADP (not human ESPN managers)")
    lines.append("")
    if notes:
        lines.append("## Notes")
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## Slot matrix")
    lines.append("")
    strats = matrix["strategies"]
    header = ["slot", *strats]
    if "marginal_vor" in strats and "adp" in strats:
        header += ["vor−adp", "vor>adp"]
    if "marginal_vor" in strats and "marginal" in strats:
        header += ["vor−raw", "vor>raw"]
    elif "marginal" in strats and "adp" in strats:
        header += ["marginal−adp", "win_rate"]
    if "marginal" in strats and "greedy" in strats:
        header += ["marginal−greedy", "win_vs_greedy"]
    if "marginal_v2" in strats and "marginal" in strats:
        header += ["v2−raw", "v2>raw"]
    if "marginal_v2" in strats and "marginal_vor" in strats:
        header += ["v2−vor", "v2>vor"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for report in matrix["rows"]:
        cells = [str(report["slot"])]
        for name in strats:
            cells.append(f"{report['summaries'][name]['mean_starter_pts']:.1f}")
        comps = report.get("comparisons") or {}
        if "marginal_vor_vs_adp" in comps:
            c = comps["marginal_vor_vs_adp"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        if "marginal_vor_vs_marginal" in comps:
            c = comps["marginal_vor_vs_marginal"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        elif "marginal_vs_adp" in comps and "marginal_vor" not in strats:
            c = comps["marginal_vs_adp"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        if "marginal_vs_greedy" in comps:
            c = comps["marginal_vs_greedy"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        if "marginal_v2_vs_marginal" in comps:
            c = comps["marginal_v2_vs_marginal"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        if "marginal_v2_vs_marginal_vor" in comps:
            c = comps["marginal_v2_vs_marginal_vor"]
            cells.append(f"{c['mean_delta']:+.1f}")
            cells.append(f"{c['win_rate']:.1%}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        "`win%` / `vor>adp` / `vor>raw` / `v2>raw` / `v2>vor` = paired "
        "starter-points win rate (not wide-receiver share)."
    )
    lines.append("")
    lines.append("## Starter-EV dispersion (population stdev)")
    lines.append("")
    lines.append("| slot | " + " | ".join(f"{s} std" for s in strats) + " |")
    lines.append("| --- | " + " | ".join(["---:"] * len(strats)) + " |")
    for report in matrix["rows"]:
        cells = [str(report["slot"])]
        for name in strats:
            cells.append(f"{report['summaries'][name].get('std_starter_pts', 0.0):.1f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    if any(
        "marginal_v2_vs_marginal" in (r.get("comparisons") or {})
        or "marginal_v2_vs_adp" in (r.get("comparisons") or {})
        for r in matrix["rows"]
    ):
        lines.append("### Paired Δ dispersion (V2)")
        lines.append("")
        lines.append("| slot | v2−raw mean | v2−raw std | v2−vor mean | v2−vor std | v2−adp mean | v2−adp std |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for report in matrix["rows"]:
            comps = report.get("comparisons") or {}
            cr = comps.get("marginal_v2_vs_marginal") or {}
            cv = comps.get("marginal_v2_vs_marginal_vor") or {}
            ca = comps.get("marginal_v2_vs_adp") or {}

            def _m(c, k, fmt="{:+.1f}"):
                return fmt.format(c[k]) if k in c and c.get(k) is not None else "—"

            lines.append(
                f"| {report['slot']} | {_m(cr, 'mean_delta')} | {_m(cr, 'std_delta', '{:.1f}')} | "
                f"{_m(cv, 'mean_delta')} | {_m(cv, 'std_delta', '{:.1f}')} | "
                f"{_m(ca, 'mean_delta')} | {_m(ca, 'std_delta', '{:.1f}')} |"
            )
        lines.append("")
    lines.append("## Position mix (user picks)")
    lines.append("")
    for report in matrix["rows"]:
        lines.append(f"### Slot {report['slot']}")
        lines.append("")
        lines.append("| strategy | position share | early rounds (1–3) |")
        lines.append("| --- | --- | --- |")
        for name in strats:
            s = report["summaries"][name]
            early_bits = []
            for rnd in ("1", "2", "3"):
                sh = (s.get("by_round_share") or {}).get(rnd) or {}
                if sh:
                    early_bits.append(f"R{rnd}: {_fmt_share(sh)}")
            lines.append(
                f"| {name} | {_fmt_share(s.get('position_share') or {})} | "
                f"{' · '.join(early_bits) if early_bits else '—'} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def write_results(matrix: dict, path: Path, *, title: str, notes: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(matrix_to_markdown(matrix, title=title, notes=notes), encoding="utf-8")
    json_path = path.with_suffix(".json")
    json_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")


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
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Write markdown+json results to this path (updated after each slot in matrix mode)",
    )
    parser.add_argument("--title", type=str, default="Ablation backtest results")
    args = parser.parse_args()
    strategies = tuple(s.strip() for s in args.strategies.split(",") if s.strip())
    out_path = Path(args.out) if args.out else None
    notes = [
        "Scored on ESPN preseason projections (not actual season outcomes).",
        "Opponents use noisy-ADP CPU policy — not human ESPN managers.",
    ]

    if args.slots is not None:
        slot_list = parse_slots(args.slots)

        def _persist(report, rows):
            if out_path is None:
                return
            partial = {
                "n": args.n,
                "slots": [r["slot"] for r in rows],
                "preset": args.preset,
                "seed": args.seed,
                "n_teams": args.teams,
                "strategies": list(strategies),
                "paired": True,
                "rows": rows,
            }
            write_results(partial, out_path, title=args.title, notes=notes)
            print(f"    wrote {out_path}", flush=True)

        matrix = run_matrix(
            n=args.n,
            slots=slot_list,
            preset=args.preset,
            seed=args.seed,
            n_teams=args.teams,
            strategies=strategies,
            on_slot=_persist if out_path else None,
        )
        _print_matrix(matrix)
        for report in matrix["rows"]:
            print(f"\n--- slot {report['slot']} detail ---")
            _print_position_mix(report)
        if out_path is not None:
            write_results(matrix, out_path, title=args.title, notes=notes)
            print(f"Wrote {out_path} and {out_path.with_suffix('.json')}")
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
    if out_path is not None:
        matrix = {
            "n": report["n"],
            "slots": [report["slot"]],
            "preset": report["preset"],
            "seed": report["seed"],
            "n_teams": report["n_teams"],
            "strategies": report["strategies"],
            "paired": True,
            "rows": [report],
        }
        write_results(matrix, out_path, title=args.title, notes=notes)
        print(f"Wrote {out_path} and {out_path.with_suffix('.json')}")
    _print_report(report)

if __name__ == "__main__":
    main()
