"""Smoke: D vs Branch B — M_D identical; M_B = M_D + C."""

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
        user_name="V3BB-smoke",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    _advance_to_user(conn, draft_id, seed)
    d = get_strategy("adp_v3a").recommend(conn, draft_id, n=n)
    b = get_strategy("adp_v3bb").recommend(conn, draft_id, n=n)

    d_full = get_strategy("adp_v3a").recommend(conn, draft_id, n=10_000)
    b_full = get_strategy("adp_v3bb").recommend(conn, draft_id, n=10_000)
    b_by_id = {str(x["player_id"]): x for x in b_full}

    md_match = True
    formula_ok = True
    for item in d_full:
        pid = str(item["player_id"])
        br = b_by_id.get(pid)
        if br is None:
            md_match = False
            continue
        if abs(float(br["marginal_d"]) - float(item["marginal"])) > 1e-6:
            md_match = False
        expected = round(float(br["marginal_d"]) + float(br["continuation"]), 2)
        if abs(float(br["marginal_b"]) - expected) > 1e-6:
            formula_ok = False

    return {
        "slot": slot,
        "seed": seed,
        "draft_id": draft_id,
        "md_identical_across_d_and_b": md_match,
        "mb_equals_md_plus_c": formula_ok,
        "d_top1": d[0]["name"] if d else None,
        "b_top1": b[0]["name"] if b else None,
        "order_changed": (d[0]["player_id"] != b[0]["player_id"]) if d and b else None,
        "b_top": [
            {
                "name": x["name"],
                "pos": x["position"],
                "marginal_d": x.get("marginal_d"),
                "continuation": x.get("continuation"),
                "marginal_b": x.get("marginal_b"),
            }
            for x in b
        ],
        "n_d": len(d_full),
        "n_b": len(b_full),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-B Branch B smoke")
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument("--out", type=Path, default=Path("results/phase2_v3bb_smoke.md"))
    args = parser.parse_args()
    conn = live_db.connect(args.draft_db)
    live_db.init(conn)
    cases = [smoke_one(conn, slot=1, seed=42), smoke_one(conn, slot=8, seed=44)]
    conn.close()
    ok = all(
        c["md_identical_across_d_and_b"] and c["mb_equals_md_plus_c"] for c in cases
    )
    report = {
        "stage": "V3BB_smoke",
        "created_at": _utcnow(),
        "ok": ok,
        "cases": cases,
        "note": "Smoke: M_D reuse and M_B=M_D+C. Gates P/N are unit tests.",
    }
    lines = [
        "# V3-B Branch B smoke (D vs B)",
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
                f"- M_D identical: `{c['md_identical_across_d_and_b']}`",
                f"- M_B = M_D + C: `{c['mb_equals_md_plus_c']}`",
                f"- D top1: {c['d_top1']}",
                f"- B top1: {c['b_top1']}",
                f"- order changed: `{c['order_changed']}`",
                "",
            ]
        )
        for row in c["b_top"]:
            lines.append(
                f"- {row['name']} ({row['pos']}): "
                f"M_D={row['marginal_d']} C={row['continuation']} M_B={row['marginal_b']}"
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
