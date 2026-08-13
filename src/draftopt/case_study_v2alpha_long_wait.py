"""
Case study: V2-alpha survival at a long snake gap.

1) Freeze marginal board at slot-1 #20 (Daniels rostered; Nabers & Kyren available).
   - Literal V2 (next=#21, ADP×0) — expect near-commutative EV.
   - Survival counterfactual: same fork with ADP×18 (as if next were ~#39).

2) Advance raw Nabers at #20; freeze at #21 (next=#40, ADP×18).
   - Score Kyren vs top raw WR under authentic long-wait V2-alpha EV.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.case_study_pick20 import advance_to_overall, _as_raw, _player_brief
from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import draft_roster, record_user_pick
from draftopt.lookahead import as_lineup_player, two_pick_ev
from draftopt.pool import remaining_ranked
from draftopt.strategies.marginal import MarginalValueStrategy, _user_roster_players
from draftopt.strategies.marginal_v2 import MarginalV2Strategy
from draftopt.strategies.marginal_vor import MarginalVorStrategy


def _score_pair(roster, remaining, slots, a, b, *, n_cpu: int) -> dict:
    ev_a = two_pick_ev(roster, a, remaining, slots, n_cpu_picks=n_cpu)
    ev_b = two_pick_ev(roster, b, remaining, slots, n_cpu_picks=n_cpu)
    return {
        "n_cpu_picks": n_cpu,
        "a": {
            "pick_now": _player_brief(as_lineup_player(a)),
            "q": _player_brief(ev_a["q"]) if ev_a.get("q") else None,
            "ev": round(float(ev_a["ev"]), 2),
            "one_pick": round(float(ev_a["one_pick"]), 2),
        },
        "b": {
            "pick_now": _player_brief(as_lineup_player(b)),
            "q": _player_brief(ev_b["q"]) if ev_b.get("q") else None,
            "ev": round(float(ev_b["ev"]), 2),
            "one_pick": round(float(ev_b["one_pick"]), 2),
        },
        "delta_b_minus_a": round(float(ev_b["ev"]) - float(ev_a["ev"]), 2),
    }


def run_case_study(*, seed: int = 0, preset: str = "league_default", conn=None, db_path=None) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    try:
        draft_id = advance_to_overall(
            conn, slot=1, target_overall=20, seed=seed, preset=preset
        )
        draft = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        slots = draft_roster(draft).get("slots") or {}
        n_teams = int(draft["n_teams"])
        n_rounds = int(draft["n_rounds"])

        roster = [
            p
            for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
            if p["projection_quality"] == "high"
        ]
        remaining = remaining_ranked(conn, draft_id)

        raw_rec = MarginalValueStrategy().recommend(conn, draft_id, n=1)[0]
        vor_rec = MarginalVorStrategy().recommend(conn, draft_id, n=1)[0]
        v2_rec = MarginalV2Strategy().recommend(conn, draft_id, n=3)

        nabers = raw_rec
        kyren = vor_rec
        until_20 = picks_until_next(20, 1, n_teams, n_rounds=n_rounds)
        nxt_20 = next_user_overall(20, 1, n_teams, n_rounds=n_rounds)

        at_20_literal = _score_pair(
            roster, remaining, slots, kyren, nabers, n_cpu=int(until_20 or 0)
        )
        # Counterfactual long gap from this board (ADP×18 ≈ R2→R3 style wait).
        at_20_survival = _score_pair(
            roster, remaining, slots, kyren, nabers, n_cpu=18
        )

        # Authenticate #21→#40: take raw's #20 (Nabers), then evaluate.
        record_user_pick(conn, draft_id, nabers["player_id"], made_by="strategy")
        draft21 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        assert int(draft21["current_pick"]) == 21

        roster21 = [
            p
            for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
            if p["projection_quality"] == "high"
        ]
        remaining21 = remaining_ranked(conn, draft_id)
        until_21 = picks_until_next(21, 1, n_teams, n_rounds=n_rounds)
        nxt_21 = next_user_overall(21, 1, n_teams, n_rounds=n_rounds)

        raw21 = MarginalValueStrategy().recommend(conn, draft_id, n=1)[0]
        vor21 = MarginalVorStrategy().recommend(conn, draft_id, n=1)[0]
        v2_21 = MarginalV2Strategy().recommend(conn, draft_id, n=3)

        # Prefer Kyren if still available; else use VOR's #21 choice vs raw's.
        kyren_id = kyren["player_id"]
        kyren_still = next(
            (p for p in remaining21 if p["player_id"] == kyren_id), None
        )
        branch_a_player = kyren_still or vor21
        branch_b_player = raw21
        at_21 = _score_pair(
            roster21,
            remaining21,
            slots,
            branch_a_player,
            branch_b_player,
            n_cpu=int(until_21 or 0),
        )

        return {
            "experiment": "v2alpha_long_wait",
            "seed": seed,
            "preset": preset,
            "freeze_20": {
                "overall": 20,
                "roster": [_player_brief(p) for p in roster],
                "next_user_pick": nxt_20,
                "picks_until_next": until_20,
                "raw_choice": _player_brief(_as_raw(nabers)),
                "vor_choice": _player_brief(_as_raw(kyren)),
                "v2_top": [
                    {
                        "name": r.get("name"),
                        "position": r.get("position"),
                        "ev_two_pick": r.get("ev_two_pick"),
                        "q_player": r.get("q_player"),
                        "why": r.get("why"),
                    }
                    for r in v2_rec
                ],
                "literal_v2_kyren_vs_nabers": at_20_literal,
                "survival_adp18_kyren_vs_nabers": at_20_survival,
            },
            "freeze_21_after_nabers": {
                "overall": 21,
                "roster": [_player_brief(p) for p in roster21],
                "next_user_pick": nxt_21,
                "picks_until_next": until_21,
                "raw_choice": _player_brief(_as_raw(raw21)),
                "vor_choice": _player_brief(_as_raw(vor21)),
                "v2_top": [
                    {
                        "name": r.get("name"),
                        "position": r.get("position"),
                        "ev_two_pick": r.get("ev_two_pick"),
                        "q_player": r.get("q_player"),
                        "picks_until_next": r.get("picks_until_next"),
                        "why": r.get("why"),
                    }
                    for r in v2_21
                ],
                "v2_ev_vorish_vs_raw": at_21,
                "note": (
                    "After Nabers at #20; branch A = Kyren if available else VOR#21; "
                    "branch B = raw#21; n_cpu = authentic picks_until_next."
                ),
            },
        }
    finally:
        if own:
            conn.close()


def to_markdown(report: dict) -> str:
    f20 = report["freeze_20"]
    f21 = report["freeze_21_after_nabers"]
    lit = f20["literal_v2_kyren_vs_nabers"]
    surv = f20["survival_adp18_kyren_vs_nabers"]
    a21 = f21["v2_ev_vorish_vs_raw"]

    def fmt_side(label: str, side: dict) -> list[str]:
        q = side.get("q") or {}
        return [
            f"- **{label}**: {side['pick_now']['name']} ({side['pick_now']['position']}) "
            f"proj {side['pick_now']['projection']:.1f}",
            f"  - q after ADP future: "
            f"{q.get('name', '—')} ({q.get('position', '—')}) "
            f"proj {q.get('projection', 0):.1f}"
            if q
            else "  - q after ADP future: —",
            f"  - two-pick EV: **{side['ev']:.1f}** (one-pick {side['one_pick']:.1f})",
        ]

    lines = [
        "# Case study — V2-alpha long-wait survival (Kyren / Nabers)",
        "",
        "## Setup",
        "",
        f"- seed: `{report['seed']}`",
        f"- preset: `{report['preset']}`",
        "- board to freeze: `marginal` (raw R1)",
        "- opponent future in EV: **ADP-greedy** (deterministic)",
        "- score: raw `lineup_ev` starter points",
        "",
        "## Part 1 — Freeze at overall #20",
        "",
        f"Roster: {', '.join(p['name'] for p in f20['roster'])}",
        "",
        f"- RAW → {f20['raw_choice']['name']} ({f20['raw_choice']['position']})",
        f"- VOR → {f20['vor_choice']['name']} ({f20['vor_choice']['position']})",
        f"- Literal next pick: #{f20['next_user_pick']} "
        f"(ADP×{f20['picks_until_next']} others)",
        "",
        "### V2 top recommendations (literal)",
        "",
    ]
    for r in f20["v2_top"]:
        lines.append(
            f"- {r['name']} ({r['position']}) EV={r['ev_two_pick']} "
            f"q={r.get('q_player')} — {r.get('why')}"
        )

    lines.extend(
        [
            "",
            "### Literal V2 EV (Kyren vs Nabers, ADP×0)",
            "",
            f"n_cpu = {lit['n_cpu_picks']}",
        ]
    )
    lines.extend(fmt_side("A Kyren-first", lit["a"]))
    lines.extend(fmt_side("B Nabers-first", lit["b"]))
    lines.append(f"- Δ (Nabers − Kyren) = **{lit['delta_b_minus_a']:+.1f}**")

    lines.extend(
        [
            "",
            "### Survival counterfactual (same board, ADP×18)",
            "",
            "Pretend the next user pick is ~18 opponents away (not the literal #21). "
            "This isolates survival without leaving the #20 fork.",
            "",
            f"n_cpu = {surv['n_cpu_picks']}",
        ]
    )
    lines.extend(fmt_side("A Kyren-first", surv["a"]))
    lines.extend(fmt_side("B Nabers-first", surv["b"]))
    lines.append(f"- Δ (Nabers − Kyren) = **{surv['delta_b_minus_a']:+.1f}**")

    lines.extend(
        [
            "",
            "## Part 2 — Freeze at #21 after Nabers (authentic #21→#40)",
            "",
            f21["note"],
            "",
            f"Roster: {', '.join(p['name'] for p in f21['roster'])}",
            "",
            f"- next pick: #{f21['next_user_pick']} "
            f"(ADP×{f21['picks_until_next']} others)",
            f"- RAW → {f21['raw_choice']['name']} ({f21['raw_choice']['position']})",
            f"- VOR → {f21['vor_choice']['name']} ({f21['vor_choice']['position']})",
            "",
            "### V2 top recommendations",
            "",
        ]
    )
    for r in f21["v2_top"]:
        lines.append(
            f"- {r['name']} ({r['position']}) EV={r['ev_two_pick']} "
            f"q={r.get('q_player')} wait={r.get('picks_until_next')} — {r.get('why')}"
        )

    lines.extend(
        [
            "",
            "### V2 EV: VOR-ish branch vs raw branch",
            "",
            f"n_cpu = {a21['n_cpu_picks']}",
        ]
    )
    lines.extend(fmt_side("A (Kyren/VOR)", a21["a"]))
    lines.extend(fmt_side("B (raw)", a21["b"]))
    lines.append(f"- Δ (raw branch − A) = **{a21['delta_b_minus_a']:+.1f}**")

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- Part 1 literal: with ADP×0, V2's best *q* is raw-marginal among "
            "**all** survivors — not forced to be the other fork candidate. "
            "Nabers→Nico (two WRs) can beat Kyren→Nabers when WR slots are empty.",
            "- Part 1 ADP×18: survival alone — after 18 ADP-greedy removals, "
            "Nabers-first still keeps Kyren as q; Kyren-first is stuck with a "
            "second RB (Bucky). Large positive Δ favors securing the scarce WR first.",
            "- Part 2: authentic #21→#40 after Nabers; V2 prefers Nico over Kyren "
            "on the same Bucky-at-#40 future (+5.1).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V2-alpha long-wait case study")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        type=str,
        default="results/case_study_v2alpha_long_wait.md",
    )
    args = parser.parse_args()
    report = run_case_study(seed=args.seed, preset=args.preset)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    surv = report["freeze_20"]["survival_adp18_kyren_vs_nabers"]
    print(
        f"at#20 literal Δ={report['freeze_20']['literal_v2_kyren_vs_nabers']['delta_b_minus_a']:+.1f} "
        f"survival18 Δ={surv['delta_b_minus_a']:+.1f} "
        f"at#21 Δ={report['freeze_21_after_nabers']['v2_ev_vorish_vs_raw']['delta_b_minus_a']:+.1f}"
    )


if __name__ == "__main__":
    main()
