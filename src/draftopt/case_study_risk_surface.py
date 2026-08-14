"""
Risk/EV surface diagnostic from existing three-scenario two-pick EVs.

No new overnight sims. For each candidate on a frozen board:
  mean  = (EV_ADP + EV_proj + EV_VOR) / 3
  floor = min_f EV
  downside = mean - floor
  regret(p,f) = max_a EV(a|f) - EV(p|f)
  max_regret = max_f regret(p,f)

Pareto on (mean, floor): A dominates B if mean_A >= mean_B and floor_A >= floor_B
with at least one strict.

Purpose: decide whether the next issue is objective (A), scenario-set (B), or both —
before inventing λ / CVaR / β3.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.case_study_robust_min import FUTURES, score_candidates
from draftopt.case_study_survival_r1 import _advance_chase_then_cpu, _find_by_name
from draftopt.draft.snake import picks_until_next
from draftopt.draft.state import create_draft, draft_roster
from draftopt.lookahead import as_lineup_player
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies.marginal import _user_roster_players


def enrich_risk_metrics(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    key_map = {
        "adp_greedy": "ev_adp",
        "proj_greedy": "ev_proj",
        "vor": "ev_vor",
    }
    best_f = {pol: max(r[key_map[pol]] for r in rows) for pol in FUTURES}

    out = []
    for r in rows:
        evs = [r["ev_adp"], r["ev_proj"], r["ev_vor"]]
        mean = round(sum(evs) / 3.0, 2)
        floor = r["ev_min"]
        downside = round(mean - floor, 2)
        regrets = {
            pol: round(best_f[pol] - r[key_map[pol]], 2) for pol in FUTURES
        }
        max_regret = max(regrets.values())
        worst_regret_f = max(regrets, key=regrets.get)
        out.append(
            {
                **r,
                "mean_ev": mean,
                "floor_ev": floor,
                "downside": downside,
                "regret_by_future": regrets,
                "max_regret": max_regret,
                "worst_regret_future": worst_regret_f,
            }
        )
    return out


def pareto_frontier(rows: list[dict]) -> list[dict]:
    """Non-dominated on (mean_ev, floor_ev); higher is better for both."""
    frontier = []
    for a in rows:
        dominated = False
        for b in rows:
            if a["player_id"] == b["player_id"]:
                continue
            if (
                b["mean_ev"] >= a["mean_ev"]
                and b["floor_ev"] >= a["floor_ev"]
                and (
                    b["mean_ev"] > a["mean_ev"]
                    or b["floor_ev"] > a["floor_ev"]
                )
            ):
                dominated = True
                break
        if not dominated:
            frontier.append(a)
    frontier.sort(key=lambda r: (-r["mean_ev"], -r["floor_ev"], r.get("name") or ""))
    return frontier


def classify_classes(rows: list[dict]) -> dict:
    """Rough skill-vs-QB class summary for narrative."""
    skill = [r for r in rows if r["position"] in {"RB", "WR", "TE"}]
    qb = [r for r in rows if r["position"] == "QB"]

    def stats(group: list[dict]) -> dict | None:
        if not group:
            return None
        return {
            "n": len(group),
            "mean_of_means": round(sum(r["mean_ev"] for r in group) / len(group), 2),
            "mean_of_floors": round(sum(r["floor_ev"] for r in group) / len(group), 2),
            "mean_downside": round(sum(r["downside"] for r in group) / len(group), 2),
            "mean_max_regret": round(sum(r["max_regret"] for r in group) / len(group), 2),
        }

    return {"skill_RB_WR_TE": stats(skill), "QB": stats(qb)}


def analyze_board(
    *,
    label: str,
    why: str,
    roster: list[dict],
    remaining: list[dict],
    candidates: list[dict],
    slots: dict,
    n_cpu: int,
    n_teams: int,
    overall: int,
    top_n: int = 15,
) -> dict:
    raw = score_candidates(
        roster, remaining, candidates, slots, n_cpu=n_cpu, n_teams=n_teams
    )
    rows = enrich_risk_metrics(raw)
    frontier = pareto_frontier(rows)
    by_mean = sorted(rows, key=lambda r: (-r["mean_ev"], -r["floor_ev"], r.get("name") or ""))
    by_floor = sorted(rows, key=lambda r: (-r["floor_ev"], -r["mean_ev"], r.get("name") or ""))
    by_regret = sorted(rows, key=lambda r: (r["max_regret"], -r["mean_ev"], r.get("name") or ""))

    alpha = by_mean[0] if by_mean else None  # equal-weight mean ≈ mixture; α uses ADP
    alpha_adp = max(rows, key=lambda r: (r["ev_adp"], -(r.get("adp_espn") or 9999))) if rows else None
    robust = by_floor[0] if by_floor else None
    min_regret = by_regret[0] if by_regret else None

    return {
        "label": label,
        "why": why,
        "overall": overall,
        "n_cpu_picks": n_cpu,
        "n_scored": len(rows),
        "alpha_adp_pick": _brief_row(alpha_adp),
        "mean_pick": _brief_row(alpha),
        "floor_pick": _brief_row(robust),
        "min_max_regret_pick": _brief_row(min_regret),
        "class_summary": classify_classes(rows),
        "pareto_frontier": [_brief_row(r) for r in frontier],
        "pareto_size": len(frontier),
        "top_by_mean": [_brief_row(r) for r in by_mean[:top_n]],
        "top_by_floor": [_brief_row(r) for r in by_floor[:top_n]],
        "lowest_max_regret": [_brief_row(r) for r in by_regret[:top_n]],
        "spotlight": {
            r["name"]: _brief_row(r)
            for r in rows
            if r["name"]
            in {
                "Ja'Marr Chase",
                "Jayden Daniels",
                "Bijan Robinson",
                "Jahmyr Gibbs",
                "Saquon Barkley",
                "CeeDee Lamb",
                "Josh Allen",
                "Jalen Hurts",
                "Lamar Jackson",
                "Malik Nabers",
            }
        },
    }


def _brief_row(r: dict | None) -> dict | None:
    if r is None:
        return None
    return {
        "name": r["name"],
        "position": r["position"],
        "ev_adp": r["ev_adp"],
        "ev_proj": r["ev_proj"],
        "ev_vor": r["ev_vor"],
        "mean_ev": r["mean_ev"],
        "floor_ev": r["floor_ev"],
        "downside": r["downside"],
        "max_regret": r["max_regret"],
        "worst_regret_future": r["worst_regret_future"],
        "regret_by_future": r["regret_by_future"],
        "worst_future": r["worst_future"],
        "on_pareto": None,  # filled later if needed
    }


def _roster_from_draft(conn, draft_id: str) -> list[dict]:
    return [
        p
        for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
        if p["projection_quality"] == "high"
    ]


def run_diagnostic(
    *,
    seed: int = 0,
    preset: str = "league_default",
    conn=None,
    db_path=None,
    top_n: int = 15,
) -> dict:
    own = conn is None
    if conn is None:
        conn = db.connect(db_path) if db_path else db.connect()
        db.init(conn)
    if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
        if own:
            conn.close()
        raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")

    try:
        boards = []
        d1 = create_draft(
            conn, user_slot=1, user_name="risk-r1", roster_preset=preset
        )
        draft1 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d1,)
        ).fetchone()
        slots = draft_roster(draft1).get("slots") or {}
        n_teams = int(draft1["n_teams"])
        n_rounds = int(draft1["n_rounds"])
        overall1 = int(draft1["current_pick"])
        n_cpu1 = int(
            picks_until_next(overall1, 1, n_teams, n_rounds=n_rounds) or 0
        )
        rem1 = remaining_ranked(conn, d1)
        board_r1 = analyze_board(
            label="R1_slot1_empty",
            why="Frozen long-wait failure board (18 picks)",
            roster=[],
            remaining=rem1,
            candidates=candidate_pool(conn, d1),
            slots=slots,
            n_cpu=n_cpu1,
            n_teams=n_teams,
            overall=overall1,
            top_n=top_n,
        )
        # mark pareto membership on spotlight / top tables
        pareto_ids = {p["name"] for p in board_r1["pareto_frontier"]}
        for section in ("top_by_mean", "top_by_floor", "lowest_max_regret", "pareto_frontier"):
            for row in board_r1[section]:
                row["on_pareto"] = row["name"] in pareto_ids
        for row in board_r1["spotlight"].values():
            row["on_pareto"] = row["name"] in pareto_ids
        boards.append(board_r1)

        chase = _find_by_name(rem1, "Ja'Marr Chase")
        d20 = _advance_chase_then_cpu(
            conn,
            chase_id=chase["player_id"],
            n_cpu=n_cpu1,
            opponent_policy="proj_greedy",
            seed=seed,
            preset=preset,
        )
        draft20 = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (d20,)
        ).fetchone()
        overall20 = int(draft20["current_pick"])
        n_cpu20 = int(
            picks_until_next(overall20, 1, n_teams, n_rounds=n_rounds) or 0
        )
        board20 = analyze_board(
            label="O20_after_Chase_proj18",
            why="Wait-0 neighbor contrast (futures collapse when n_cpu=0)",
            roster=_roster_from_draft(conn, d20),
            remaining=remaining_ranked(conn, d20),
            candidates=candidate_pool(conn, d20),
            slots=slots,
            n_cpu=n_cpu20,
            n_teams=n_teams,
            overall=overall20,
            top_n=top_n,
        )
        pareto_ids20 = {p["name"] for p in board20["pareto_frontier"]}
        for section in ("top_by_mean", "top_by_floor", "lowest_max_regret", "pareto_frontier"):
            for row in board20[section]:
                row["on_pareto"] = row["name"] in pareto_ids20
        boards.append(board20)

        # Verdict from R1 frontier shape
        fr = board_r1["pareto_frontier"]
        fr_pos = sorted({p["position"] for p in fr})
        skill_on = any(p["position"] in {"RB", "WR", "TE"} for p in fr)
        qb_on = any(p["position"] == "QB" for p in fr)
        reading = []
        if skill_on and qb_on and len(fr) >= 2:
            reading.append(
                "R1 Pareto spans skill (high mean/fragile) and elite QB "
                "(lower mean/high floor) — risk preference is a real decision variable."
            )
            verdict_code = "A_frontier_exists"
        elif len(fr) == 1:
            reading.append(
                "Single Pareto point dominates — issue may be valuation more than risk."
            )
            verdict_code = "valuation_dominated"
        else:
            reading.append(
                f"Pareto size={len(fr)} positions={fr_pos}; inspect table."
            )
            verdict_code = "inspect"

        # Compare Chase vs Daniels max regret if present
        spot = board_r1["spotlight"]
        if "Ja'Marr Chase" in spot and "Jayden Daniels" in spot:
            c, d = spot["Ja'Marr Chase"], spot["Jayden Daniels"]
            reading.append(
                f"Chase: mean={c['mean_ev']} floor={c['floor_ev']} "
                f"downside={c['downside']} max_regret={c['max_regret']} "
                f"({c['worst_regret_future']})."
            )
            reading.append(
                f"Daniels: mean={d['mean_ev']} floor={d['floor_ev']} "
                f"downside={d['downside']} max_regret={d['max_regret']} "
                f"({d['worst_regret_future']})."
            )

        if board20["n_cpu_picks"] == 0:
            reading.append(
                "Wait-0 board: scenario EVs coincide (no intervening picks) — "
                "risk surface collapses; confirms uncertainty is board-evolution, "
                "not player-value uncertainty."
            )

        return {
            "futures": list(FUTURES),
            "note": (
                "Diagnostic only from three deterministic scenario EVs — not "
                "calibrated probabilities. No λ / CVaR / β3. UI stays marginal."
            ),
            "boards": boards,
            "verdict": {
                "code": verdict_code,
                "pareto_size_r1": len(fr),
                "pareto_positions_r1": fr_pos,
                "reading": reading,
                "next": (
                    "If frontier spans skill vs QB (A): risk-sensitive objective "
                    "is justified. Also ask whether proj_greedy scenario is too "
                    "extreme (B/C) before coding λ."
                ),
            },
        }
    finally:
        if own:
            conn.close()


def _table(rows: list[dict], lines: list[str]) -> None:
    lines.append(
        "| player | pos | ADP | proj | VOR | mean | floor | downside | "
        "max regret | worst regret f | Pareto? |"
    )
    lines.append(
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"
    )
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['position']} | {r['ev_adp']:.1f} | "
            f"{r['ev_proj']:.1f} | {r['ev_vor']:.1f} | {r['mean_ev']:.1f} | "
            f"{r['floor_ev']:.1f} | {r['downside']:.1f} | {r['max_regret']:.1f} | "
            f"{r['worst_regret_future']} | "
            f"{'yes' if r.get('on_pareto') else ''} |"
        )


def to_markdown(report: dict) -> str:
    lines = [
        "# Risk / EV surface + Pareto frontier",
        "",
        "## Purpose",
        "",
        report["note"],
        "",
        "Success: articulate *why* a rational pick sits between Chase upside and "
        "Daniels insurance — not invent λ that happens to.",
        "",
        f"Futures: `{', '.join(report['futures'])}`",
        "",
        "## Verdict",
        "",
        f"- code: **{report['verdict']['code']}**",
        f"- R1 Pareto size: **{report['verdict']['pareto_size_r1']}** "
        f"positions=`{report['verdict']['pareto_positions_r1']}`",
        "",
    ]
    for line in report["verdict"]["reading"]:
        lines.append(f"- {line}")
    lines.append("")
    lines.append(f"- next: {report['verdict']['next']}")
    lines.append("")

    for b in report["boards"]:
        lines.extend(
            [
                f"## {b['label']} (overall #{b['overall']}, wait {b['n_cpu_picks']})",
                "",
                f"_{b['why']}_",
                "",
                f"- scored: **{b['n_scored']}**",
                f"- α (max ADP EV): **{(b.get('alpha_adp_pick') or {}).get('name')}**",
                f"- max mean EV: **{(b.get('mean_pick') or {}).get('name')}**",
                f"- max floor: **{(b.get('floor_pick') or {}).get('name')}**",
                f"- min max-regret: **{(b.get('min_max_regret_pick') or {}).get('name')}**",
                f"- Pareto size: **{b['pareto_size']}**",
                "",
                "### Class summary",
                "",
            ]
        )
        for cls, st in (b.get("class_summary") or {}).items():
            if not st:
                continue
            lines.append(
                f"- `{cls}` n={st['n']}: mean_of_means={st['mean_of_means']}, "
                f"mean_of_floors={st['mean_of_floors']}, "
                f"mean_downside={st['mean_downside']}, "
                f"mean_max_regret={st['mean_max_regret']}"
            )
        lines.extend(["", "### Pareto frontier", ""])
        _table(b["pareto_frontier"], lines)
        lines.extend(["", "### Top by mean EV", ""])
        _table(b["top_by_mean"], lines)
        lines.extend(["", "### Top by floor", ""])
        _table(b["top_by_floor"], lines)
        lines.extend(["", "### Lowest max regret", ""])
        _table(b["lowest_max_regret"], lines)
        if b.get("spotlight"):
            lines.extend(["", "### Spotlight", ""])
            _table(list(b["spotlight"].values()), lines)
        lines.append("")

    lines.extend(
        [
            "## Reading",
            "",
            "- **A (objective):** frontier has both high-mean skill and high-floor QB "
            "→ risk preference is the missing dial (not another ranking hack).",
            "- **B (scenario set):** if only proj creates the skill cliff, ask whether "
            "proj_greedy is too extreme before coding λ.",
            "- **C (both):** most likely — need risk-sensitive objective *and* "
            "realistic board-evolution uncertainty.",
            "- Wait-0 boards collapsing scenarios confirms the uncertainty is "
            "**state transition** (who survives), not player valuation.",
            "- Do **not** implement Score = E[EV] − λR yet; freeze this surface first.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Risk/EV surface + Pareto frontier (three-scenario diagnostic)"
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument("--top-n", type=int, default=15)
    parser.add_argument(
        "--out",
        type=str,
        default="results/case_study_risk_ev_surface.md",
    )
    args = parser.parse_args()
    report = run_diagnostic(
        seed=args.seed, preset=args.preset, top_n=args.top_n
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"verdict={report['verdict']['code']} pareto_r1={report['verdict']['pareto_size_r1']}")
    for line in report["verdict"]["reading"]:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
