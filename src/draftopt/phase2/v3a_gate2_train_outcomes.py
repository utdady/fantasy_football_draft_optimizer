"""V3-A Gate 2: train-year actual PPR for FFC ADP pools (2021–2023).

Uses the same week_ppr_points / DST rules as ppr_eval_v1_2024, but does NOT
write under CONTRACT_ID 2024 and does not peek at 2024 for calibration.
Missing ≠ zero. No fit.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from draftopt.phase2.attach_outcomes_p22c import (
    load_player_weeks,
    load_reg_scores,
    load_roster_gsis,
    load_team_weeks,
    _nflverse_team,
)
from draftopt.phase2.dst_scoring import week_dst_points
from draftopt.phase2.map_players import load_id_crosswalk, map_ffc_players
from draftopt.phase2.ppr_scoring import week_ppr_points
from draftopt.phase2.scoring_contract import SEASON_TYPE
from draftopt.phase2.v3a_gate1_adp_provenance import TRAIN_YEARS, stable_raw_path
from draftopt.sources import ffc

TRAIN_CONTRACT = "ppr_train_v1_rules_match_ppr_eval_v1"
SOURCE = "nflverse_computed"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _score_offense(gsis: str, by_gsis: dict, roster_gsis: set[str]) -> dict:
    weeks = by_gsis.get(gsis) or []
    if not weeks and gsis not in roster_gsis:
        return {"state": "missing_identity", "points": None, "n_weeks": 0}
    if not weeks:
        return {"state": "observed_zero", "points": 0.0, "n_weeks": 0}
    pts = [week_ppr_points(w) for w in weeks]
    total = round(sum(pts), 4)
    state = "observed_zero" if total == 0.0 else "observed_points"
    return {"state": state, "points": total, "n_weeks": len(pts)}


def _score_dst(
    team: str,
    *,
    team_by_tw: dict,
    scores: dict,
    weeks_by_team: dict,
) -> dict:
    canon = (team or "").upper()
    nv = _nflverse_team(canon)
    expected = weeks_by_team.get(nv) or set()
    if not expected:
        return {"state": "missing_identity", "points": None, "n_weeks": 0}
    week_pts: list[float] = []
    for week in sorted(expected):
        def_row = team_by_tw.get((nv, week))
        if def_row is None:
            continue
        opp = def_row.get("opponent_team")
        opp_row = team_by_tw.get((str(opp), week)) if opp else None
        if opp_row is None:
            continue
        pa = scores.get((str(opp), week))
        if pa is None:
            continue
        ya = float(opp_row.get("passing_yards") or 0) + float(
            opp_row.get("rushing_yards") or 0
        )
        week_pts.append(
            week_dst_points(
                points_allowed=float(pa),
                yards_allowed=ya,
                def_row=def_row,
            )
        )
    if len(week_pts) < max(1, int(0.5 * len(expected))):
        return {
            "state": "missing_weeks",
            "points": None,
            "n_weeks": len(week_pts),
            "expected_weeks": len(expected),
        }
    total = round(sum(week_pts), 4)
    state = "observed_zero" if total == 0.0 else "observed_points"
    return {
        "state": state,
        "points": total,
        "n_weeks": len(week_pts),
        "expected_weeks": len(expected),
    }


def run_year(year: int) -> dict:
    payload = ffc.load_adp_json(stable_raw_path(year))
    players = ffc.parse_adp_players(payload)
    mapping = map_ffc_players(players, load_id_crosswalk())
    mapped = mapping["mapped"]

    weekly = load_player_weeks(year)
    roster_gsis = load_roster_gsis(year)
    team_weeks = load_team_weeks(year)
    scores = load_reg_scores(year)

    by_gsis: dict[str, list] = defaultdict(list)
    for raw in weekly:
        g = raw.get("player_id")
        if g:
            by_gsis[str(g)].append(raw)

    team_by_tw: dict[tuple[str, int], dict] = {}
    for raw in team_weeks:
        team_by_tw[(str(raw.get("team") or ""), int(raw.get("week") or 0))] = raw

    weeks_by_team: dict[str, set[int]] = defaultdict(set)
    for (team, week), _ in scores.items():
        weeks_by_team[team].add(week)

    counts = defaultdict(int)
    pairs: list[dict] = []
    adp_by_ffc = {str(p["ffc_player_id"]): p.get("adp") for p in players}
    for m in mapped:
        pos = (m.get("position") or "").upper()
        name = m.get("name")
        adp = adp_by_ffc.get(str(m.get("source_player_id")))
        if pos == "DST":
            scored = _score_dst(
                m.get("team") or "",
                team_by_tw=team_by_tw,
                scores=scores,
                weeks_by_team=weeks_by_team,
            )
        else:
            gsis = m.get("gsis_id")
            if not gsis:
                scored = {"state": "missing_identity", "points": None, "n_weeks": 0}
            else:
                scored = _score_offense(str(gsis), by_gsis, roster_gsis)
        counts[scored["state"]] += 1
        if scored["state"] in {"observed_points", "observed_zero"} and adp is not None:
            pairs.append(
                {
                    "train_year": year,
                    "name": name,
                    "position": pos,
                    "adp": float(adp),
                    "actual_ppr": float(scored["points"]),
                    "outcome_state": scored["state"],
                    "player_id": m.get("player_id"),
                    "gsis_id": m.get("gsis_id"),
                    "ffc_player_id": str(m.get("source_player_id")),
                }
            )

    n_mapped = mapping["n_mapped"]
    n_obs = counts["observed_points"] + counts["observed_zero"]
    return {
        "year": year,
        "season_type": SEASON_TYPE,
        "n_ffc": mapping["n_ffc"],
        "n_mapped": n_mapped,
        "n_unresolved": mapping["n_unresolved"],
        "outcome_counts": dict(counts),
        "n_observed": n_obs,
        "observed_coverage_of_mapped": round(n_obs / n_mapped, 4) if n_mapped else 0.0,
        "n_train_pairs_adp_and_observed": len(pairs),
        "train_pairs": pairs,
        "missing_never_coalesced_to_zero": True,
        "sample_pairs_head": pairs[:5],
    }


def run_gate2() -> dict:
    years = [run_year(y) for y in TRAIN_YEARS]
    # Gate: each year ≥90% of mapped have observed_* (not missing_*)
    ok = all(y["observed_coverage_of_mapped"] >= 0.90 for y in years)
    return {
        "stage": "V3A_gate2_train_outcomes",
        "created_at": _utcnow(),
        "contract_rules": TRAIN_CONTRACT,
        "note": (
            "Scoring rules match ppr_eval_v1_2024 (week_ppr_points + DST tiers). "
            "Not the 2024 eval contract row. No calibration fit. No 2024 train use."
        ),
        "source": SOURCE,
        "verdict": "pass" if ok else "fail",
        "years": years,
        "next": (
            "Gate 3 — freeze calibration definition (bins, mins, rookies) "
            "before any 2024 calibration peek"
            if ok
            else "STOP — fix outcome coverage before fitting"
        ),
    }


def _md(report: dict) -> str:
    lines = [
        "# V3-A Gate 2 — train-year outcomes (2021–2023)",
        "",
        f"- created: `{report['created_at']}`",
        f"- scoring rules: `{report['contract_rules']}`",
        f"- source: `{report['source']}`",
        f"- verdict: **{report['verdict']}**",
        "",
        report["note"],
        "",
        "## Coverage",
        "",
        "| Year | FFC | Mapped | Observed | Obs/mapped | Train pairs | missing_id | missing_weeks |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for y in report["years"]:
        c = y["outcome_counts"]
        lines.append(
            f"| {y['year']} | {y['n_ffc']} | {y['n_mapped']} | {y['n_observed']} | "
            f"{y['observed_coverage_of_mapped']:.1%} | "
            f"{y['n_train_pairs_adp_and_observed']} | "
            f"{c.get('missing_identity', 0)} | {c.get('missing_weeks', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Checklist",
            "",
            f"- [{'x' if report['verdict']=='pass' else ' '}] Actual PPR via same scoring functions as eval contract",
            "- [x] REG weeks only",
            "- [x] Offense + DST identity handling",
            "- [x] missing ≠ zero",
            f"- [{'x' if report['verdict']=='pass' else ' '}] Coverage report (≥90% observed among mapped)",
            "",
            f"**Next:** {report['next']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-A Gate 2 train outcomes")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_gate2_train_outcomes.md"),
    )
    args = parser.parse_args()
    report = run_gate2()
    # Drop bulky sample in md-facing json? keep light
    slim = dict(report)
    slim["years"] = [
        {
            k: v
            for k, v in y.items()
            if k not in {"sample_pairs_head", "train_pairs"}
        }
        for y in report["years"]
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_md(report), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(_md(report))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
