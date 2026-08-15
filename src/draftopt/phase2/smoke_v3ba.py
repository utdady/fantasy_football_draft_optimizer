"""Smoke: D vs Branch A — M_D identical; delta = M_D(q*) only."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt import db as live_db
from draftopt.backtest import pick_rng
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import create_draft, is_user_turn, snapshot
from draftopt.phase2.materialize_p22c_v3a import P22C_V3A_DB_PATH
from draftopt.phase2.scoring_contract import N_ROUNDS, N_TEAMS, ROSTER_PRESET
from draftopt.strategies import get_strategy


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _advance_to_user(conn, draft_id: str, seed: int) -> None:
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            raise RuntimeError("complete before user turn")
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if is_user_turn(draft_row):
            return
        overall = int(draft_row["current_pick"])
        cpu_pick(conn, draft_id, rng=pick_rng(seed, overall), policy="noisy_adp")


def smoke_one(conn, *, slot: int, seed: int, n: int = 8) -> dict:
    draft_id = create_draft(
        conn,
        user_slot=slot,
        user_name="V3BA-smoke",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    _advance_to_user(conn, draft_id, seed)
    d = get_strategy("adp_v3a").recommend(conn, draft_id, n=n)
    a = get_strategy("adp_v3ba").recommend(conn, draft_id, n=n)

    d_full = get_strategy("adp_v3a").recommend(conn, draft_id, n=10_000)
    a_full = get_strategy("adp_v3ba").recommend(conn, draft_id, n=10_000)
    a_by_id = {str(x["player_id"]): x for x in a_full}

    md_match = True
    formula_ok = True
    for item in d_full:
        pid = str(item["player_id"])
        ar = a_by_id.get(pid)
        if ar is None:
            md_match = False
            continue
        if abs(float(ar["marginal_d"]) - float(item["marginal"])) > 1e-9:
            md_match = False
        expected = round(float(ar["marginal_d"]) - float(ar["cross_alt_marginal"]), 2)
        if abs(float(ar["marginal_a"]) - expected) > 1e-9:
            formula_ok = False

    sample = a[0] if a else {}
    return {
        "slot": slot,
        "seed": seed,
        "draft_id": draft_id,
        "d_top": [
            {"name": x["name"], "pos": x["position"], "marginal": x["marginal"]}
            for x in d
        ],
        "a_top": [
            {
                "name": x["name"],
                "pos": x["position"],
                "marginal_d": x.get("marginal_d"),
                "cross_alt_marginal": x.get("cross_alt_marginal"),
                "cross_alt_missing": x.get("cross_alt_missing"),
                "cross_alt_pos": x.get("cross_alt_position"),
                "N_R": x.get("empty_capacity_positions"),
                "marginal_a": x.get("marginal_a"),
            }
            for x in a
        ],
        "n_d": len(d_full),
        "n_a": len(a_full),
        "md_identical_across_d_and_a": md_match,
        "ma_equals_md_minus_md_qstar": formula_ok,
        "d_top1": d[0]["name"] if d else None,
        "a_top1": a[0]["name"] if a else None,
        "sample_N_R": sample.get("empty_capacity_positions"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-B Branch A smoke D vs A")
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3ba_smoke.md"),
    )
    args = parser.parse_args()
    conn = live_db.connect(args.draft_db)
    live_db.init(conn)
    cases = [
        smoke_one(conn, slot=1, seed=42),
        smoke_one(conn, slot=8, seed=44),
    ]
    conn.close()
    ok = all(
        c["md_identical_across_d_and_a"] and c["ma_equals_md_minus_md_qstar"]
        for c in cases
    )
    report = {
        "stage": "V3BA_smoke",
        "created_at": _utcnow(),
        "ok": ok,
        "cases": cases,
        "note": (
            "Smoke only: verifies M_D reuse and M_A=M_D(p)−M_D(q*). Not the A−D ladder."
        ),
    }
    lines = [
        "# V3-B Branch A smoke (D vs A decision-time)",
        "",
        f"- ok: **{ok}**",
        f"- created: `{report['created_at']}`",
        "",
        report["note"],
        "",
    ]
    for c in cases:
        lines.extend(
            [
                f"## Slot {c['slot']} seed {c['seed']}",
                "",
                f"- M_D identical: `{c['md_identical_across_d_and_a']}`",
                f"- M_A = M_D − M_D(q*): `{c['ma_equals_md_minus_md_qstar']}`",
                f"- D top1: {c['d_top1']}",
                f"- A top1: {c['a_top1']}",
                f"- sample N(R): {c['sample_N_R']}",
                f"- pool n: D={c['n_d']} A={c['n_a']}",
                "",
                "A top:",
                "",
            ]
        )
        for row in c["a_top"]:
            lines.append(
                f"- {row['name']} ({row['pos']}): "
                f"M_D={row['marginal_d']} M_D(q*)={row['cross_alt_marginal']} "
                f"alt_pos={row['cross_alt_pos']} missing={row['cross_alt_missing']} "
                f"M_A={row['marginal_a']}"
            )
        lines.append("")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n".join(lines))
    print(f"Wrote {args.out}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
