"""P2.2C C−B valuation mechanism report (no new drafts).

Reads results/phase2_p22c_adp_feasible_ladder.json and decomposes
valuation_gain = adp_structural − adp_feasible by:

1. Position (starter attribution)
2. Round / round-band (starter attribution via lineup_ev)
3. Draft slot
4. Left tail (worst valuation_gain pairs)

Does not change strategies, curve, or evaluable. Not V3.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt.config import get_roster_preset
from draftopt.lineup import lineup_ev
from draftopt.phase2.diagnose_delta_p22c import _dist_summary
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    ROSTER_PRESET,
    contract_meta,
)

POS_ORDER = ("QB", "RB", "WR", "TE", "DST", "K")
ROUND_BANDS = ("r1-5", "r6-10", "r11-15")
DEFAULT_LADDER = Path("results/phase2_p22c_adp_feasible_ladder.json")
STRAT_B = "adp_feasible"
STRAT_C = "adp_structural"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _round_band(rnd: int) -> str:
    if rnd <= 5:
        return "r1-5"
    if rnd <= 10:
        return "r6-10"
    return "r11-15"


def _roster_from_picks(picks: list[dict]) -> list[dict]:
    return [
        {
            "player_id": p["player_id"],
            "name": p["name"],
            "position": p["position"],
            "season_points": float(p["actual_ppr"]),
            "draft_round": int(p["round"]),
            "overall": int(p["overall"]),
        }
        for p in picks
    ]


def _starter_contrib(picks: list[dict], slots: dict[str, int]) -> dict:
    """Starter actual-PPR totals by position, round, and round-band."""
    roster = _roster_from_picks(picks)
    lined = lineup_ev(roster, slots)
    starter_ids = {
        p["player_id"]
        for slot_players in lined.starters.values()
        for p in slot_players
    }
    by_pos: dict[str, float] = defaultdict(float)
    by_round: dict[int, float] = defaultdict(float)
    by_band: dict[str, float] = defaultdict(float)
    starter_picks: list[dict] = []
    for p in roster:
        if p["player_id"] not in starter_ids:
            continue
        pos = (p["position"] or "?").upper()
        rnd = int(p["draft_round"])
        pts = float(p["season_points"])
        by_pos[pos] += pts
        by_round[rnd] += pts
        by_band[_round_band(rnd)] += pts
        starter_picks.append(
            {
                "round": rnd,
                "overall": int(p["overall"]),
                "player_id": p["player_id"],
                "name": p["name"],
                "position": pos,
                "actual_ppr": pts,
            }
        )
    return {
        "total": round(lined.total, 4),
        "by_pos": dict(by_pos),
        "by_round": {str(k): v for k, v in sorted(by_round.items())},
        "by_band": dict(by_band),
        "starter_picks": starter_picks,
    }


def _mean_map(d: dict[str, list[float]]) -> dict[str, float]:
    return {k: round(statistics.mean(v), 4) if v else 0.0 for k, v in d.items()}


def _se_above_chance(win_rate: float, n: int) -> dict:
    """Binomial SE under H0: p=0.5; z = (wr - 0.5) / se."""
    se = math.sqrt(0.25 / n) if n else float("nan")
    z = (win_rate - 0.5) / se if se and se > 0 else float("nan")
    return {
        "n": n,
        "win_rate": round(win_rate, 4),
        "se_under_null_50": round(se, 4),
        "z_vs_50": round(z, 4),
        "note": (
            "Approximate; treats pairs as iid Bernoulli under H0 p=0.5. "
            "Not a formal test of effect size."
        ),
    }


def _pick_diff(b_picks: list[dict], c_picks: list[dict]) -> dict:
    b_ids = {p["player_id"]: p for p in b_picks}
    c_ids = {p["player_id"]: p for p in c_picks}
    only_c = [c_ids[i] for i in c_ids if i not in b_ids]
    only_b = [b_ids[i] for i in b_ids if i not in c_ids]
    only_c.sort(key=lambda p: int(p["overall"]))
    only_b.sort(key=lambda p: int(p["overall"]))
    return {
        "n_shared": len(set(b_ids) & set(c_ids)),
        "n_only_structural": len(only_c),
        "n_only_feasible": len(only_b),
        "only_structural": only_c,
        "only_feasible": only_b,
    }


def analyze_ladder(ladder: dict, *, n_tail: int = 10) -> dict:
    slots_cfg = get_roster_preset(ROSTER_PRESET)["slots"]
    pairs_in = ladder["pairs"]

    pos_deltas: dict[str, list[float]] = defaultdict(list)
    band_deltas: dict[str, list[float]] = defaultdict(list)
    round_deltas: dict[str, list[float]] = defaultdict(list)
    slot_gains: dict[int, list[float]] = defaultdict(list)
    enriched: list[dict] = []

    for pair in pairs_in:
        slot = int(pair["slot"])
        seed = int(pair["seed"])
        vg_full = float(pair["metrics"]["full"]["valuation_gain"])
        vg_ex = float(pair["metrics"]["ex_dst"]["valuation_gain"])
        vg_ex_te = float(pair["metrics"]["ex_dst_te"]["valuation_gain"])

        b_contrib = _starter_contrib(pair["picks"][STRAT_B], slots_cfg)
        c_contrib = _starter_contrib(pair["picks"][STRAT_C], slots_cfg)

        # Prefer recomputed totals; cross-check vs stored metrics
        recomputed_vg = round(c_contrib["total"] - b_contrib["total"], 4)

        pos_d: dict[str, float] = {}
        for pos in POS_ORDER:
            d = float(c_contrib["by_pos"].get(pos, 0.0)) - float(
                b_contrib["by_pos"].get(pos, 0.0)
            )
            pos_d[pos] = round(d, 4)
            pos_deltas[pos].append(d)

        band_d: dict[str, float] = {}
        for band in ROUND_BANDS:
            d = float(c_contrib["by_band"].get(band, 0.0)) - float(
                b_contrib["by_band"].get(band, 0.0)
            )
            band_d[band] = round(d, 4)
            band_deltas[band].append(d)

        # Per-round: union of rounds present in either
        rounds = set(b_contrib["by_round"]) | set(c_contrib["by_round"])
        round_d: dict[str, float] = {}
        for r in sorted(rounds, key=int):
            d = float(c_contrib["by_round"].get(r, 0.0)) - float(
                b_contrib["by_round"].get(r, 0.0)
            )
            round_d[r] = round(d, 4)
            round_deltas[r].append(d)

        slot_gains[slot].append(vg_full)
        diff = _pick_diff(pair["picks"][STRAT_B], pair["picks"][STRAT_C])

        enriched.append(
            {
                "slot": slot,
                "seed": seed,
                "valuation_gain_full": vg_full,
                "valuation_gain_ex_dst": vg_ex,
                "valuation_gain_ex_dst_te": vg_ex_te,
                "recomputed_valuation_gain": recomputed_vg,
                "pos_delta": pos_d,
                "band_delta": band_d,
                "round_delta": round_d,
                "pick_diff": {
                    "n_shared": diff["n_shared"],
                    "n_only_structural": diff["n_only_structural"],
                    "n_only_feasible": diff["n_only_feasible"],
                    "only_structural": diff["only_structural"],
                    "only_feasible": diff["only_feasible"],
                },
            }
        )

    vg_full = [p["valuation_gain_full"] for p in enriched]
    vg_ex = [p["valuation_gain_ex_dst"] for p in enriched]
    vg_ex_te = [p["valuation_gain_ex_dst_te"] for p in enriched]
    n = len(enriched)

    by_slot = []
    for slot in sorted(slot_gains):
        vals = slot_gains[slot]
        by_slot.append(
            {
                "slot": slot,
                "n": len(vals),
                "mean_valuation_gain": round(statistics.mean(vals), 4),
                "median_valuation_gain": round(statistics.median(vals), 4),
                "win_rate": round(sum(1 for v in vals if v > 0) / len(vals), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
            }
        )

    # Left tail: worst n_tail by full valuation_gain
    worst = sorted(enriched, key=lambda p: p["valuation_gain_full"])[:n_tail]
    best = sorted(enriched, key=lambda p: p["valuation_gain_full"], reverse=True)[
        : min(5, n_tail)
    ]

    # Tail structure: which positions drive losses among worst?
    tail_pos_means = {
        pos: round(
            statistics.mean([w["pos_delta"].get(pos, 0.0) for w in worst]), 4
        )
        for pos in POS_ORDER
    }
    tail_band_means = {
        band: round(
            statistics.mean([w["band_delta"].get(band, 0.0) for w in worst]), 4
        )
        for band in ROUND_BANDS
    }
    tail_slots = Counter(w["slot"] for w in worst)

    # Positional concentration of mean C−B
    mean_pos = _mean_map(pos_deltas)
    pos_sum = sum(abs(v) for v in mean_pos.values()) or 1.0

    return {
        "stage": "P2.2C_valuation_cb_mechanism",
        "created_at": _utcnow(),
        "snapshot_id": ladder.get("snapshot_id", DECISION_SNAPSHOT_ID),
        "contract_id": ladder.get("contract_id", CONTRACT_ID),
        "evaluable": 0,
        "source_ladder": str(DEFAULT_LADDER),
        "claim": (
            "Mechanism decomposition of valuation_gain (adp_structural − "
            "adp_feasible) under ppr_eval_v1_2024. Attribution only "
            "(no re-draft). Modeled opponents; n=1 season."
        ),
        "note": (
            "Load-bearing quantity is C−B. Left-tail characterization precedes "
            "mean chasing. V3 still blocked. UI stays marginal."
        ),
        "contract": contract_meta(),
        "n_pairs": n,
        "valuation_gain_summary": {
            "full": _dist_summary(vg_full),
            "ex_dst": _dist_summary(vg_ex),
            "ex_dst_te": _dist_summary(vg_ex_te),
        },
        "win_rate_vs_chance": {
            "full": _se_above_chance(
                sum(1 for v in vg_full if v > 0) / n, n
            ),
            "ex_dst": _se_above_chance(
                sum(1 for v in vg_ex if v > 0) / n, n
            ),
            "ex_dst_te": _se_above_chance(
                sum(1 for v in vg_ex_te if v > 0) / n, n
            ),
        },
        "by_position": {
            "mean_delta": mean_pos,
            "share_of_abs_mean": {
                k: round(abs(v) / pos_sum, 4) for k, v in mean_pos.items()
            },
            "distributions": {pos: _dist_summary(pos_deltas[pos]) for pos in POS_ORDER},
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
        "left_tail": {
            "n": len(worst),
            "selection": f"worst {n_tail} pairs by full valuation_gain",
            "mean_valuation_gain": round(
                statistics.mean([w["valuation_gain_full"] for w in worst]), 4
            ),
            "mean_pos_delta": tail_pos_means,
            "mean_band_delta": tail_band_means,
            "slot_counts": dict(sorted(tail_slots.items())),
            "pairs": worst,
        },
        "right_tail_sample": best,
        "pairs": enriched,
    }


def _fmt(v: float | None, signed: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v:+.2f}" if signed else f"{v:.2f}"


def _md(report: dict) -> str:
    vg = report["valuation_gain_summary"]
    wr = report["win_rate_vs_chance"]
    lines = [
        "# P2.2C C−B valuation mechanism",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- evaluable: **{report['evaluable']}**",
        f"- pairs: {report['n_pairs']}",
        f"- source: `{report['source_ladder']}`",
        "",
        report["claim"],
        "",
        f"**{report['note']}**",
        "",
        "## Charter reminder",
        "",
        "> Core thesis: 🟡 preliminary support (C−B > 0 after feasibility + DST "
        "controls). External validity 🔴. V3 conceptually justified, "
        "implementation blocked pending C−B mechanism. UI: `marginal`.",
        "",
        "## Valuation gain (C−B) distribution",
        "",
        "| Contract | Mean | Median | SD | WR | z vs 50% | n_neg | min | p10 | p90 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, label in (
        ("full", "Full"),
        ("ex_dst", "Ex-DST"),
        ("ex_dst_te", "Ex-DST+TE"),
    ):
        d = vg[key]
        z = wr[key]
        lines.append(
            f"| {label} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{_fmt(d['stdev'], signed=False)} | {d['win_rate']:.0%} | "
            f"{z['z_vs_50']:+.1f} SE | {d['n_negative']} | {_fmt(d['min'])} | "
            f"{_fmt(d['p10'])} | {_fmt(d['p90'])} |"
        )
    lines.extend(
        [
            "",
            f"Under H0 p=0.5, SE ≈ {wr['full']['se_under_null_50']:.1%} for n={report['n_pairs']}. "
            f"Ex-DST ({wr['ex_dst']['z_vs_50']:+.1f} SE) is the load-bearing win-rate claim; "
            f"Ex-DST+TE ({wr['ex_dst_te']['z_vs_50']:+.1f} SE) is not distinguishable from "
            "chance at this n.",
            "",
            "## 1. Position contribution to C−B",
            "",
            "Mean starter actual-PPR difference (structural − feasible), attribution only.",
            "",
            "| Pos | Mean Δ | Median Δ | WR (pos Δ>0) |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for pos in POS_ORDER:
        d = report["by_position"]["distributions"][pos]
        lines.append(
            f"| {pos} | {_fmt(d['mean'])} | {_fmt(d['median'])} | "
            f"{(d['win_rate'] or 0):.0%} |"
        )
    mean_pos = report["by_position"]["mean_delta"]
    lines.extend(
        [
            "",
            f"Sum of mean pos Δ = {_fmt(sum(mean_pos.values()))} "
            "(should ≈ full mean C−B).",
            "",
            "## 2. Round / round-band",
            "",
            "### Round bands",
            "",
            "| Band | Mean Δ | Median Δ | WR |",
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
            "### By draft round (starter contrib)",
            "",
            "| Round | Mean Δ |",
            "| --- | ---: |",
        ]
    )
    for r, v in report["by_round"]["mean_delta"].items():
        lines.append(f"| {r} | {_fmt(v)} |")

    lines.extend(
        [
            "",
            "## 3. Draft slot",
            "",
            "| Slot | n | Mean C−B | Median | WR | min | max |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["by_slot"]:
        lines.append(
            f"| {row['slot']} | {row['n']} | {_fmt(row['mean_valuation_gain'])} | "
            f"{_fmt(row['median_valuation_gain'])} | {row['win_rate']:.0%} | "
            f"{_fmt(row['min'])} | {_fmt(row['max'])} |"
        )

    tail = report["left_tail"]
    lines.extend(
        [
            "",
            "## 4. Left tail",
            "",
            f"Worst {tail['n']} pairs by full valuation_gain "
            f"(mean C−B among them: {_fmt(tail['mean_valuation_gain'])}).",
            "",
            "### Mean pos / band Δ among left-tail pairs",
            "",
            "| Pos | Mean Δ in tail |",
            "| --- | ---: |",
        ]
    )
    for pos in POS_ORDER:
        lines.append(f"| {pos} | {_fmt(tail['mean_pos_delta'][pos])} |")
    lines.extend(
        [
            "",
            "| Band | Mean Δ in tail |",
            "| --- | ---: |",
        ]
    )
    for band in ROUND_BANDS:
        lines.append(f"| {band} | {_fmt(tail['mean_band_delta'][band])} |")
    lines.extend(
        [
            "",
            f"Tail slot counts: `{tail['slot_counts']}`",
            "",
            "### Worst pairs (detail)",
            "",
        ]
    )
    for w in tail["pairs"]:
        lines.append(
            f"#### Slot {w['slot']} seed {w['seed']} — "
            f"C−B {_fmt(w['valuation_gain_full'])} "
            f"(ex-DST {_fmt(w['valuation_gain_ex_dst'])})"
        )
        lines.append("")
        lines.append(
            "Pos Δ: "
            + ", ".join(f"{p} {_fmt(w['pos_delta'][p])}" for p in POS_ORDER)
        )
        lines.append("")
        lines.append(
            "Band Δ: "
            + ", ".join(f"{b} {_fmt(w['band_delta'][b])}" for b in ROUND_BANDS)
        )
        lines.append("")
        pd = w["pick_diff"]
        lines.append(
            f"Roster overlap: {pd['n_shared']} shared; "
            f"{pd['n_only_structural']} only structural; "
            f"{pd['n_only_feasible']} only feasible."
        )
        lines.append("")
        if pd["only_structural"]:
            lines.append("Only structural:")
            for p in pd["only_structural"]:
                lines.append(
                    f"- R{p['round']} {p['name']} ({p['position']}) "
                    f"{float(p['actual_ppr']):+.1f}"
                )
            lines.append("")
        if pd["only_feasible"]:
            lines.append("Only feasible:")
            for p in pd["only_feasible"]:
                lines.append(
                    f"- R{p['round']} {p['name']} ({p['position']}) "
                    f"{float(p['actual_ppr']):+.1f}"
                )
            lines.append("")

    lines.extend(
        [
            "## Status",
            "",
            "- Mechanism report: 🟢 complete (attribution; same 60 pairs)",
            "- V3: 🔴 implementation blocked until this report is interpreted",
            "- UI: `marginal`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C C−B valuation mechanism")
    parser.add_argument("--ladder", type=Path, default=DEFAULT_LADDER)
    parser.add_argument("--n-tail", type=int, default=10)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_valuation_cb_mechanism.md"),
    )
    args = parser.parse_args()
    if not args.ladder.is_file():
        raise SystemExit(f"missing ladder JSON: {args.ladder}")
    ladder = json.loads(args.ladder.read_text(encoding="utf-8"))
    report = analyze_ladder(ladder, n_tail=args.n_tail)
    report["source_ladder"] = str(args.ladder)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    # JSON without full pair pick dumps already in enriched — keep enriched
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
