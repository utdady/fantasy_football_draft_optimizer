"""V3-A Gate 1: historical FFC ADP provenance for train years 2021–2023.

Saves/loads data/raw/ffc_adp_ppr_12tm_{year}.json and reports dating + mapping
coverage. Does not fit calibration or touch 2024 outcomes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from draftopt.config import RAW_DIR
from draftopt.phase2.map_players import load_id_crosswalk, map_ffc_players
from draftopt.sources import ffc

TRAIN_YEARS = (2021, 2022, 2023)
TEAMS = 12
SCORING = "ppr"


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_raw_path(year: int) -> Path:
    return RAW_DIR / f"ffc_adp_ppr_{TEAMS}tm_{year}.json"


def load_or_fetch(year: int, *, raw_json: Path | None = None) -> tuple[dict, Path, str]:
    if raw_json is not None:
        return ffc.load_adp_json(raw_json), raw_json, "raw_json_arg"
    stable = stable_raw_path(year)
    if stable.is_file():
        return ffc.load_adp_json(stable), stable, "stable_cache"
    try:
        payload = ffc.fetch_adp(year=year, teams=TEAMS, scoring=SCORING)
        path = ffc.save_raw(payload, year=year, teams=TEAMS)
        stable.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload, stable, "httpx_fetch"
    except Exception as e:
        raise RuntimeError(
            f"FFC fetch failed for {year}: {e}. "
            f"Save browser JSON to {stable} and re-run."
        ) from e


def run_gate1(*, raw_by_year: dict[int, Path] | None = None) -> dict:
    crosswalk = load_id_crosswalk()
    years_out: list[dict] = []
    for year in TRAIN_YEARS:
        raw_arg = (raw_by_year or {}).get(year)
        payload, path, how = load_or_fetch(year, raw_json=raw_arg)
        # keep stable copy
        stable = stable_raw_path(year)
        if path.resolve() != stable.resolve():
            stable.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        prov = ffc.extract_provenance(
            payload, requested_year=year, requested_teams=TEAMS
        )
        players = ffc.parse_adp_players(payload)
        mapping = map_ffc_players(players, crosswalk)
        unresolved = [
            {
                "name": u.get("name"),
                "position": u.get("position"),
                "team": u.get("team"),
                "ffc_player_id": u.get("ffc_player_id") or u.get("source_player_id"),
            }
            for u in (mapping.get("unresolved") or [])
        ]
        years_out.append(
            {
                **prov,
                "fetch": how,
                "stable_raw_path": str(stable),
                "n_parsed": len(players),
                "mapping": {
                    "n_ffc": mapping["n_ffc"],
                    "n_mapped": mapping["n_mapped"],
                    "n_unresolved": mapping["n_unresolved"],
                    "coverage": mapping["coverage"],
                    "unresolved": unresolved,
                },
                "source": "fantasyfootballcalculator.com",
                "scoring": SCORING,
                "market": "FFC 12-team PPR",
                "url": ffc.adp_url(year=year, teams=TEAMS, scoring=SCORING),
                "attribution": "https://fantasyfootballcalculator.com/",
            }
        )

    all_pass = all(y["gate"] == "pass" for y in years_out)
    # dating + teams required; mapping coverage advisory if < 0.95
    map_ok = all(y["mapping"]["coverage"] >= 0.95 for y in years_out)
    verdict = "pass" if all_pass and map_ok else ("pass_with_warnings" if all_pass else "fail")

    return {
        "stage": "V3A_gate1_adp_provenance",
        "created_at": _utcnow(),
        "train_years": list(TRAIN_YEARS),
        "requested_teams": TEAMS,
        "scoring": SCORING,
        "source": "FFC",
        "verdict": verdict,
        "dating_gate": "pass" if all_pass else "fail",
        "mapping_gate": "pass" if map_ok else "fail",
        "years": years_out,
        "notes": [
            "as_of = FFC meta.end_date (draft-window upper bound), same rule as P2.2C.",
            "Direct httpx may 403 (Cloudflare); use stable data/raw cache from browser/WebFetch.",
            "No 2024 outcomes used. No calibration fit.",
            "2022 player count may be thin if FFC window is short — still dated.",
        ],
        "next": (
            "Gate 2 — historical outcomes for train years under same PPR rules"
            if verdict.startswith("pass")
            else "STOP — do not substitute undated ADP / ECR"
        ),
    }


def _md(report: dict) -> str:
    lines = [
        "# V3-A Gate 1 — historical ADP provenance (2021–2023)",
        "",
        f"- created: `{report['created_at']}`",
        f"- market: FFC {report['requested_teams']}-team {report['scoring'].upper()}",
        f"- verdict: **{report['verdict']}**",
        f"- dating gate: **{report['dating_gate']}**",
        f"- mapping gate (≥95%): **{report['mapping_gate']}**",
        "",
        "Prerequisite for V3-A.0. No calibration fit. No 2024 outcome peek.",
        "",
        "## Per-year provenance",
        "",
        "| Year | Dating | as_of | Window | Teams | Players | Mapped | Coverage | Raw |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for y in report["years"]:
        win = f"{y.get('start_date')} → {y.get('end_date')}"
        lines.append(
            f"| {y['requested_year']} | {y['gate']} | `{y.get('as_of')}` | {win} | "
            f"{y.get('meta_teams')} | {y.get('n_players')} | "
            f"{y['mapping']['n_mapped']} | {y['mapping']['coverage']:.1%} | "
            f"`{y['stable_raw_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Checklist",
            "",
            f"- [{'x' if report['dating_gate']=='pass' else ' '}] Concrete preseason/as_of date per year",
            f"- [x] Documented source (FFC API / attribution)",
            f"- [{'x' if report['mapping_gate']=='pass' else ' '}] Player identity mapping (≥95% to gsis/crosswalk)",
            "- [x] No post-draft info in ADP payload (window ends at meta.end_date)",
            "- [x] Same market definition: FFC 12-team PPR (matches 2024 eval market size)",
            "",
            f"**Next:** {report['next']}",
            "",
            "If dating fails: **stop**. Do not substitute ECR or undated ADP.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="V3-A Gate 1 ADP provenance")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_gate1_adp_provenance.md"),
    )
    args = parser.parse_args()
    report = run_gate1()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_md(report), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(_md(report))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
