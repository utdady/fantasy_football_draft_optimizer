"""V3-B.0 failure mechanism audit (descriptive only).

Frozen E/D ladder pairs + targeted replay to the first D≠E pick to join
decision-time M_D / r* / M_E. No new objective. No E.1. No map retune.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import pick_rng
from draftopt.config import get_roster_preset
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    is_user_turn,
    record_user_pick,
    round_for_pick,
    snapshot,
)
from draftopt.phase2.diagnose_delta_p22c import _dist_summary
from draftopt.phase2.diagnose_valuation_p22c import (
    POS_ORDER,
    ROUND_BANDS,
    _mean_map,
    _round_band,
    _starter_contrib,
)
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.replacement_nextbest import CONSTRUCTION_ID
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    N_ROUNDS,
    N_TEAMS,
    ROSTER_PRESET,
    contract_meta,
)
from draftopt.phase2.v3a_calibration import CURVE_ID
from draftopt.strategies import get_strategy

DEFAULT_LADDER = Path("results/phase2_v3b_ladder.json")
STRAT_D = "adp_v3a"
STRAT_E = "adp_v3b"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_divergence(d_picks: list[dict], e_picks: list[dict]) -> dict | None:
    for i, (d, e) in enumerate(zip(d_picks, e_picks)):
        if d["player_id"] != e["player_id"]:
            return {
                "pick_index": i,
                "round": int(d["round"]),
                "overall_d": int(d["overall"]),
                "overall_e": int(e["overall"]),
                "d_pick": d,
                "e_pick": e,
            }
    return None


def _find_in_recs(recs: list[dict], player_id: str) -> dict | None:
    for r in recs:
        if str(r.get("player_id")) == str(player_id):
            return r
    return None


def _replay_to_first_fork(
    conn,
    *,
    slot: int,
    seed: int,
    d_picks: list[dict],
    e_picks: list[dict],
) -> dict | None:
    """
    Follow frozen identical prefix picks until first D≠E; join decision-time scores.
    Board state is shared until divergence (same CPU + same prior user picks).
    """
    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="V3B0-fail-audit",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    pick_i = 0
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            return None
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            if pick_i >= len(d_picks) or pick_i >= len(e_picks):
                return None
            d_p = d_picks[pick_i]
            e_p = e_picks[pick_i]
            overall = int(draft_row["current_pick"])
            rnd = round_for_pick(overall, N_TEAMS)
            if str(d_p["player_id"]) != str(e_p["player_id"]):
                d_recs = get_strategy(STRAT_D).recommend(conn, draft_id, n=10_000)
                e_recs = get_strategy(STRAT_E).recommend(conn, draft_id, n=10_000)
                d_on_d = _find_in_recs(d_recs, d_p["player_id"])
                e_on_d = _find_in_recs(d_recs, e_p["player_id"])
                d_on_e = _find_in_recs(e_recs, d_p["player_id"])
                e_on_e = _find_in_recs(e_recs, e_p["player_id"])

                # Collapse stats on E's full decision pool
                collapse_rows = []
                near_zero_me = 0
                for item in e_recs:
                    v = item.get("season_points")
                    if v is None:
                        v = item.get("proj_espn")
                    md = item.get("marginal_d")
                    r = item.get("replacement")
                    me = item.get("marginal_e")
                    if v is None or float(v) <= 0:
                        continue
                    ratio = float(r or 0) / float(v) if float(v) else None
                    if me is not None and abs(float(me)) <= 1.0:
                        near_zero_me += 1
                    collapse_rows.append(
                        {
                            "player_id": str(item["player_id"]),
                            "name": item.get("name"),
                            "position": (item.get("position") or "").upper(),
                            "v": float(v),
                            "marginal_d": md,
                            "replacement": r,
                            "replacement_missing": item.get("replacement_missing"),
                            "marginal_e": me,
                            "r_over_v": round(ratio, 4) if ratio is not None else None,
                        }
                    )

                return {
                    "draft_id": draft_id,
                    "pick_index": pick_i,
                    "round": rnd,
                    "overall": overall,
                    "d_pick_ladder": d_p,
                    "e_pick_ladder": e_p,
                    "d_under_d": d_on_d,
                    "e_under_d": e_on_d,
                    "d_under_e": d_on_e,
                    "e_under_e": e_on_e,
                    "collapse_pool": collapse_rows,
                    "n_pool": len(collapse_rows),
                    "n_near_zero_me": near_zero_me,
                }
            # Shared prefix — take the frozen (identical) pick
            record_user_pick(conn, draft_id, d_p["player_id"], made_by="strategy")
            pick_i += 1
        else:
            overall = int(draft_row["current_pick"])
            cpu_pick(conn, draft_id, rng=pick_rng(seed, overall), policy="noisy_adp")


def _view_cand(rec: dict | None, actual: float | None) -> dict | None:
    if not rec:
        return None
    v = rec.get("season_points")
    if v is None:
        v = rec.get("proj_espn")
    return {
        "player_id": str(rec.get("player_id")),
        "name": rec.get("name"),
        "position": (rec.get("position") or "").upper(),
        "calibrated_value": None if v is None else float(v),
        "marginal_d": rec.get("marginal_d", rec.get("marginal")),
        "replacement": rec.get("replacement"),
        "replacement_missing": rec.get("replacement_missing"),
        "marginal_e": rec.get("marginal_e"),
        "actual_ppr": actual,
    }


def analyze(ladder: dict, *, draft_db: Path, join_decision_time: bool = True) -> dict:
    slots_cfg = get_roster_preset(ROSTER_PRESET)["slots"]
    pairs_in = ladder["pairs"]

    # --- §1 divergence aggregates ---
    fork_rounds: Counter[str] = Counter()
    fork_bands: Counter[str] = Counter()
    d_pos: Counter[str] = Counter()
    e_pos: Counter[str] = Counter()
    pos_transitions: Counter[str] = Counter()
    n_changed_picks_total = 0
    n_boards_diverge = 0

    # --- §2 attribution ---
    fork_actual_deltas: list[float] = []
    pos_deltas: dict[str, list[float]] = defaultdict(list)
    band_deltas: dict[str, list[float]] = defaultdict(list)

    # --- §4 holes ---
    pos_count_deltas: dict[str, list[float]] = defaultdict(list)

    enriched: list[dict] = []
    collapse_all_ratios: list[float] = []
    collapse_near_zero_fracs: list[float] = []
    sacrifice_rows: list[dict] = []

    conn = None
    if join_decision_time:
        conn = live_db.connect(draft_db)
        live_db.init(conn)

    for pair in pairs_in:
        slot = int(pair["slot"])
        seed = int(pair["seed"])
        ed = float(pair["metrics"]["full"]["construction_gain_e_minus_d"])
        d_picks = pair["picks"][STRAT_D]
        e_picks = pair["picks"][STRAT_E]

        fork = _first_divergence(d_picks, e_picks)
        n_changed = sum(
            1
            for a, b in zip(d_picks, e_picks)
            if a["player_id"] != b["player_id"]
        )
        n_changed_picks_total += n_changed

        d_contrib = _starter_contrib(d_picks, slots_cfg)
        e_contrib = _starter_contrib(e_picks, slots_cfg)

        pos_d = {}
        for pos in POS_ORDER:
            delta = float(e_contrib["by_pos"].get(pos, 0.0)) - float(
                d_contrib["by_pos"].get(pos, 0.0)
            )
            pos_d[pos] = round(delta, 4)
            pos_deltas[pos].append(delta)

        band_d = {}
        for band in ROUND_BANDS:
            delta = float(e_contrib["by_band"].get(band, 0.0)) - float(
                d_contrib["by_band"].get(band, 0.0)
            )
            band_d[band] = round(delta, 4)
            band_deltas[band].append(delta)

        # Position draft counts (full roster, not just starters)
        d_counts = Counter((p.get("position") or "?").upper() for p in d_picks)
        e_counts = Counter((p.get("position") or "?").upper() for p in e_picks)
        count_delta = {}
        for pos in POS_ORDER:
            delta = float(e_counts.get(pos, 0) - d_counts.get(pos, 0))
            count_delta[pos] = delta
            pos_count_deltas[pos].append(delta)

        fork_row = None
        decision_join = None
        if fork:
            n_boards_diverge += 1
            rnd = int(fork["round"])
            fork_rounds[str(rnd)] += 1
            fork_bands[_round_band(rnd)] += 1
            dp = (fork["d_pick"].get("position") or "?").upper()
            ep = (fork["e_pick"].get("position") or "?").upper()
            d_pos[dp] += 1
            e_pos[ep] += 1
            pos_transitions[f"{dp}->{ep}"] += 1
            act_d = fork["d_pick"].get("actual_ppr")
            act_e = fork["e_pick"].get("actual_ppr")
            fork_act = None
            if act_d is not None and act_e is not None:
                fork_act = round(float(act_e) - float(act_d), 4)
                fork_actual_deltas.append(fork_act)

            if join_decision_time and conn is not None:
                decision_join = _replay_to_first_fork(
                    conn,
                    slot=slot,
                    seed=seed,
                    d_picks=d_picks,
                    e_picks=e_picks,
                )
                if decision_join:
                    # D/E candidates under both rankings
                    dd = decision_join.get("d_under_d")
                    edd = decision_join.get("e_under_d")
                    de = decision_join.get("d_under_e")
                    ee = decision_join.get("e_under_e")

                    d_view = _view_cand(
                        de or dd,
                        float(act_d) if act_d is not None else None,
                    )
                    e_view = _view_cand(
                        ee or edd,
                        float(act_e) if act_e is not None else None,
                    )
                    if d_view and dd is not None:
                        d_view["marginal_d"] = float(dd.get("marginal"))
                        if d_view.get("calibrated_value") is None:
                            v = dd.get("season_points") or dd.get("proj_espn")
                            if v is not None:
                                d_view["calibrated_value"] = float(v)
                    if e_view and edd is not None:
                        e_view["marginal_d"] = float(edd.get("marginal"))
                        if e_view.get("calibrated_value") is None:
                            v = edd.get("season_points") or edd.get("proj_espn")
                            if v is not None:
                                e_view["calibrated_value"] = float(v)
                    # E-ranking fields for both (r*, M_E)
                    if d_view and de is not None:
                        d_view["replacement"] = de.get("replacement")
                        d_view["replacement_missing"] = de.get("replacement_missing")
                        d_view["marginal_e"] = de.get("marginal_e")
                    if e_view and ee is not None:
                        e_view["replacement"] = ee.get("replacement")
                        e_view["replacement_missing"] = ee.get("replacement_missing")
                        e_view["marginal_e"] = ee.get("marginal_e")

                    ratios = [
                        r["r_over_v"]
                        for r in decision_join["collapse_pool"]
                        if r.get("r_over_v") is not None
                    ]
                    collapse_all_ratios.extend(ratios)
                    if decision_join["n_pool"]:
                        collapse_near_zero_fracs.append(
                            decision_join["n_near_zero_me"] / decision_join["n_pool"]
                        )

                    sac = {
                        "slot": slot,
                        "seed": seed,
                        "round": decision_join["round"],
                        "e_minus_d_full": ed,
                        "d": d_view,
                        "e": e_view,
                        "fork_actual_delta_e_minus_d": fork_act,
                        "n_near_zero_me": decision_join["n_near_zero_me"],
                        "n_pool": decision_join["n_pool"],
                        "near_zero_me_frac": (
                            round(
                                decision_join["n_near_zero_me"]
                                / decision_join["n_pool"],
                                4,
                            )
                            if decision_join["n_pool"]
                            else None
                        ),
                    }
                    if d_view and e_view:
                        md_d = d_view.get("marginal_d")
                        md_e = e_view.get("marginal_d")
                        if md_d is not None and md_e is not None:
                            sac["md_sacrifice_d_minus_e"] = round(
                                float(md_d) - float(md_e), 4
                            )
                        me_d = d_view.get("marginal_e")
                        me_e = e_view.get("marginal_e")
                        if me_d is not None and me_e is not None:
                            sac["me_adv_e_minus_d"] = round(
                                float(me_e) - float(me_d), 4
                            )
                    sacrifice_rows.append(sac)

            # Cascade after first fork
            post = []
            for j in range(fork["pick_index"] + 1, min(len(d_picks), len(e_picks))):
                if d_picks[j]["player_id"] != e_picks[j]["player_id"]:
                    post.append(
                        {
                            "pick_index": j,
                            "round": int(d_picks[j]["round"]),
                            "d": d_picks[j]["name"],
                            "e": e_picks[j]["name"],
                            "d_pos": d_picks[j]["position"],
                            "e_pos": e_picks[j]["position"],
                        }
                    )

            fork_row = {
                "pick_index": fork["pick_index"],
                "round": fork["round"],
                "d_name": fork["d_pick"]["name"],
                "e_name": fork["e_pick"]["name"],
                "d_pos": dp,
                "e_pos": ep,
                "d_actual": act_d,
                "e_actual": act_e,
                "fork_actual_delta_e_minus_d": fork_act,
                "n_subsequent_divergences": len(post),
                "subsequent_divergences_head": post[:5],
            }

        enriched.append(
            {
                "slot": slot,
                "seed": seed,
                "e_minus_d_full": ed,
                "e_minus_d_ex_dst_te": float(
                    pair["metrics"]["ex_dst_te"]["construction_gain_e_minus_d"]
                ),
                "n_changed_picks": n_changed,
                "pos_delta_starters": pos_d,
                "band_delta_starters": band_d,
                "pos_count_delta": count_delta,
                "fork": fork_row,
            }
        )

    if conn is not None:
        conn.close()

    # Interpretive findings (descriptive — not permission for E.1)
    findings: list[str] = []
    mean_ed = statistics.mean(
        [p["e_minus_d_full"] for p in enriched]
    )
    findings.append(
        f"E−D mean={mean_ed:+.2f} on {len(enriched)} boards "
        f"({n_boards_diverge} diverge at ≥1 pick)."
    )
    if fork_bands:
        findings.append(f"First-fork bands: {dict(fork_bands)}")
    if pos_transitions:
        top_t = pos_transitions.most_common(5)
        findings.append(f"Top first-fork transitions: {top_t}")
    if sacrifice_rows:
        md_sac = [
            r["md_sacrifice_d_minus_e"]
            for r in sacrifice_rows
            if r.get("md_sacrifice_d_minus_e") is not None
        ]
        if md_sac:
            findings.append(
                f"At first fork, mean M_D(D)−M_D(E)={statistics.mean(md_sac):+.2f} "
                f"(positive ⇒ E left higher M_D on the table)."
            )
        nz = [r["near_zero_me_frac"] for r in sacrifice_rows if r.get("near_zero_me_frac") is not None]
        if nz:
            findings.append(
                f"Mean fraction of pool with |M_E|≤1 at first fork: "
                f"{statistics.mean(nz):.1%}."
            )
    if collapse_all_ratios:
        findings.append(
            f"Pool r*/v at first forks: mean={statistics.mean(collapse_all_ratios):.3f}, "
            f"median={statistics.median(collapse_all_ratios):.3f}."
        )
    te_delta = _dist_summary(pos_deltas["TE"])
    findings.append(
        f"Starter TE E−D mean={te_delta['mean']:+.2f}; "
        f"RB mean={_dist_summary(pos_deltas['RB'])['mean']:+.2f}; "
        f"WR mean={_dist_summary(pos_deltas['WR'])['mean']:+.2f}."
    )

    return {
        "stage": "V3B0_FAILURE_AUDIT",
        "created_at": _utcnow(),
        "curve_id": CURVE_ID,
        "construction_id": CONSTRUCTION_ID,
        "contract_id": CONTRACT_ID,
        "evaluable": 0,
        "source_ladder": str(DEFAULT_LADDER),
        "claim": (
            "Descriptive audit of why V3-B.0 E−D failed. First D≠E divergence is "
            "the anchor; decision-time M_D/r*/M_E joined via targeted replay. "
            "No new objective; not E.1."
        ),
        "methodological_rule": (
            "Failure → mechanism audit → hypothesis → design contract → "
            "implementation. Do not tweak r* after this report."
        ),
        "contract": contract_meta(),
        "n_pairs": len(enriched),
        "findings": findings,
        "section1_divergence": {
            "n_boards_with_divergence": n_boards_diverge,
            "mean_changed_picks_per_board": round(
                n_changed_picks_total / len(enriched), 4
            )
            if enriched
            else None,
            "first_fork_rounds": dict(sorted(fork_rounds.items(), key=lambda x: int(x[0]))),
            "first_fork_bands": dict(fork_bands),
            "first_fork_d_positions": dict(d_pos),
            "first_fork_e_positions": dict(e_pos),
            "first_fork_transitions": dict(pos_transitions.most_common()),
        },
        "section2_attribution": {
            "fork_pick_actual_e_minus_d": _dist_summary(fork_actual_deltas),
            "starter_e_minus_d_by_pos": {
                pos: _dist_summary(pos_deltas[pos]) for pos in POS_ORDER
            },
            "starter_e_minus_d_by_band": {
                band: _dist_summary(band_deltas[band]) for band in ROUND_BANDS
            },
            "mean_starter_delta_by_pos": _mean_map(pos_deltas),
        },
        "section3_immediate_sacrifice": {
            "n_joined": len(sacrifice_rows),
            "rows": sacrifice_rows,
            "md_sacrifice_d_minus_e": _dist_summary(
                [
                    r["md_sacrifice_d_minus_e"]
                    for r in sacrifice_rows
                    if r.get("md_sacrifice_d_minus_e") is not None
                ]
            ),
            "me_adv_e_minus_d": _dist_summary(
                [
                    r["me_adv_e_minus_d"]
                    for r in sacrifice_rows
                    if r.get("me_adv_e_minus_d") is not None
                ]
            ),
            "fork_actual_when_joined": _dist_summary(
                [
                    r["fork_actual_delta_e_minus_d"]
                    for r in sacrifice_rows
                    if r.get("fork_actual_delta_e_minus_d") is not None
                ]
            ),
        },
        "section4_new_holes": {
            "mean_roster_count_delta_e_minus_d": {
                pos: round(statistics.mean(pos_count_deltas[pos]), 4)
                for pos in POS_ORDER
            },
            "note": (
                "Roster pick-count Δ (E−D), not starter points. "
                "ex-DST+TE E−D≈−117 elevates TE scrutiny."
            ),
            "starter_te_e_minus_d": _dist_summary(pos_deltas["TE"]),
            "starter_rb_e_minus_d": _dist_summary(pos_deltas["RB"]),
        },
        "section5_replacement_collapse": {
            "r_over_v_pool": _dist_summary(collapse_all_ratios),
            "near_zero_me_frac_by_board": _dist_summary(collapse_near_zero_fracs),
            "note": (
                "At first-fork decision pools: r*/v and fraction with |M_E|≤1. "
                "High r*/v + near-zero M_E ⇒ absolute valuation collapsed."
            ),
        },
        "pairs": enriched,
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    s1 = report["section1_divergence"]
    s2 = report["section2_attribution"]
    s3 = report["section3_immediate_sacrifice"]
    s4 = report["section4_new_holes"]
    s5 = report["section5_replacement_collapse"]
    lines = [
        "# V3-B.0 failure mechanism audit",
        "",
        f"- stage: `{report['stage']}`",
        f"- curve: `{report['curve_id']}` (frozen)",
        f"- construction: `{report['construction_id']}` (falsified)",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']}",
        f"- source: `{report['source_ladder']}`",
        "",
        report["claim"],
        "",
        f"**{report['methodological_rule']}**",
        "",
        "## Findings",
        "",
    ]
    for f in report["findings"]:
        lines.append(f"- {f}")

    lines.extend(
        [
            "",
            "## 1. Decision divergence",
            "",
            f"- boards with ≥1 D≠E pick: {s1['n_boards_with_divergence']}",
            f"- mean changed picks / board: {s1['mean_changed_picks_per_board']}",
            f"- first-fork bands: `{s1['first_fork_bands']}`",
            f"- first-fork rounds: `{s1['first_fork_rounds']}`",
            f"- D positions at first fork: `{s1['first_fork_d_positions']}`",
            f"- E positions at first fork: `{s1['first_fork_e_positions']}`",
            f"- transitions: `{s1['first_fork_transitions']}`",
            "",
            "## 2. Outcome attribution",
            "",
            f"- first-fork actual E−D: mean={_fmt(s2['fork_pick_actual_e_minus_d']['mean'])}, "
            f"WR(E)={s2['fork_pick_actual_e_minus_d']['win_rate']}",
            "",
            "| Pos | Mean starter E−D | Median | WR |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for pos in POS_ORDER:
        d = s2["starter_e_minus_d_by_pos"][pos]
        lines.append(
            f"| {pos} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{(d['win_rate'] or 0):.0%} |"
        )
    lines.extend(
        [
            "",
            "| Band | Mean starter E−D | Median | WR |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for band in ROUND_BANDS:
        d = s2["starter_e_minus_d_by_band"][band]
        lines.append(
            f"| {band} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{(d['win_rate'] or 0):.0%} |"
        )

    lines.extend(
        [
            "",
            "## 3. Immediate-value sacrifice (first fork)",
            "",
            f"- joined boards: {s3['n_joined']}",
            f"- mean M_D(D)−M_D(E): {_fmt(s3['md_sacrifice_d_minus_e']['mean'])}",
            f"- mean M_E(E)−M_E(D): {_fmt(s3['me_adv_e_minus_d']['mean'])}",
            f"- mean fork actual E−D: {_fmt(s3['fork_actual_when_joined']['mean'])}",
            "",
            "| Slot | Seed | R | D pick | E pick | M_D(D) | M_D(E) | r*(D) | r*(E) | "
            "M_E(D) | M_E(E) | act D | act E | Δact |",
            "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for r in s3["rows"]:
        d, e = r.get("d") or {}, r.get("e") or {}
        lines.append(
            f"| {r['slot']} | {r['seed']} | {r['round']} | "
            f"{d.get('name')} ({d.get('position')}) | "
            f"{e.get('name')} ({e.get('position')}) | "
            f"{_fmt(d.get('marginal_d'), False)} | {_fmt(e.get('marginal_d'), False)} | "
            f"{_fmt(d.get('replacement'), False)} | {_fmt(e.get('replacement'), False)} | "
            f"{_fmt(d.get('marginal_e'), False)} | {_fmt(e.get('marginal_e'), False)} | "
            f"{_fmt(d.get('actual_ppr'), False)} | {_fmt(e.get('actual_ppr'), False)} | "
            f"{_fmt(r.get('fork_actual_delta_e_minus_d'))} |"
        )

    lines.extend(
        [
            "",
            "## 4. New-hole analysis",
            "",
            s4["note"],
            "",
            f"- mean roster count Δ (E−D): `{s4['mean_roster_count_delta_e_minus_d']}`",
            f"- starter TE E−D: mean={_fmt(s4['starter_te_e_minus_d']['mean'])}, "
            f"median={_fmt(s4['starter_te_e_minus_d']['median'])}",
            f"- starter RB E−D: mean={_fmt(s4['starter_rb_e_minus_d']['mean'])}, "
            f"median={_fmt(s4['starter_rb_e_minus_d']['median'])}",
            "",
            "## 5. Replacement-collapse diagnostic",
            "",
            s5["note"],
            "",
            f"- r*/v (pool at first forks): mean={_fmt(s5['r_over_v_pool']['mean'], False)}, "
            f"median={_fmt(s5['r_over_v_pool']['median'], False)}, "
            f"p10={_fmt(s5['r_over_v_pool']['p10'], False)}, "
            f"p90={_fmt(s5['r_over_v_pool']['p90'], False)}",
            f"- |M_E|≤1 fraction by board: mean={_fmt(s5['near_zero_me_frac_by_board']['mean'], False)}, "
            f"median={_fmt(s5['near_zero_me_frac_by_board']['median'], False)}",
            "",
            "## Status",
            "",
            "- V3-B.0: 🔴 falsified (`5a2d4fc`)",
            "- E.1: 🔴 not opened",
            "- UI: `marginal`",
            "- map: frozen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-B.0 failure mechanism audit")
    parser.add_argument("--ladder", type=Path, default=DEFAULT_LADDER)
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument("--no-decision-join", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3b0_failure_audit.md"),
    )
    args = parser.parse_args()
    ladder = json.loads(args.ladder.read_text(encoding="utf-8"))
    report = analyze(
        ladder,
        draft_db=args.draft_db,
        join_decision_time=not args.no_decision_join,
    )
    # Slim: drop bulky collapse pools already aggregated
    slim = dict(report)
    md = _md(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
