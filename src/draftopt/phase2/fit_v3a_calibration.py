"""Fit and freeze V3-A.0 calibration map (2021–2023 only). No 2024 outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt.phase2.v3a_calibration import (
    CURVE_ID,
    DEFAULT_ARTIFACT,
    fit_calibration,
    save_artifact,
)


def _md(artifact: dict) -> str:
    lines = [
        "# V3-A.0 calibration fit (frozen)",
        "",
        f"- curve_id: `{artifact['curve_id']}`",
        f"- created: `{artifact['created_at']}`",
        f"- training_seasons: {artifact['training_seasons']}",
        f"- calibration_as_of: `{artifact['calibration_as_of']}`",
        f"- eval_snapshot_as_of: `{artifact['eval_snapshot_as_of']}`",
        f"- n_train_pairs: **{artifact['n_train_pairs']}**",
        "",
        artifact["temporal_boundary"],
        "",
        "## Train years",
        "",
        "| Year | as_of | FFC | Mapped | Train pairs |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for y in artifact["train_meta"]["years"]:
        lines.append(
            f"| {y['year']} | {y['as_of']} | {y['n_ffc']} | {y['n_mapped']} | "
            f"{y['n_train_pairs']} |"
        )
    lines.extend(
        [
            "",
            "## Position maps (isotonic values at bin centers)",
            "",
        ]
    )
    for pos, data in artifact["positions"].items():
        lines.append(f"### {pos} (n={data['n_pairs']})")
        lines.append("")
        lines.append("| ADP center | n | raw mean | isotonic value |")
        lines.append("| ---: | ---: | ---: | ---: |")
        for p in data["points"]:
            lines.append(
                f"| {p['adp_center']} | {p['n']} | {p['raw_mean']} | {p['value']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Rules",
            "",
            f"- edges: `{artifact['rules']['adp_edges']}`",
            f"- min_n: {artifact['rules']['min_n']}",
            f"- monotone: {artifact['rules']['monotone']}",
            f"- rookies: {artifact['rules']['rookie_rule']}",
            "",
            "**Do not retune after seeing 2024 ladder Δ.**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit V3-A.0 calibration map")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/phase2_v3a_calibration_fit.md"),
    )
    args = parser.parse_args()
    artifact = fit_calibration()
    assert artifact["curve_id"] == CURVE_ID
    path = save_artifact(artifact, args.out)
    # Slim JSON for report companion (drop bulky train_pairs)
    slim = {k: v for k, v in artifact.items() if k != "train_pairs"}
    md = _md(artifact)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(md, encoding="utf-8")
    args.report.with_suffix(".json").write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {path}")
    print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()
