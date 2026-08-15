"""Smoke: D vs E on 1–2 frozen boards — M_D identical; delta = r* only."""

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
        user_name="V3B-smoke",
        roster_preset=ROSTER_PRESET,
        n_rounds=N_ROUNDS,
        n_teams=N_TEAMS,
    )
    _advance_to_user(conn, draft_id, seed)
    d = get_strategy("adp_v3a").recommend(conn, draft_id, n=n)
    e = get_strategy("adp_v3b").recommend(conn, draft_id, n=n)

    # Full M_D maps for equality check
    d_full = get_strategy("adp_v3a").recommend(conn, draft_id, n=10_000)
    e_full = get_strategy("adp_v3b").recommend(conn, draft_id, n=10_000)
    e_by_id = {str(x["player_id"]): x for x in e_full}

    md_match = True
    me_formula_ok = True
    for item in d_full:
        pid = str(item["player_id"])
        er = e_by_id.get(pid)
        if er is None:
            md_match = False
            continue
        if abs(float(er["marginal_d"]) - float(item["marginal"])) > 1e-9:
            md_match = False
        expected = round(float(er["marginal_d"]) - float(er["replacement"]), 2)
        if abs(float(er["marginal_e"]) - expected) > 1e-9:
            me_formula_ok = False

    return {
        "slot": slot,
        "seed": seed,
        "draft_id": draft_id,
        "d_top": [
            {"name": x["name"], "pos": x["position"], "marginal": x["marginal"]}
            for x in d
        ],
        "e_top": [
            {
                "name": x["name"],
                "pos": x["position"],
                "marginal_d": x.get("marginal_d"),
                "replacement": x.get("replacement"),
                "replacement_missing": x.get("replacement_missing"),
                "marginal_e": x.get("marginal_e"),
            }
            for x in e
        ],
        "n_d": len(d_full),
        "n_e": len(e_full),
        "md_identical_across_d_and_e": md_match,
        "me_equals_md_minus_r": me_formula_ok,
        "d_top1": d[0]["name"] if d else None,
        "e_top1": e[0]["name"] if e else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-B smoke D vs E")
    parser.add_argument("--draft-db", type=Path, default=P22C_V3A_DB_PATH)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3b_smoke.md"),
    )
    args = parser.parse_args()
    conn = live_db.connect(args.draft_db)
    live_db.init(conn)
    cases = [
        smoke_one(conn, slot=1, seed=42),
        smoke_one(conn, slot=8, seed=44),
    ]
    conn.close()
    ok = all(c["md_identical_across_d_and_e"] and c["me_equals_md_minus_r"] for c in cases)
    report = {
        "stage": "V3B_smoke",
        "created_at": _utcnow(),
        "ok": ok,
        "cases": cases,
        "note": (
            "Smoke only: verifies M_D reuse and M_E=M_D−r*. Not the E−D ladder."
        ),
    }
    lines = [
        "# V3-B smoke (D vs E decision-time)",
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
                f"- M_D identical: `{c['md_identical_across_d_and_e']}`",
                f"- M_E = M_D − r*: `{c['me_equals_md_minus_r']}`",
                f"- D top1: {c['d_top1']}",
                f"- E top1: {c['e_top1']}",
                f"- pool n: D={c['n_d']} E={c['n_e']}",
                "",
                "E top:",
                "",
            ]
        )
        for row in c["e_top"]:
            lines.append(
                f"- {row['name']} ({row['pos']}): "
                f"M_D={row['marginal_d']} r*={row['replacement']} "
                f"missing={row['replacement_missing']} M_E={row['marginal_e']}"
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
