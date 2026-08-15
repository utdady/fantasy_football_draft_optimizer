"""P2.2 stage-A feasibility spike: FFC ADP + nflverse outcomes + ID map.

Never sets evaluable=1. No draft replay. No strategy comparison.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt.config import EVAL_DB_PATH
from draftopt.phase2 import connect_eval
from draftopt.phase2.map_players import (
    load_id_crosswalk,
    map_ffc_players,
    persist_mapping,
)
from draftopt.phase2.outcomes_nflverse import ingest_season_outcomes
from draftopt.phase2.schema import migrate_eval_schema
from draftopt.sources import ffc


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_ffc_payload(
    *,
    year: int,
    teams: int,
    raw_json: Path | None,
) -> tuple[dict, Path | None]:
    if raw_json is not None:
        payload = ffc.load_adp_json(raw_json)
        return payload, raw_json
    # Prefer a stable local cache if present (Cloudflare often blocks httpx).
    cached = Path("data/raw") / f"ffc_adp_ppr_{teams}tm_{year}.json"
    if cached.is_file():
        return ffc.load_adp_json(cached), cached
    payload = ffc.fetch_adp(year=year, teams=teams)
    path = ffc.save_raw(payload, year=year, teams=teams)
    return payload, path


def run_spike(
    *,
    year: int = 2024,
    teams: int = 10,
    raw_json: Path | None = None,
    eval_path: Path | None = None,
    skip_outcomes: bool = False,
) -> dict:
    eval_path = eval_path or EVAL_DB_PATH
    conn = connect_eval(eval_path)
    migrate_eval_schema(conn)

    payload, raw_path = _load_ffc_payload(year=year, teams=teams, raw_json=raw_json)
    players = ffc.parse_adp_players(payload)
    provenance = ffc.extract_provenance(
        payload, requested_year=year, requested_teams=teams
    )

    crosswalk = load_id_crosswalk()
    mapping = map_ffc_players(players, crosswalk)
    persist_mapping(conn, mapping)

    gsis_to_pid = {
        m["gsis_id"]: m["player_id"]
        for m in mapping["mapped"]
        if m.get("gsis_id")
    }

    outcomes = None
    if not skip_outcomes:
        outcomes = ingest_season_outcomes(
            conn,
            season=year,
            gsis_to_player_id=gsis_to_pid,
        )

    # Outcome coverage among mapped FFC players with gsis
    mapped_with_gsis = [m for m in mapping["mapped"] if m.get("gsis_id")]
    outcome_hit = 0
    if outcomes and mapped_with_gsis:
        pids = {m["player_id"] for m in mapped_with_gsis}
        rows = conn.execute(
            """
            SELECT player_id FROM eval_outcomes
            WHERE season = ? AND source = 'nflverse_computed'
            """,
            (year,),
        ).fetchall()
        have = {r["player_id"] for r in rows}
        outcome_hit = sum(1 for pid in pids if pid in have)

    # Snapshot stays non-evaluable (stage A). Prefer dated window end as date.
    as_of = provenance.get("as_of")
    snap_date = as_of or f"{year}-08-01"
    # Placeholder id until Gate 4 + evaluable promotion
    snapshot_id = f"{year}-preseason-ffc-pending"
    if as_of:
        # Still pending evaluable; date in id only if provenance dated
        snapshot_id = f"{year}-preseason-{as_of}-ffc-pending"

    # Decide validation_status / reason (fail closed; never evaluable here)
    reasons: list[str] = []
    if provenance["gate"] == "fail" and provenance.get("reason"):
        reasons.append(provenance["reason"])
    reasons.append("historical_projection_missing")
    if mapping["coverage"] < 0.85:
        reasons.append("player_mapping_below_threshold")
    n_map_gsis = len(mapped_with_gsis)
    cov_out = (outcome_hit / n_map_gsis) if n_map_gsis else 0.0
    if not skip_outcomes and n_map_gsis and cov_out < 0.85:
        reasons.append("outcome_coverage_below_threshold")

    primary_reason = reasons[0]
    validation_status = "source_validation"

    # ADP-only snapshot rows (proj null; as_of stamped for schema NOT NULL)
    proj_as_of = as_of or snap_date
    adp_as_of = as_of or snap_date
    # Use canonical player_id when mapped, else ffc: id
    by_ffc = {m["source_player_id"]: m for m in mapping["mapped"]}

    conn.execute(
        "DELETE FROM eval_snapshot_players WHERE snapshot_id = ?", (snapshot_id,)
    )
    conn.execute("DELETE FROM eval_snapshots WHERE snapshot_id = ?", (snapshot_id,))
    notes = (
        f"P2.2 stage-A feasibility spike. FFC PPR ADP year={year} "
        f"requested_teams={teams} meta_teams={provenance.get('meta_teams')}. "
        f"evaluable forced 0. Reasons: {', '.join(reasons)}. "
        f"Raw: {raw_path}"
    )
    conn.execute(
        """
        INSERT INTO eval_snapshots (
            snapshot_id, season, snapshot_date, label, notes, created_at,
            pipeline_proof, evaluable, outcome_season,
            validation_status, validation_reason
        ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
        """,
        (
            snapshot_id,
            year,
            snap_date,
            snapshot_id,
            notes,
            _utcnow(),
            year,
            validation_status,
            primary_reason,
        ),
    )
    snap_rows = []
    for p in players:
        m = by_ffc.get(str(p["ffc_player_id"]))
        pid = m["player_id"] if m else f"ffc:{p['ffc_player_id']}"
        snap_rows.append(
            (
                snapshot_id,
                pid,
                p.get("name"),
                p.get("position"),
                p.get("team"),
                p.get("adp"),
                "ffc",
                adp_as_of,
                None,
                None,
                proj_as_of,
            )
        )
    conn.executemany(
        """
        INSERT INTO eval_snapshot_players (
            snapshot_id, player_id, name, position, team,
            adp, adp_source, adp_as_of,
            proj_ppr, proj_source, proj_as_of
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        snap_rows,
    )
    conn.commit()

    report = {
        "stage": "A_feasibility",
        "snapshot_id": snapshot_id,
        "evaluable": 0,
        "pipeline_proof": 0,
        "validation_status": validation_status,
        "validation_reason": primary_reason,
        "validation_reasons_all": reasons,
        "ffc_raw_path": str(raw_path) if raw_path else None,
        "provenance": provenance,
        "mapping": {
            "n_ffc": mapping["n_ffc"],
            "n_mapped": mapping["n_mapped"],
            "n_manual": mapping["n_manual"],
            "n_unresolved": mapping["n_unresolved"],
            "coverage": mapping["coverage"],
            "name_only_joins": mapping["name_only_joins"],
            "unresolved_sample": mapping["unresolved"][:15],
        },
        "outcomes": outcomes,
        "outcome_coverage_mapped_gsis": {
            "n_mapped_with_gsis": n_map_gsis,
            "n_with_outcomes": outcome_hit,
            "coverage": cov_out,
        },
        "gates": {
            "ffc_adp_provenance": provenance["gate"],
            "player_mapping": "pass" if mapping["coverage"] >= 0.85 else "fail",
            "outcome_coverage": (
                "skip"
                if skip_outcomes
                else ("pass" if cov_out >= 0.85 else "fail")
            ),
            "historical_projection": "fail",
            "evaluable": "fail",
        },
        "eval_db": str(eval_path),
    }
    conn.close()
    return report


def to_markdown(report: dict) -> str:
    p = report["provenance"]
    m = report["mapping"]
    o = report.get("outcome_coverage_mapped_gsis") or {}
    lines = [
        f"# P2.2 feasibility spike — `{report['snapshot_id']}`",
        "",
        f"**Stage:** {report['stage']} (no draft replay; **evaluable=0**)",
        "",
        f"- validation_status: `{report['validation_status']}`",
        f"- validation_reason: `{report['validation_reason']}`",
        f"- all reasons: `{', '.join(report['validation_reasons_all'])}`",
        "",
        "## Gates",
        "",
        "| gate | result |",
        "| --- | --- |",
    ]
    for k, v in report["gates"].items():
        lines.append(f"| {k} | **{v}** |")
    lines += [
        "",
        "## FFC ADP provenance",
        "",
        f"- requested: year={p.get('requested_year')} teams={p.get('requested_teams')}",
        f"- meta teams/type: {p.get('meta_teams')} / {p.get('meta_type')}",
        f"- draft window: {p.get('start_date')} → {p.get('end_date')}",
        f"- as_of (end_date): `{p.get('as_of')}`",
        f"- interpretation: {p.get('as_of_interpretation')}",
        f"- players: {p.get('n_players')}",
        f"- gate: **{p.get('gate')}** reason=`{p.get('reason')}`",
        "",
        "## Player mapping (FFC → canonical → gsis)",
        "",
        "| Metric | Result |",
        "| --- | ---: |",
        f"| FFC players | {m['n_ffc']} |",
        f"| Automatically mapped | {m['n_mapped']} |",
        f"| Manually resolved | {m['n_manual']} |",
        f"| Unresolved | {m['n_unresolved']} |",
        f"| Coverage | {m['coverage']:.1%} |",
        f"| Name-only joins | **{m['name_only_joins']}** |",
        "",
        "## Outcomes (nflverse weekly → computed PPR)",
        "",
    ]
    if report.get("outcomes"):
        oc = report["outcomes"]
        lines += [
            f"- weekly rows: {oc.get('n_weekly_rows')}",
            f"- season players: {oc.get('n_players')}",
            f"- mapped-with-gsis outcome coverage: "
            f"{o.get('n_with_outcomes')}/{o.get('n_mapped_with_gsis')} "
            f"({o.get('coverage', 0):.1%})",
            "",
        ]
    else:
        lines.append("- skipped")
        lines.append("")
    lines += [
        "## Next",
        "",
        "- Do **not** set `evaluable=1` until historical projections (Gate 4) pass.",
        "- If FFC provenance failed, try another ADP source — treat fail as success.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2 stage-A feasibility spike")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--teams", type=int, default=10)
    parser.add_argument(
        "--raw-json",
        type=Path,
        default=None,
        help="FFC ADP JSON (use when API is Cloudflare-blocked)",
    )
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--skip-outcomes", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22_feasibility_2024.md"),
    )
    args = parser.parse_args()
    report = run_spike(
        year=args.year,
        teams=args.teams,
        raw_json=args.raw_json,
        eval_path=args.eval_db,
        skip_outcomes=args.skip_outcomes,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_markdown(report), encoding="utf-8")
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(to_markdown(report))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
