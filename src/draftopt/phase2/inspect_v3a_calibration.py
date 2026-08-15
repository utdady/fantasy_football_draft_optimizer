"""Calibration inspection (pos × ADP region) before trusting 2024 ladder Δ."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt.phase2.adp_value_curve import adp_to_value as structural_value
from draftopt.phase2.v3a_calibration import CURVE_ID, DEFAULT_ARTIFACT, CalibrationMap
from draftopt.sources import ffc

DEFAULT_RAW = Path("data/raw/ffc_adp_ppr_12tm_2024.json")
REGIONS = [
    ("R1-2", 1.0, 24.0),
    ("R3-4", 24.0, 48.0),
    ("R5-7", 48.0, 84.0),
    ("R8-10", 84.0, 120.0),
    ("R11+", 120.0, float("inf")),
]


def inspect(*, calibration_path: Path, raw_json: Path) -> dict:
    cal = CalibrationMap.load(calibration_path)
    art = cal.artifact
    payload = ffc.load_adp_json(raw_json)
    players = ffc.parse_adp_players(payload)

    # Train map summary already in artifact; add 2024 apply distribution
    by_pos_region: dict[str, dict] = {}
    for pos in ("QB", "RB", "WR", "TE", "DST"):
        by_pos_region[pos] = {}
        for label, lo, hi in REGIONS:
            subset = [
                p
                for p in players
                if (p.get("position") or "").upper() == pos
                and p.get("adp") is not None
                and (
                    (lo <= float(p["adp"]) < hi)
                    or (hi == float("inf") and float(p["adp"]) >= lo)
                )
            ]
            if not subset:
                by_pos_region[pos][label] = {"n": 0}
                continue
            cals = [cal.value(p["adp"], pos) for p in subset]
            structs = [structural_value(p["adp"]) for p in subset]
            cals_f = [c for c in cals if c is not None]
            structs_f = [s for s in structs if s is not None]
            mean_c = sum(cals_f) / len(cals_f) if cals_f else None
            mean_s = sum(structs_f) / len(structs_f) if structs_f else None
            by_pos_region[pos][label] = {
                "n": len(subset),
                "mean_v3a": round(mean_c, 2) if mean_c is not None else None,
                "mean_structural": round(mean_s, 2) if mean_s is not None else None,
                "delta_v3a_minus_structural": (
                    round(mean_c - mean_s, 2)
                    if mean_c is not None and mean_s is not None
                    else None
                ),
            }

    return {
        "curve_id": CURVE_ID,
        "calibration_as_of": art.get("calibration_as_of"),
        "n_train_pairs": art.get("n_train_pairs"),
        "train_position_bins": {
            pos: data["points"] for pos, data in art["positions"].items()
        },
        "apply_2024_pos_x_region": by_pos_region,
        "note": (
            "Inspection only — do not retune map from this table or from ladder Δ."
        ),
    }


def _md(report: dict) -> str:
    lines = [
        "# V3-A calibration inspection (pre-ladder)",
        "",
        f"- curve_id: `{report['curve_id']}`",
        f"- calibration_as_of: `{report['calibration_as_of']}`",
        f"- train pairs: {report['n_train_pairs']}",
        "",
        report["note"],
        "",
        "## Train isotonic bins",
        "",
    ]
    for pos, points in report["train_position_bins"].items():
        lines.append(f"### {pos}")
        lines.append("")
        lines.append("| ADP center | n | raw | isotonic |")
        lines.append("| ---: | ---: | ---: | ---: |")
        for p in points:
            lines.append(
                f"| {p['adp_center']} | {p['n']} | {p['raw_mean']} | {p['value']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## 2024 apply: mean V3-A vs structural by pos × ADP region",
            "",
            "| Pos | Region | n | mean V3-A | mean structural | Δ (V3A−C) |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for pos, regions in report["apply_2024_pos_x_region"].items():
        for label, row in regions.items():
            if row["n"] == 0:
                lines.append(f"| {pos} | {label} | 0 | — | — | — |")
            else:
                lines.append(
                    f"| {pos} | {label} | {row['n']} | {row['mean_v3a']} | "
                    f"{row['mean_structural']} | {row['delta_v3a_minus_structural']} |"
                )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect V3-A calibration map")
    parser.add_argument("--calibration", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--raw-json", type=Path, default=DEFAULT_RAW)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_v3a_calibration_inspection.md"),
    )
    args = parser.parse_args()
    report = inspect(calibration_path=args.calibration, raw_json=args.raw_json)
    md = _md(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
