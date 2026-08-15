"""P2.2C decision-space coverage report (before nflverse PPR attach).

Board coverage ≠ outcome coverage. Unmapped players still draft as ffc:{id}
but cannot join actual PPR — silent evaluator losses.

Does not set evaluable=1. Does not attach outcomes. Does not retune the curve.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import parse_slots
from draftopt.config import EVAL_DB_PATH
from draftopt.phase2 import connect_eval
from draftopt.phase2.adp_value_curve import CURVE_ID
from draftopt.phase2.materialize_p22c import (
    P22C_DB_PATH,
    SNAPSHOT_ID,
    materialize,
)
from draftopt.phase2.smoke_p22c import DEFAULT_ROSTER, N_ROUNDS, N_TEAMS, STRATEGIES

TOP_N = (50, 100, 150)
ADP_BANDS = (
    ("1-50", 1, 50),
    ("51-100", 51, 100),
    ("101-150", 101, 150),
    ("151+", 151, 10_000),
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _adp_rank_order(players: list[dict]) -> list[dict]:
    """Lowest ADP first; missing ADP last. Rank is 1-based among all snapshot players."""
    with_adp = [p for p in players if p.get("adp") is not None]
    without = [p for p in players if p.get("adp") is None]
    with_adp.sort(key=lambda p: (float(p["adp"]), p.get("name") or "", p["player_id"]))
    ordered = with_adp + without
    for i, p in enumerate(ordered, start=1):
        p["adp_rank"] = i
    return ordered


def _load_snapshot_universe(eval_conn, snapshot_id: str) -> dict:
    snap = eval_conn.execute(
        """
        SELECT snapshot_id, snapshot_date, evaluable, validation_status, validation_reason
        FROM eval_snapshots WHERE snapshot_id = ?
        """,
        (snapshot_id,),
    ).fetchone()
    if snap is None:
        raise RuntimeError(f"missing snapshot {snapshot_id}; run materialize_p22c first")

    rows = eval_conn.execute(
        """
        SELECT player_id, name, position, team, adp, adp_source, proj_ppr, proj_source
        FROM eval_snapshot_players WHERE snapshot_id = ?
        """,
        (snapshot_id,),
    ).fetchall()
    players = [dict(r) for r in rows]

    mapped_rows = eval_conn.execute(
        """
        SELECT source_player_id, player_id, gsis_id, method
        FROM eval_player_map WHERE source = 'ffc'
        """
    ).fetchall()
    unresolved_rows = eval_conn.execute(
        """
        SELECT source_player_id, name, position, team, reason
        FROM eval_player_unresolved WHERE source = 'ffc'
        """
    ).fetchall()

    mapped_by_canonical = {r["player_id"]: dict(r) for r in mapped_rows}
    unresolved_ffc = {r["source_player_id"]: dict(r) for r in unresolved_rows}

    for p in players:
        pid = p["player_id"]
        pos = (p.get("position") or "").upper()
        if pid.startswith("ffc:"):
            ffc_id = pid.split(":", 1)[1]
            p["mapped"] = False
            p["has_gsis"] = False
            p["has_outcome_key"] = False
            p["map_method"] = None
            p["ffc_player_id"] = ffc_id
            u = unresolved_ffc.get(ffc_id) or {}
            p["unresolved_reason"] = u.get("reason") or "ffc_prefix_unmapped"
        else:
            m = mapped_by_canonical.get(pid)
            p["mapped"] = m is not None or (
                pos == "DST" and pid.startswith("dst:")
            )
            p["has_gsis"] = bool(m and m.get("gsis_id"))
            # Offense/K need GSIS; DST uses team entity dst:{TEAM} (no GSIS).
            if pos == "DST":
                team_code = pid.split(":", 1)[-1] if pid.startswith("dst:") else ""
                p["has_outcome_key"] = bool(p["mapped"] and len(team_code) >= 2)
            else:
                p["has_outcome_key"] = bool(p["has_gsis"])
            if m:
                p["map_method"] = m.get("method")
                p["ffc_player_id"] = m.get("source_player_id")
            else:
                p["map_method"] = "dst_team" if pid.startswith("dst:") else None
                p["ffc_player_id"] = None
            p["unresolved_reason"] = None if p["mapped"] else "canonical_not_in_map"

    ordered = _adp_rank_order(players)
    return {
        "snapshot": dict(snap),
        "players": ordered,
        "n_players": len(ordered),
        "n_mapped": sum(1 for p in ordered if p["mapped"]),
        "n_mapped_with_gsis": sum(1 for p in ordered if p["has_gsis"]),
        "n_outcome_ready": sum(1 for p in ordered if p["has_outcome_key"]),
        "n_unmapped": sum(1 for p in ordered if not p["mapped"]),
        "unresolved_table": [dict(r) for r in unresolved_rows],
    }


def _band_for_rank(rank: int) -> str:
    for label, lo, hi in ADP_BANDS:
        if lo <= rank <= hi:
            return label
    return "151+"


def _coverage_slice(players: list[dict], *, top_n: int | None = None) -> dict:
    subset = players if top_n is None else players[:top_n]
    n = len(subset)
    n_mapped = sum(1 for p in subset if p["mapped"])
    n_gsis = sum(1 for p in subset if p["has_gsis"])
    n_ready = sum(1 for p in subset if p.get("has_outcome_key"))
    return {
        "n": n,
        "n_mapped": n_mapped,
        "n_unmapped": n - n_mapped,
        "n_mapped_with_gsis": n_gsis,
        "n_outcome_ready": n_ready,
        "coverage": (n_mapped / n) if n else 0.0,
        "gsis_coverage": (n_gsis / n) if n else 0.0,
        "outcome_key_coverage": (n_ready / n) if n else 0.0,
        "unmapped": [
            {
                "player_id": p["player_id"],
                "name": p.get("name"),
                "position": p.get("position"),
                "team": p.get("team"),
                "adp": p.get("adp"),
                "adp_rank": p.get("adp_rank"),
                "reason": p.get("unresolved_reason"),
            }
            for p in subset
            if not p["mapped"]
        ],
    }


def _by_position(players: list[dict]) -> dict[str, dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for p in players:
        groups[(p.get("position") or "?").upper()].append(p)
    return {pos: _coverage_slice(ps) for pos, ps in sorted(groups.items())}


def _by_adp_band(players: list[dict]) -> dict[str, dict]:
    groups: dict[str, list[dict]] = {label: [] for label, _, _ in ADP_BANDS}
    for p in players:
        groups[_band_for_rank(int(p["adp_rank"]))].append(p)
    return {label: _coverage_slice(groups[label]) for label, _, _ in ADP_BANDS}


def _lookup(players: list[dict]) -> dict[str, dict]:
    return {p["player_id"]: p for p in players}


def _run_one_with_id(
    conn,
    *,
    strategy_name: str,
    user_slot: int,
    seed: int,
):
    """Like backtest.run_one but also returns draft_id for board scans."""
    from draftopt.backtest import _user_pick_log, pick_rng
    from draftopt.draft.cpu import cpu_pick
    from draftopt.draft.state import (
        create_draft,
        is_user_turn,
        record_user_pick,
        snapshot,
    )
    from draftopt.strategies import get_strategy

    strategy = get_strategy(strategy_name)
    draft_id = create_draft(
        conn,
        user_slot=user_slot,
        user_name=f"Bot-{strategy_name}",
        roster_preset=DEFAULT_ROSTER,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
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
                policy="noisy_adp",
            )
    picks = _user_pick_log(conn, draft_id, user_slot)
    return draft_id, picks


def _run_drafted_unmapped(
    *,
    draft_db: Path,
    players: list[dict],
    slots: list[int],
    n_sims: int,
    seed0: int,
) -> dict:
    by_id = _lookup(players)
    conn = live_db.connect(draft_db)
    live_db.init(conn)

    strategy_hits: dict[str, list[dict]] = {s: [] for s in STRATEGIES}
    board_hits: list[dict] = []
    n_user_picks = 0
    n_board_picks = 0

    for slot in slots:
        for strategy in STRATEGIES:
            for i in range(n_sims):
                seed = seed0 + i
                draft_id, picks = _run_one_with_id(
                    conn,
                    strategy_name=strategy,
                    user_slot=slot,
                    seed=seed,
                )
                for pick in picks:
                    n_user_picks += 1
                    meta = by_id.get(pick["player_id"])
                    mapped = bool(meta and meta["mapped"])
                    outcome_ok = bool(meta and meta.get("has_outcome_key"))
                    if not mapped or not outcome_ok:
                        strategy_hits[strategy].append(
                            {
                                "strategy": strategy,
                                "slot": slot,
                                "seed": seed,
                                "round": pick["round"],
                                "overall": pick["overall"],
                                "player_id": pick["player_id"],
                                "name": pick.get("name"),
                                "position": pick.get("position"),
                                "adp": meta.get("adp") if meta else pick.get("adp_espn"),
                                "adp_rank": meta.get("adp_rank") if meta else None,
                                "mapped": mapped,
                                "has_gsis": bool(meta and meta.get("has_gsis")),
                                "has_outcome_key": outcome_ok,
                                "reason": (
                                    None
                                    if mapped and outcome_ok
                                    else (
                                        meta.get("unresolved_reason")
                                        if meta
                                        else "not_in_snapshot"
                                    )
                                ),
                            }
                        )

                board_rows = conn.execute(
                    """
                    SELECT pk.overall, pk.round, pk.team_slot, pk.made_by,
                           p.player_id, p.name, p.position
                    FROM picks pk
                    JOIN players p ON p.player_id = pk.player_id
                    WHERE pk.draft_id = ?
                    ORDER BY pk.overall
                    """,
                    (draft_id,),
                ).fetchall()
                for row in board_rows:
                    n_board_picks += 1
                    meta = by_id.get(row["player_id"])
                    mapped = bool(meta and meta["mapped"])
                    outcome_ok = bool(meta and meta.get("has_outcome_key"))
                    if not mapped or not outcome_ok:
                        board_hits.append(
                            {
                                "strategy_run": strategy,
                                "slot": slot,
                                "seed": seed,
                                "overall": int(row["overall"]),
                                "round": int(row["round"]),
                                "team_slot": int(row["team_slot"]),
                                "made_by": row["made_by"],
                                "player_id": row["player_id"],
                                "name": row["name"],
                                "position": row["position"],
                                "adp": meta.get("adp") if meta else None,
                                "adp_rank": meta.get("adp_rank") if meta else None,
                                "mapped": mapped,
                                "has_gsis": bool(meta and meta.get("has_gsis")),
                                "has_outcome_key": outcome_ok,
                            }
                        )
    conn.close()

    # Dedup strategy hits by player for summary
    def _uniq(hits: list[dict]) -> list[dict]:
        seen: set[str] = set()
        out: list[dict] = []
        for h in sorted(hits, key=lambda x: (x.get("adp_rank") or 9999, x["player_id"])):
            if h["player_id"] in seen:
                continue
            seen.add(h["player_id"])
            out.append(h)
        return out

    n_strat_unmapped = {s: len(strategy_hits[s]) for s in STRATEGIES}
    gate_ok = all(n == 0 for n in n_strat_unmapped.values())

    return {
        "slots": slots,
        "n_sims": n_sims,
        "seed0": seed0,
        "n_user_picks_scanned": n_user_picks,
        "n_board_picks_scanned": n_board_picks,
        "strategy_unmapped_pick_events": n_strat_unmapped,
        "strategy_unmapped_unique": {s: _uniq(strategy_hits[s]) for s in STRATEGIES},
        "strategy_unmapped_events": strategy_hits,
        "board_unmapped_pick_events": len(board_hits),
        "board_unmapped_unique": _uniq(board_hits),
        "gate_strategy_unmapped_zero": gate_ok,
    }


def build_report(
    *,
    raw_json: Path | None = None,
    eval_db: Path | None = None,
    draft_db: Path | None = None,
    slots: list[int] | None = None,
    n_sims: int = 3,
    seed0: int = 42,
    rematerialize: bool = False,
) -> dict:
    draft_path = draft_db or P22C_DB_PATH
    eval_path = eval_db or EVAL_DB_PATH
    mat = None
    if rematerialize or not draft_path.is_file():
        mat = materialize(raw_json=raw_json, eval_path=eval_path, draft_db=draft_path)

    eval_conn = connect_eval(eval_path)
    universe = _load_snapshot_universe(eval_conn, SNAPSHOT_ID)
    eval_conn.close()

    players = universe["players"]
    overall = _coverage_slice(players)
    tops = {f"top_{n}": _coverage_slice(players, top_n=n) for n in TOP_N}

    drafted = _run_drafted_unmapped(
        draft_db=draft_path,
        players=players,
        slots=slots or [1, 5, 10],
        n_sims=n_sims,
        seed0=seed0,
    )

    # Decision-space gate reasons (evaluable stays 0 regardless)
    reasons: list[str] = []
    if overall["n_unmapped"] > 0:
        reasons.append("unmapped_players_remain")
    if any(tops[f"top_{n}"]["n_unmapped"] > 0 for n in (50, 100, 150)):
        reasons.append("unmapped_in_top_adp_bands")
    if not drafted["gate_strategy_unmapped_zero"]:
        reasons.append("strategy_selected_unmapped_or_no_outcome_key")

    gate = "pass" if not reasons else "fail"

    return {
        "stage": "P2.2C_decision_space_coverage",
        "created_at": _utcnow(),
        "snapshot_id": SNAPSHOT_ID,
        "evaluable": 0,
        "decision_market": "FFC",
        "league_size": N_TEAMS,
        "value_signal": CURVE_ID,
        "note": (
            "Board coverage ≠ outcome coverage. Unmapped ffc:* players remain "
            "draftable but are silent losses for actual-PPR scoring. "
            "No nflverse attach in this report. Not production marginal."
        ),
        "materialize": mat,
        "snapshot_meta": universe["snapshot"],
        "overall": {
            **overall,
            "n_mapped_with_gsis": universe["n_mapped_with_gsis"],
            "n_outcome_ready": universe["n_outcome_ready"],
            "gsis_coverage": (
                universe["n_mapped_with_gsis"] / universe["n_players"]
                if universe["n_players"]
                else 0.0
            ),
            "outcome_key_coverage": (
                universe["n_outcome_ready"] / universe["n_players"]
                if universe["n_players"]
                else 0.0
            ),
        },
        "top_adp": tops,
        "by_position": _by_position(players),
        "by_adp_band": _by_adp_band(players),
        "unmapped_all": overall["unmapped"],
        "drafted": drafted,
        "decision_space_gate": gate,
        "decision_space_gate_reasons": reasons,
        "next": (
            "decision_space_gate=pass — safe to attach nflverse 2024 PPR next. "
            "DST outcomes still need team-level scoring (dst:TEAM), not GSIS player weeks. "
            "Keep evaluable=0 until outcome coverage gates pass. Do not retune ADP curve."
            if gate == "pass"
            else (
                "Fix high-value unmapped (Jr/Sr/III/nicknames/DST), rematerialize, "
                "re-run this report until gate=pass; then attach nflverse PPR."
            )
        ),
    }


def _md(report: dict) -> str:
    o = report["overall"]
    lines = [
        "# P2.2C decision-space coverage",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- evaluable: **{report['evaluable']}** (locked)",
        f"- decision_space_gate: **{report['decision_space_gate']}**",
        f"- reasons: {', '.join(report['decision_space_gate_reasons']) or 'none'}",
        "",
        report["note"],
        "",
        "## Overall mapping",
        "",
        f"| Metric | Value |",
        f"| --- | ---: |",
        f"| Players | {o['n']} |",
        f"| Mapped | {o['n_mapped']} ({o['coverage']:.1%}) |",
        f"| Unmapped | {o['n_unmapped']} |",
        f"| Mapped with gsis | {o['n_mapped_with_gsis']} ({o['gsis_coverage']:.1%}) |",
        f"| Outcome-ready (gsis or dst:TEAM) | {o['n_outcome_ready']} ({o['outcome_key_coverage']:.1%}) |",
        "",
        "_Prior failed report preserved at `phase2_p22c_decision_space_coverage.md` (v1)._",
        "",
        "## Top-N ADP coverage (lowest ADP)",
        "",
        "| Band | n | mapped | unmapped | coverage |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for n in TOP_N:
        t = report["top_adp"][f"top_{n}"]
        lines.append(
            f"| Top {n} | {t['n']} | {t['n_mapped']} | {t['n_unmapped']} | {t['coverage']:.1%} |"
        )

    lines.extend(["", "## Unmapped by ADP band", ""])
    lines.append("| Band | n | mapped | unmapped | coverage |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for label, band in report["by_adp_band"].items():
        lines.append(
            f"| {label} | {band['n']} | {band['n_mapped']} | "
            f"{band['n_unmapped']} | {band['coverage']:.1%} |"
        )

    lines.extend(["", "## Unmapped by position", ""])
    lines.append("| Pos | n | mapped | unmapped | coverage |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for pos, band in report["by_position"].items():
        lines.append(
            f"| {pos} | {band['n']} | {band['n_mapped']} | "
            f"{band['n_unmapped']} | {band['coverage']:.1%} |"
        )

    lines.extend(["", "## All unmapped (ADP-ranked)", ""])
    lines.append("| ADP rank | ADP | Pos | Name | Team | reason |")
    lines.append("| ---: | ---: | --- | --- | --- | --- |")
    for u in report["unmapped_all"]:
        adp = f"{u['adp']:.1f}" if u.get("adp") is not None else "—"
        lines.append(
            f"| {u.get('adp_rank')} | {adp} | {u.get('position')} | "
            f"{u.get('name')} | {u.get('team') or '—'} | {u.get('reason')} |"
        )

    d = report["drafted"]
    lines.extend(
        [
            "",
            "## Strategy selections of unmapped / no-gsis",
            "",
            f"- slots: {d['slots']} · n_sims: {d['n_sims']} · seed0: {d['seed0']}",
            f"- user picks scanned: {d['n_user_picks_scanned']}",
            f"- gate_strategy_unmapped_zero: **{d['gate_strategy_unmapped_zero']}**",
            "",
        ]
    )
    for strat in STRATEGIES:
        uniq = d["strategy_unmapped_unique"][strat]
        events = d["strategy_unmapped_pick_events"][strat]
        lines.append(f"### `{strat}` — {events} pick-events, {len(uniq)} unique players")
        if not uniq:
            lines.append("")
            lines.append("_none_")
            lines.append("")
            continue
        lines.append("")
        lines.append("| ADP rank | Name | Pos | events (see JSON) |")
        lines.append("| ---: | --- | --- | --- |")
        counts = Counter(
            h["player_id"] for h in d["strategy_unmapped_events"][strat]
        )
        for u in uniq:
            lines.append(
                f"| {u.get('adp_rank')} | {u.get('name')} | {u.get('position')} | "
                f"{counts[u['player_id']]} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Board-wide unmapped picks (secondary)",
            "",
            f"- board pick-events with unmapped/no-gsis: {d['board_unmapped_pick_events']}",
            f"- unique players: {len(d['board_unmapped_unique'])}",
            "",
            f"**Next:** {report['next']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="P2.2C decision-space coverage (no PPR attach)"
    )
    parser.add_argument("--raw-json", type=Path, default=None)
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--draft-db", type=Path, default=None)
    parser.add_argument("--slots", type=str, default="1,5,10")
    parser.add_argument("--n-sims", type=int, default=3)
    parser.add_argument("--seed0", type=int, default=42)
    parser.add_argument(
        "--rematerialize",
        action="store_true",
        help="Rebuild draft/eval snapshot before reporting",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_decision_space_coverage.md"),
    )
    args = parser.parse_args()
    report = build_report(
        raw_json=args.raw_json,
        eval_db=args.eval_db,
        draft_db=args.draft_db,
        slots=parse_slots(args.slots),
        n_sims=args.n_sims,
        seed0=args.seed0,
        rematerialize=args.rematerialize,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
