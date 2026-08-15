"""Smoke: D vs B.1 on 1–2 frozen boards — M_D identical; delta = a* only."""

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
        user_name="V3B1-smoke",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    _advance_to_user(conn, draft_id, seed)
    d = get_strategy("adp_v3a").recommend(conn, draft_id, n=n)
    b1 = get_strategy("adp_v3b1").recommend(conn, draft_id, n=n)

    d_full = get_strategy("adp_v3a").recommend(conn, draft_id, n=10_000)
    b1_full = get_strategy("adp_v3b1").recommend(conn, draft_id, n=10_000)
    b1_by_id = {str(x["player_id"]): x for x in b1_full}

    md_match = True
    formula_ok = True
    for item in d_full:
        pid = str(item["player_id"])
        br = b1_by_id.get(pid)
        if br is None:
            md_match = False
            continue
        if abs(float(br["marginal_d"]) - float(item["marginal"])) > 1e-9:
            md_match = False
        expected = round(float(br["marginal_d"]) - float(br["cross_alt"]), 2)
        if abs(float(br["marginal_b1"]) - expected) > 1e-9:
            formula_ok = False

    sample = b1[0] if b1 else {}
    return {
        "slot": slot,
        "seed": seed,
        "draft_id": draft_id,
        "d_top": [
            {"name": x["name"], "pos": x["position"], "marginal": x["marginal"]}
            for x in d
        ],
        "b1_top": [
            {
                "name": x["name"],
                "pos": x["position"],
                "marginal_d": x.get("marginal_d"),
                "cross_alt": x.get("cross_alt"),
                "cross_alt_missing": x.get("cross_alt_missing"),
                "cross_alt_pos": x.get("cross_alt_position"),
                "N_R": x.get("empty_capacity_positions"),
                "marginal_b1": x.get("marginal_b1"),
            }
            for x in b1
        ],
        "n_d": len(d_full),
        "n_b1": len(b1_full),
        "md_identical_across_d_and_b1": md_match,
        "mb1_equals_md_minus_a": formula_ok,
        "d_top1": d[0]["name"] if d else None,
        "b1_top1": b1[0]["name"] if b1 else None,
        "sample_N_R": sample.get("empty_capacity_positions"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-B.1 smoke D vs B.1")
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3b1_smoke.md"),
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
        c["md_identical_across_d_and_b1"] and c["mb1_equals_md_minus_a"] for c in cases
    )
    report = {
        "stage": "V3B1_smoke",
        "created_at": _utcnow(),
        "ok": ok,
        "cases": cases,
        "note": (
            "Smoke only: verifies M_D reuse and M_B1=M_D−a*. Not the B.1−D ladder."
        ),
    }
    lines = [
        "# V3-B.1 smoke (D vs B.1 decision-time)",
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
                f"- M_D identical: `{c['md_identical_across_d_and_b1']}`",
                f"- M_B1 = M_D − a*: `{c['mb1_equals_md_minus_a']}`",
                f"- D top1: {c['d_top1']}",
                f"- B.1 top1: {c['b1_top1']}",
                f"- sample N(R): {c['sample_N_R']}",
                f"- pool n: D={c['n_d']} B.1={c['n_b1']}",
                "",
                "B.1 top:",
                "",
            ]
        )
        for row in c["b1_top"]:
            lines.append(
                f"- {row['name']} ({row['pos']}): "
                f"M_D={row['marginal_d']} a*={row['cross_alt']} "
                f"alt_pos={row['cross_alt_pos']} missing={row['cross_alt_missing']} "
                f"M_B1={row['marginal_b1']}"
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
