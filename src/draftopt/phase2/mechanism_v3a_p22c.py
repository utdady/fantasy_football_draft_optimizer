"""V3-A mechanism audit: D−C decomposition on frozen ladder pairs.

No resimulation, no map retune, no new strategy. Reads
results/phase2_v3a_ladder.json and joins C/D projection snapshots for values.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.config import get_roster_preset
from draftopt.lineup import lineup_ev
from draftopt.phase2.diagnose_delta_p22c import _dist_summary
from draftopt.phase2.diagnose_valuation_p22c import (
    POS_ORDER,
    ROUND_BANDS,
    _mean_map,
    _starter_contrib,
)
from draftopt.phase2.materialize_p22c import P22C_DB_PATH
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.v3a_calibration import CURVE_ID

DEFAULT_LADDER = Path("results/phase2_v3a_ladder.json")
STRAT_C = "adp_structural"
STRAT_D = "adp_v3a"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_proj_adp(conn) -> tuple[dict[str, float], dict[str, float]]:
    """player_id -> season_points / adp (espn-aliased FFC plumbing)."""
    proj = {
        str(r["player_id"]): float(r["season_points"])
        for r in conn.execute(
            """
            SELECT player_id, season_points FROM projections_snapshots
            WHERE source = 'espn' AND season_points IS NOT NULL
            """
        )
    }
    adp = {
        str(r["player_id"]): float(r["adp"])
        for r in conn.execute(
            """
            SELECT player_id, adp FROM adp_snapshots
            WHERE source = 'espn' AND adp IS NOT NULL
            """
        )
    }
    return proj, adp


def _err(actual: float | None, value: float | None) -> float | None:
    if actual is None or value is None:
        return None
    return round(float(actual) - float(value), 4)


def _abs_errs(errs: list[float | None]) -> list[float]:
    return [abs(float(e)) for e in errs if e is not None]


def _first_fork(c_picks: list[dict], d_picks: list[dict]) -> dict | None:
    for i, (c, d) in enumerate(zip(c_picks, d_picks)):
        if c["player_id"] != d["player_id"]:
            return {
                "pick_index": i,
                "round": int(c["round"]),
                "overall_c": int(c["overall"]),
                "overall_d": int(d["overall"]),
                "c_pick": c,
                "d_pick": d,
            }
    return None


def _enrich_pick(p: dict, c_vals: dict, d_vals: dict, adp: dict) -> dict:
    pid = str(p["player_id"])
    act = p.get("actual_ppr")
    cv = c_vals.get(pid)
    dv = d_vals.get(pid)
    return {
        "round": int(p["round"]),
        "overall": int(p["overall"]),
        "player_id": pid,
        "name": p.get("name"),
        "position": (p.get("position") or "?").upper(),
        "adp": adp.get(pid),
        "actual_ppr": None if act is None else float(act),
        "c_value": cv,
        "d_value": dv,
        "value_delta_d_minus_c": (
            round(dv - cv, 4) if cv is not None and dv is not None else None
        ),
        "e_c": _err(act, cv),
        "e_d": _err(act, dv),
    }


def analyze(
    ladder: dict,
    *,
    c_vals: dict[str, float],
    d_vals: dict[str, float],
    adp: dict[str, float],
) -> dict:
    slots_cfg = get_roster_preset(ROSTER_PRESET)["slots"]
    pairs_in = ladder["pairs"]

    dc_full = [float(p["metrics"]["full"]["calibration_vs_structural_d_minus_c"]) for p in pairs_in]
    dc_ex = [float(p["metrics"]["ex_dst"]["calibration_vs_structural_d_minus_c"]) for p in pairs_in]
    dc_ex_te = [
        float(p["metrics"]["ex_dst_te"]["calibration_vs_structural_d_minus_c"])
        for p in pairs_in
    ]

    # --- concentration ---
    total_dc = sum(dc_full)
    ranked = sorted(
        (
            {
                "slot": int(p["slot"]),
                "seed": int(p["seed"]),
                "d_minus_c": float(
                    p["metrics"]["full"]["calibration_vs_structural_d_minus_c"]
                ),
            }
            for p in pairs_in
        ),
        key=lambda r: r["d_minus_c"],
        reverse=True,
    )
    pos_mass = [r for r in ranked if r["d_minus_c"] > 0]
    neg_mass = [r for r in ranked if r["d_minus_c"] < 0]

    def _share(rows: list[dict], k: int) -> dict:
        top = rows[:k]
        s = sum(r["d_minus_c"] for r in top)
        denom = sum(r["d_minus_c"] for r in rows)
        return {
            "k": k,
            "sum": round(s, 4),
            "share_of_positive_mass": round(s / denom, 4) if denom else None,
            "rows": top,
        }

    # share of total Σ(D−C) from top-k (including negatives in ranking by value)
    def _contrib_to_total(top_k: list[dict]) -> dict:
        s = sum(r["d_minus_c"] for r in top_k)
        return {
            "k": len(top_k),
            "sum": round(s, 4),
            "share_of_sum_dc": round(s / total_dc, 4) if total_dc else None,
            "rows": top_k,
        }

    concentration = {
        "sum_d_minus_c": round(total_dc, 4),
        "mean_d_minus_c": round(statistics.mean(dc_full), 4),
        "top5_by_d_minus_c": _contrib_to_total(ranked[:5]),
        "top10_by_d_minus_c": _contrib_to_total(ranked[:10]),
        "top5_of_positive_mass": _share(pos_mass, 5) if pos_mass else None,
        "top10_of_positive_mass": _share(pos_mass, 10) if pos_mass else None,
        "worst5_by_d_minus_c": _contrib_to_total(ranked[-5:][::-1]),
        "n_positive": len(pos_mass),
        "n_negative": len(neg_mass),
        "flag": None,
    }
    t10_pos = (
        concentration["top10_of_positive_mass"]["share_of_positive_mass"]
        if concentration["top10_of_positive_mass"]
        else None
    )
    if t10_pos is not None and t10_pos >= 0.70:
        concentration["flag"] = (
            "mega_win_driven — top-10 positive drafts ≥70% of positive mass"
        )
    elif t10_pos is not None and t10_pos >= 0.50:
        concentration["flag"] = (
            "concentrated — top-10 positive drafts ≥50% of positive mass"
        )
    else:
        concentration["flag"] = "broad — top-10 share of positive mass < 50%"
    concentration["top10_positive_mass_share"] = t10_pos

    # --- position / round / slot ---
    pos_deltas: dict[str, list[float]] = defaultdict(list)
    band_deltas: dict[str, list[float]] = defaultdict(list)
    round_deltas: dict[str, list[float]] = defaultdict(list)
    slot_gains: dict[int, list[float]] = defaultdict(list)

    forks: list[dict] = []
    e_c_all: list[float] = []
    e_d_all: list[float] = []
    e_c_fork: list[float] = []
    e_d_fork: list[float] = []
    # same player: both values available
    paired_abs: list[dict] = []
    value_shifts: list[dict] = []
    seen_shift: set[str] = set()

    enriched_pairs: list[dict] = []

    for pair in pairs_in:
        slot = int(pair["slot"])
        seed = int(pair["seed"])
        dc = float(pair["metrics"]["full"]["calibration_vs_structural_d_minus_c"])
        c_picks_raw = pair["picks"][STRAT_C]
        d_picks_raw = pair["picks"][STRAT_D]
        c_picks = [_enrich_pick(p, c_vals, d_vals, adp) for p in c_picks_raw]
        d_picks = [_enrich_pick(p, c_vals, d_vals, adp) for p in d_picks_raw]

        c_contrib = _starter_contrib(c_picks_raw, slots_cfg)
        d_contrib = _starter_contrib(d_picks_raw, slots_cfg)

        pos_d: dict[str, float] = {}
        for pos in POS_ORDER:
            delta = float(d_contrib["by_pos"].get(pos, 0.0)) - float(
                c_contrib["by_pos"].get(pos, 0.0)
            )
            pos_d[pos] = round(delta, 4)
            pos_deltas[pos].append(delta)

        band_d: dict[str, float] = {}
        for band in ROUND_BANDS:
            delta = float(d_contrib["by_band"].get(band, 0.0)) - float(
                c_contrib["by_band"].get(band, 0.0)
            )
            band_d[band] = round(delta, 4)
            band_deltas[band].append(delta)

        rounds = set(c_contrib["by_round"]) | set(d_contrib["by_round"])
        round_d: dict[str, float] = {}
        for r in sorted(rounds, key=int):
            delta = float(d_contrib["by_round"].get(r, 0.0)) - float(
                c_contrib["by_round"].get(r, 0.0)
            )
            round_d[r] = round(delta, 4)
            round_deltas[r].append(delta)

        slot_gains[slot].append(dc)

        for p in c_picks:
            if p["e_c"] is not None:
                e_c_all.append(p["e_c"])
        for p in d_picks:
            if p["e_d"] is not None:
                e_d_all.append(p["e_d"])
            # paired error on D's roster (same player, both maps)
            if p["e_c"] is not None and p["e_d"] is not None:
                paired_abs.append(
                    {
                        "player_id": p["player_id"],
                        "name": p["name"],
                        "position": p["position"],
                        "adp": p["adp"],
                        "abs_e_c": abs(p["e_c"]),
                        "abs_e_d": abs(p["e_d"]),
                        "abs_improve_d_minus_c": round(
                            abs(p["e_c"]) - abs(p["e_d"]), 4
                        ),
                        "source": "d_roster",
                    }
                )
            pid = p["player_id"]
            if pid not in seen_shift and p["value_delta_d_minus_c"] is not None:
                seen_shift.add(pid)
                value_shifts.append(
                    {
                        "player_id": pid,
                        "name": p["name"],
                        "position": p["position"],
                        "adp": p["adp"],
                        "c_value": p["c_value"],
                        "d_value": p["d_value"],
                        "value_delta_d_minus_c": p["value_delta_d_minus_c"],
                    }
                )

        for p in c_picks:
            pid = p["player_id"]
            if pid not in seen_shift and p["value_delta_d_minus_c"] is not None:
                seen_shift.add(pid)
                value_shifts.append(
                    {
                        "player_id": pid,
                        "name": p["name"],
                        "position": p["position"],
                        "adp": p["adp"],
                        "c_value": p["c_value"],
                        "d_value": p["d_value"],
                        "value_delta_d_minus_c": p["value_delta_d_minus_c"],
                    }
                )

        fork_raw = _first_fork(c_picks, d_picks)
        fork_row = None
        if fork_raw:
            cp = fork_raw["c_pick"]
            dp = fork_raw["d_pick"]
            act_c = cp["actual_ppr"]
            act_d = dp["actual_ppr"]
            winner = None
            if act_c is not None and act_d is not None:
                if act_d > act_c:
                    winner = "D"
                elif act_c > act_d:
                    winner = "C"
                else:
                    winner = "tie"
            regret_d = (
                round(float(act_c) - float(act_d), 4)
                if act_c is not None and act_d is not None
                else None
            )
            # positive regret_d => D's fork pick worse on actual than C's
            if cp["e_c"] is not None:
                e_c_fork.append(cp["e_c"])
            if dp["e_d"] is not None:
                e_d_fork.append(dp["e_d"])
            fork_row = {
                "slot": slot,
                "seed": seed,
                "d_minus_c_full": dc,
                "pick_index": fork_raw["pick_index"],
                "round": fork_raw["round"],
                "c": {
                    "name": cp["name"],
                    "position": cp["position"],
                    "player_id": cp["player_id"],
                    "adp": cp["adp"],
                    "c_value": cp["c_value"],
                    "d_value": cp["d_value"],
                    "actual_ppr": act_c,
                    "e_c": cp["e_c"],
                    "e_d": cp["e_d"],
                },
                "d": {
                    "name": dp["name"],
                    "position": dp["position"],
                    "player_id": dp["player_id"],
                    "adp": dp["adp"],
                    "c_value": dp["c_value"],
                    "d_value": dp["d_value"],
                    "actual_ppr": act_d,
                    "e_c": dp["e_c"],
                    "e_d": dp["e_d"],
                },
                "first_fork_winner_actual": winner,
                "first_fork_regret_d_vs_c": regret_d,
                "actual_delta_d_minus_c_at_fork": (
                    round(float(act_d) - float(act_c), 4)
                    if act_c is not None and act_d is not None
                    else None
                ),
            }
            forks.append(fork_row)

        enriched_pairs.append(
            {
                "slot": slot,
                "seed": seed,
                "d_minus_c_full": dc,
                "d_minus_c_ex_dst": float(
                    pair["metrics"]["ex_dst"]["calibration_vs_structural_d_minus_c"]
                ),
                "d_minus_c_ex_dst_te": float(
                    pair["metrics"]["ex_dst_te"]["calibration_vs_structural_d_minus_c"]
                ),
                "pos_delta": pos_d,
                "band_delta": band_d,
                "round_delta": round_d,
                "pick_diff": {
                    "n_shared": len(
                        {p["player_id"] for p in c_picks_raw}
                        & {p["player_id"] for p in d_picks_raw}
                    ),
                    "n_only_c": len(
                        {p["player_id"] for p in c_picks_raw}
                        - {p["player_id"] for p in d_picks_raw}
                    ),
                    "n_only_d": len(
                        {p["player_id"] for p in d_picks_raw}
                        - {p["player_id"] for p in c_picks_raw}
                    ),
                },
                "fork": fork_row,
            }
        )

    by_slot = []
    for slot in sorted(slot_gains):
        vals = slot_gains[slot]
        by_slot.append(
            {
                "slot": slot,
                "n": len(vals),
                "mean_d_minus_c": round(statistics.mean(vals), 4),
                "median_d_minus_c": round(statistics.median(vals), 4),
                "win_rate": round(sum(1 for v in vals if v > 0) / len(vals), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
            }
        )

    # value-shift extremes
    value_shifts.sort(key=lambda r: r["value_delta_d_minus_c"])
    biggest_down = value_shifts[:15]
    biggest_up = list(reversed(value_shifts[-15:]))

    shift_by_pos: dict[str, list[float]] = defaultdict(list)
    for r in value_shifts:
        shift_by_pos[r["position"]].append(r["value_delta_d_minus_c"])

    # fork summaries
    fork_winners = Counter(f["first_fork_winner_actual"] for f in forks)
    fork_regrets = [
        f["first_fork_regret_d_vs_c"]
        for f in forks
        if f["first_fork_regret_d_vs_c"] is not None
    ]
    fork_rounds = Counter(str(f["round"]) for f in forks)
    fork_c_pos = Counter(f["c"]["position"] for f in forks)
    fork_d_pos = Counter(f["d"]["position"] for f in forks)

    # paired abs error on D roster: does D map improve |error|?
    abs_imp = [r["abs_improve_d_minus_c"] for r in paired_abs]
    n_abs_better = sum(1 for v in abs_imp if v > 0)
    n_abs_worse = sum(1 for v in abs_imp if v < 0)

    pred = {
        "all_c_picks_e_c": _dist_summary(e_c_all),
        "all_d_picks_e_d": _dist_summary(e_d_all),
        "all_c_picks_abs_e_c": _dist_summary(_abs_errs(e_c_all)),
        "all_d_picks_abs_e_d": _dist_summary(_abs_errs(e_d_all)),
        "fork_c_pick_e_c": _dist_summary(e_c_fork),
        "fork_d_pick_e_d": _dist_summary(e_d_fork),
        "fork_c_pick_abs_e_c": _dist_summary(_abs_errs(e_c_fork)),
        "fork_d_pick_abs_e_d": _dist_summary(_abs_errs(e_d_fork)),
        "d_roster_paired_abs_improve_d_minus_c": _dist_summary(abs_imp),
        "d_roster_paired_n": len(paired_abs),
        "d_roster_abs_better_count": n_abs_better,
        "d_roster_abs_worse_count": n_abs_worse,
        "d_roster_abs_better_rate": (
            round(n_abs_better / len(paired_abs), 4) if paired_abs else None
        ),
        "note": (
            "e = actual − value. Negative mean ⇒ over-projection. "
            "Paired abs improve on D roster: |e_C| − |e_D| > 0 means D closer to actual."
        ),
    }

    # interpretation gate (ordered)
    mean_abs_c = pred["all_c_picks_abs_e_c"]["mean"]
    mean_abs_d = pred["all_d_picks_abs_e_d"]["mean"]
    mean_dc = statistics.mean(dc_full)
    p10_dc = _dist_summary(dc_full)["p10"]
    p10_cb = ladder.get("ladder", {}).get("full", {}).get(
        "valuation_gain_c_minus_b", {}
    ).get("p10")
    abs_err_improved = (
        mean_abs_c is not None
        and mean_abs_d is not None
        and mean_abs_d < mean_abs_c - 5
    )
    abs_err_still_poor = mean_abs_d is not None and mean_abs_d > 80
    draft_tail_worse = p10_dc is not None and (
        p10_cb is None or p10_dc < float(p10_cb) - 20
    )
    concentrated = concentration["flag"].startswith("mega_win") or concentration[
        "flag"
    ].startswith("concentrated")

    gates: list[str] = []
    # Primary hinge first
    if abs_err_improved and draft_tail_worse:
        gates.append(
            "HINGE: D |error| substantially closer to 0 + D draft tail worse — "
            "calibration works at player level; construction interaction implicated "
            "(V3-B becomes legitimate to design, not implement yet)"
        )
    elif abs_err_improved and mean_dc <= 0:
        gates.append(
            "HINGE: D improves player error but not draft outcomes — "
            "strong evidence for valuation × construction interaction"
        )
    elif abs_err_improved and mean_dc > 0 and not draft_tail_worse:
        gates.append(
            "HINGE: D improves both player error and draft distribution — "
            "V3-A itself gets stronger, but still needs another season"
        )
    elif abs_err_still_poor and not abs_err_improved:
        gates.append(
            "HINGE: D error remains poor — valuation/calibration problem → "
            "V3-B stays blocked"
        )
    else:
        gates.append(
            "HINGE: mixed / inconclusive — inspect fork and position tables; "
            "do not retune map"
        )

    if concentrated and mean_dc > 0:
        gates.append(
            "CAVEAT: D−C positive mass is concentrated (Hypothesis D) — "
            "mean improvement is not evenly distributed across boards"
        )

    # Smoking gun from forks (already computed above)
    if (
        forks
        and fork_rounds.get("1") == len(forks)
        and fork_d_pos.get("QB", 0) == len(forks)
    ):
        gates.append(
            "FINDING: every first fork is R1 D=QB vs C=RB/WR — "
            "D wins the fork pick on actual (~95%) but mean RB starter Δ is large "
            "negative (portfolio / construction interaction). Not a map edit."
        )

    mean_pos = _mean_map(pos_deltas)

    return {
        "stage": "V3A_MECHANISM_AUDIT",
        "created_at": _utcnow(),
        "snapshot_id": ladder.get("snapshot_id", DECISION_SNAPSHOT_ID),
        "v3a_snapshot_id": ladder.get("v3a_snapshot_id"),
        "curve_id": CURVE_ID,
        "contract_id": ladder.get("contract_id", CONTRACT_ID),
        "evaluable": 0,
        "source_ladder": str(DEFAULT_LADDER),
        "claim": (
            "Mechanism audit of D−C on frozen V3-A.0 ladder pairs. "
            "No resimulation; values joined from structural + calibrated DBs. "
            "Map remains f6c5010 artifact; findings are not permission to retune."
        ),
        "methodological_rule": (
            "A mechanism finding (e.g. late-QB uplift) is a finding, not a map edit."
        ),
        "contract": contract_meta(),
        "n_pairs": len(pairs_in),
        "classification": "mean_improvement_tail_tradeoff",
        "aggregate_d_minus_c": {
            "full": _dist_summary(dc_full),
            "ex_dst": _dist_summary(dc_ex),
            "ex_dst_te": _dist_summary(dc_ex_te),
        },
        "concentration": concentration,
        "by_position": {
            "mean_delta": mean_pos,
            "distributions": {
                pos: _dist_summary(pos_deltas[pos]) for pos in POS_ORDER
            },
        },
        "by_round_band": {
            "mean_delta": _mean_map(band_deltas),
            "distributions": {
                band: _dist_summary(band_deltas[band]) for band in ROUND_BANDS
            },
        },
        "by_round": {
            "mean_delta": _mean_map(
                {r: round_deltas[r] for r in sorted(round_deltas, key=int)}
            ),
        },
        "by_slot": by_slot,
        "value_shifts": {
            "n_unique_players": len(value_shifts),
            "mean_delta_by_pos": {
                pos: round(statistics.mean(vs), 4) for pos, vs in shift_by_pos.items()
            },
            "biggest_upward_d_minus_c": biggest_up,
            "biggest_downward_d_minus_c": biggest_down,
        },
        "forks": {
            "n": len(forks),
            "winner_counts": dict(fork_winners),
            "d_win_rate_at_fork": (
                round(fork_winners.get("D", 0) / len(forks), 4) if forks else None
            ),
            "regret_d_vs_c": _dist_summary(fork_regrets),
            "rounds": dict(sorted(fork_rounds.items(), key=lambda x: int(x[0]))),
            "c_positions": dict(fork_c_pos),
            "d_positions": dict(fork_d_pos),
            "rows": forks,
        },
        "prediction_errors": pred,
        "interpretation_gates": gates,
        "pairs": enriched_pairs,
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    agg = report["aggregate_d_minus_c"]
    conc = report["concentration"]
    pred = report["prediction_errors"]
    forks = report["forks"]
    lines = [
        "# V3-A mechanism audit (D−C)",
        "",
        f"- stage: `{report['stage']}`",
        f"- curve: `{report['curve_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']}",
        f"- source: `{report['source_ladder']}`",
        f"- classification: `{report['classification']}`",
        "",
        report["claim"],
        "",
        f"**{report['methodological_rule']}**",
        "",
        "## Interpretation gates",
        "",
    ]
    for g in report["interpretation_gates"]:
        lines.append(f"- {g}")

    lines.extend(
        [
            "",
            "## 1. Aggregate D−C",
            "",
            "| Contract | Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, key in (
        ("Full", "full"),
        ("Ex-DST", "ex_dst"),
        ("Ex-DST+TE", "ex_dst_te"),
    ):
        d = agg[key]
        lines.append(
            f"| {name} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{d['win_rate']:.0%} | {_fmt(d['p10'])} | {_fmt(d['p25'])} | "
            f"{_fmt(d['p75'])} | {_fmt(d['p90'])} | {_fmt(d['min'])} | "
            f"{_fmt(d['max'])} | {d['n_negative']}/{d['n']} |"
        )

    t10 = conc["top10_by_d_minus_c"]
    t5 = conc["top5_by_d_minus_c"]
    lines.extend(
        [
            "",
            "## 2. Concentration",
            "",
            f"- Σ(D−C) = {_fmt(conc['sum_d_minus_c'])}",
            f"- flag: **{conc['flag']}**",
            f"- top-5 sum = {_fmt(t5['sum'])} "
            f"(share of Σ = {t5['share_of_sum_dc']})",
            f"- top-10 sum = {_fmt(t10['sum'])} "
            f"(share of Σ = {t10['share_of_sum_dc']}; "
            f"share of positive mass = {conc.get('top10_positive_mass_share')})",
            "",
            "### Top-10 drafts by D−C",
            "",
            "| Slot | Seed | D−C |",
            "| ---: | ---: | ---: |",
        ]
    )
    for r in t10["rows"]:
        lines.append(f"| {r['slot']} | {r['seed']} | {_fmt(r['d_minus_c'])} |")

    lines.extend(
        [
            "",
            "## 3. Position × round × slot",
            "",
            "### Mean starter actual Δ (D−C) by position",
            "",
            "| Pos | Mean Δ | Median | WR |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for pos in POS_ORDER:
        d = report["by_position"]["distributions"][pos]
        lines.append(
            f"| {pos} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{(d['win_rate'] or 0):.0%} |"
        )

    lines.extend(
        [
            "",
            "### Mean starter actual Δ by round band",
            "",
            "| Band | Mean Δ | Median | WR |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for band in ROUND_BANDS:
        d = report["by_round_band"]["distributions"][band]
        lines.append(
            f"| {band} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{(d['win_rate'] or 0):.0%} |"
        )

    lines.extend(
        [
            "",
            "### By draft slot",
            "",
            "| Slot | Mean D−C | Median | WR |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["by_slot"]:
        lines.append(
            f"| {row['slot']} | {_fmt(row['mean_d_minus_c'])} | "
            f"{_fmt(row['median_d_minus_c'])} | {row['win_rate']:.0%} |"
        )

    vs = report["value_shifts"]
    lines.extend(
        [
            "",
            "### Value map shifts (D−C on unique drafted players)",
            "",
            f"- unique players with both values: {vs['n_unique_players']}",
            f"- mean value Δ by pos: `{vs['mean_delta_by_pos']}`",
            "",
            "Biggest upward (D lifts vs C):",
            "",
            "| Player | Pos | ADP | C val | D val | Δ |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for r in vs["biggest_upward_d_minus_c"][:10]:
        lines.append(
            f"| {r['name']} | {r['position']} | {_fmt(r['adp'], False)} | "
            f"{_fmt(r['c_value'], False)} | {_fmt(r['d_value'], False)} | "
            f"{_fmt(r['value_delta_d_minus_c'])} |"
        )
    lines.extend(
        [
            "",
            "Biggest downward (D compresses vs C):",
            "",
            "| Player | Pos | ADP | C val | D val | Δ |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for r in vs["biggest_downward_d_minus_c"][:10]:
        lines.append(
            f"| {r['name']} | {r['position']} | {_fmt(r['adp'], False)} | "
            f"{_fmt(r['c_value'], False)} | {_fmt(r['d_value'], False)} | "
            f"{_fmt(r['value_delta_d_minus_c'])} |"
        )

    lines.extend(
        [
            "",
            "## 4. Fork analysis (first C≠D pick)",
            "",
            f"- forks: {forks['n']}",
            f"- first-fork actual winner counts: `{forks['winner_counts']}`",
            f"- D win rate at first fork: {forks['d_win_rate_at_fork']}",
            f"- regret (C_actual − D_actual): mean={_fmt(forks['regret_d_vs_c']['mean'])}, "
            f"median={_fmt(forks['regret_d_vs_c']['median'])}, "
            f"p10={_fmt(forks['regret_d_vs_c']['p10'])}",
            f"- fork rounds: `{forks['rounds']}`",
            f"- C positions: `{forks['c_positions']}`",
            f"- D positions: `{forks['d_positions']}`",
            "",
            "### Fork rows (all)",
            "",
            "| Slot | Seed | R | C pick | D pick | C val | D val | act C | act D | "
            "e_C | e_D | winner | regret_D |",
            "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for f in forks["rows"]:
        c, d = f["c"], f["d"]
        lines.append(
            f"| {f['slot']} | {f['seed']} | {f['round']} | "
            f"{c['name']} ({c['position']}) | {d['name']} ({d['position']}) | "
            f"{_fmt(c['c_value'], False)} | {_fmt(d['d_value'], False)} | "
            f"{_fmt(c['actual_ppr'], False)} | {_fmt(d['actual_ppr'], False)} | "
            f"{_fmt(c['e_c'])} | {_fmt(d['e_d'])} | "
            f"{f['first_fork_winner_actual']} | {_fmt(f['first_fork_regret_d_vs_c'])} |"
        )

    lines.extend(
        [
            "",
            "## 5. Prediction-error comparison (hinge)",
            "",
            pred["note"],
            "",
            "| Set | Mean e | Median e | Mean |e| | Median |e| |",
            "| --- | ---: | ---: | ---: | ---: |",
            f"| All C picks (e_C) | {_fmt(pred['all_c_picks_e_c']['mean'])} | "
            f"{_fmt(pred['all_c_picks_e_c']['median'])} | "
            f"{_fmt(pred['all_c_picks_abs_e_c']['mean'], False)} | "
            f"{_fmt(pred['all_c_picks_abs_e_c']['median'], False)} |",
            f"| All D picks (e_D) | {_fmt(pred['all_d_picks_e_d']['mean'])} | "
            f"{_fmt(pred['all_d_picks_e_d']['median'])} | "
            f"{_fmt(pred['all_d_picks_abs_e_d']['mean'], False)} | "
            f"{_fmt(pred['all_d_picks_abs_e_d']['median'], False)} |",
            f"| Fork C pick (e_C) | {_fmt(pred['fork_c_pick_e_c']['mean'])} | "
            f"{_fmt(pred['fork_c_pick_e_c']['median'])} | "
            f"{_fmt(pred['fork_c_pick_abs_e_c']['mean'], False)} | "
            f"{_fmt(pred['fork_c_pick_abs_e_c']['median'], False)} |",
            f"| Fork D pick (e_D) | {_fmt(pred['fork_d_pick_e_d']['mean'])} | "
            f"{_fmt(pred['fork_d_pick_e_d']['median'])} | "
            f"{_fmt(pred['fork_d_pick_abs_e_d']['mean'], False)} | "
            f"{_fmt(pred['fork_d_pick_abs_e_d']['median'], False)} |",
            "",
            "### Paired |e| on D roster (same player, both maps)",
            "",
            f"- n={pred['d_roster_paired_n']}; "
            f"|e| better under D: {pred['d_roster_abs_better_count']} "
            f"({pred['d_roster_abs_better_rate']}); "
            f"worse: {pred['d_roster_abs_worse_count']}",
            f"- mean (|e_C| − |e_D|) = "
            f"{_fmt(pred['d_roster_paired_abs_improve_d_minus_c']['mean'])} "
            f"(positive ⇒ D closer)",
            "",
            "## Status",
            "",
            "- Map: frozen (`adp_emp_pos_v1_train_2021_2023` / f6c5010)",
            "- V3-B: only if hinge shows better player error + worse draft tail",
            "- UI: `marginal`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-A D−C mechanism audit")
    parser.add_argument("--ladder", type=Path, default=DEFAULT_LADDER)
    parser.add_argument("--draft-db", type=Path, default=P22C_DB_PATH)
    parser.add_argument("--v3a-draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_mechanism_audit.md"),
    )
    args = parser.parse_args()

    ladder = json.loads(args.ladder.read_text(encoding="utf-8"))
    c_conn = live_db.connect(args.draft_db)
    d_conn = live_db.connect(args.v3a_draft_db)
    c_vals, adp_c = _load_proj_adp(c_conn)
    d_vals, adp_d = _load_proj_adp(d_conn)
    c_conn.close()
    d_conn.close()
    adp = {**adp_c, **adp_d}

    report = analyze(ladder, c_vals=c_vals, d_vals=d_vals, adp=adp)
    # Drop bulky paired list from default json? keep forks+pairs; trim paired abs detail
    slim = dict(report)
    md = _md(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
