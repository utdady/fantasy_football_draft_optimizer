"""V3-A.0 calibration map: positional ADP → E[PPR] (train 2021–2023 only).

Frozen rules: results/phase2_v3a_gate3_calibration_freeze.md
Must not import or read 2024 outcomes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from draftopt.phase2.v3a_gate1_adp_provenance import TRAIN_YEARS, stable_raw_path
from draftopt.phase2.v3a_gate2_train_outcomes import run_year
from draftopt.sources import ffc

CURVE_ID = "adp_emp_pos_v1_train_2021_2023"
ADP_EDGES = [1.0, 12.0, 24.0, 36.0, 48.0, 60.0, 84.0, 108.0, 132.0, 156.0, 180.0, float("inf")]
MIN_N = 5
POSITIONS = ("QB", "RB", "WR", "TE", "DST")
ADP_RANGE_MID = 90.0
DEFAULT_ARTIFACT = Path("results/v3a_calibration_2021_2023.json")


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pava_non_decreasing(ys: list[float]) -> list[float]:
    """Classic adjacent-violator PAVA (non-decreasing)."""
    n = len(ys)
    if n == 0:
        return []
    # blocks: [sum, weight, size]
    blocks: list[list[float]] = []
    for y in ys:
        blocks.append([float(y), 1.0, 1.0])
        while len(blocks) >= 2:
            s0, w0, c0 = blocks[-2]
            s1, w1, c1 = blocks[-1]
            if s0 / w0 <= s1 / w1 + 1e-15:
                break
            blocks.pop()
            blocks.pop()
            blocks.append([s0 + s1, w0 + w1, c0 + c1])
    out: list[float] = []
    for s, w, c in blocks:
        out.extend([s / w] * int(c))
    return out


def _isotonic_nonincreasing_in_adp(ys: list[float]) -> list[float]:
    """Value must not rise as ADP worsens (ADP index ascending)."""
    return [-v for v in _pava_non_decreasing([-y for y in ys])]


def _merge_bins(bin_stats: list[dict]) -> list[dict]:
    """Merge bins with n < MIN_N toward the middle of the ADP range."""
    bins = [dict(b) for b in bin_stats if b["n"] > 0]
    if not bins:
        return []

    while True:
        small = [i for i, b in enumerate(bins) if b["n"] < MIN_N]
        if not small or len(bins) == 1:
            break
        i = small[0]
        if bins[i]["adp_center"] <= ADP_RANGE_MID:
            j = i + 1 if i + 1 < len(bins) else i - 1
        else:
            j = i - 1 if i - 1 >= 0 else i + 1
        a, b = bins[i], bins[j]
        n = a["n"] + b["n"]
        mean = (a["raw_mean"] * a["n"] + b["raw_mean"] * b["n"]) / n
        lo = min(a["lo"], b["lo"])
        hi_a, hi_b = a["hi"], b["hi"]
        hi = float("inf") if hi_a == float("inf") or hi_b == float("inf") else max(hi_a, hi_b)
        center_hi = 200.0 if hi == float("inf") else hi
        merged = {
            "lo": lo,
            "hi": hi,
            "n": n,
            "raw_mean": mean,
            "adp_center": (lo + center_hi) / 2.0,
        }
        for idx in sorted((i, j), reverse=True):
            bins.pop(idx)
        bins.insert(min(i, j), merged)
        bins.sort(key=lambda x: x["lo"])

    return bins


@dataclass
class PosMap:
    position: str
    points: list[dict[str, Any]]

    def value_at(self, adp: float) -> float:
        if not self.points:
            raise ValueError(f"empty map for {self.position}")
        a = max(1.0, float(adp))
        pts = self.points
        if a <= pts[0]["adp_center"]:
            return float(pts[0]["value"])
        if a >= pts[-1]["adp_center"]:
            return float(pts[-1]["value"])
        for i in range(len(pts) - 1):
            x0, x1 = pts[i]["adp_center"], pts[i + 1]["adp_center"]
            if x0 <= a <= x1:
                y0, y1 = pts[i]["value"], pts[i + 1]["value"]
                if x1 == x0:
                    return float(y0)
                t = (a - x0) / (x1 - x0)
                return float(y0 + t * (y1 - y0))
        return float(pts[-1]["value"])


def fit_position(pairs: list[dict], position: str) -> PosMap:
    rows = [p for p in pairs if p["position"] == position and p.get("adp") is not None]
    bin_stats: list[dict] = []
    for i in range(len(ADP_EDGES) - 1):
        lo, hi = ADP_EDGES[i], ADP_EDGES[i + 1]
        in_bin = [
            r
            for r in rows
            if (lo <= float(r["adp"]) < hi)
            or (hi == float("inf") and float(r["adp"]) >= lo)
        ]
        n = len(in_bin)
        raw_mean = sum(float(r["actual_ppr"]) for r in in_bin) / n if n else 0.0
        center_hi = min(hi, 200.0) if hi != float("inf") else 200.0
        bin_stats.append(
            {
                "lo": lo,
                "hi": hi,
                "n": n,
                "raw_mean": raw_mean,
                "adp_center": (lo + center_hi) / 2.0,
            }
        )
    merged = _merge_bins(bin_stats)
    if not merged:
        if not rows:
            return PosMap(position=position, points=[])
        mean = sum(float(r["actual_ppr"]) for r in rows) / len(rows)
        return PosMap(
            position=position,
            points=[
                {
                    "lo": 1.0,
                    "hi": None,
                    "n": len(rows),
                    "raw_mean": round(mean, 4),
                    "adp_center": 90.0,
                    "value": round(mean, 4),
                }
            ],
        )
    merged.sort(key=lambda b: b["adp_center"])
    ys = [b["raw_mean"] for b in merged]
    iso = _isotonic_nonincreasing_in_adp(ys)
    points = []
    for b, v in zip(merged, iso):
        points.append(
            {
                "lo": b["lo"],
                "hi": None if b["hi"] == float("inf") else b["hi"],
                "n": b["n"],
                "raw_mean": round(b["raw_mean"], 4),
                "adp_center": round(b["adp_center"], 4),
                "value": round(float(v), 4),
            }
        )
    return PosMap(position=position, points=points)


def collect_train_pairs() -> tuple[list[dict], dict]:
    """Build train pairs from Gate 1 raw + Gate 2 scoring (no 2024)."""
    meta_years = []
    all_pairs: list[dict] = []
    for year in TRAIN_YEARS:
        path = stable_raw_path(year)
        payload = ffc.load_adp_json(path)
        prov = ffc.extract_provenance(payload, requested_year=year, requested_teams=12)
        year_rep = run_year(year)
        pairs = year_rep["train_pairs"]
        for p in pairs:
            p = dict(p)
            p["adp_as_of"] = prov.get("as_of")
            all_pairs.append(p)
        meta_years.append(
            {
                "year": year,
                "as_of": prov.get("as_of"),
                "start_date": prov.get("start_date"),
                "end_date": prov.get("end_date"),
                "n_ffc": year_rep["n_ffc"],
                "n_mapped": year_rep["n_mapped"],
                "n_train_pairs": len(pairs),
                "raw_path": str(path),
            }
        )
    return all_pairs, {"years": meta_years}


def fit_calibration() -> dict:
    pairs, meta = collect_train_pairs()
    by_pos: dict[str, PosMap] = {}
    for pos in POSITIONS:
        by_pos[pos] = fit_position(pairs, pos)
    gmap = fit_position(
        [
            {"position": "ALL", "adp": p["adp"], "actual_ppr": p["actual_ppr"]}
            for p in pairs
        ],
        "ALL",
    )

    as_ofs = [y["as_of"] for y in meta["years"] if y.get("as_of")]
    calibration_as_of = max(as_ofs) if as_ofs else None

    return {
        "curve_id": CURVE_ID,
        "created_at": _utcnow(),
        "training_seasons": list(TRAIN_YEARS),
        "calibration_as_of": calibration_as_of,
        "eval_snapshot_as_of": "2024-09-01",
        "temporal_boundary": (
            "Training 2021–2023 only. No 2024 outcome information used in fit."
        ),
        "rules": {
            "adp_edges": [None if e == float("inf") else e for e in ADP_EDGES],
            "min_n": MIN_N,
            "monotone": "non-increasing value as ADP increases (PAVA)",
            "rookie_rule": "none — 2024 ADP through frozen map only",
            "fallback": "global ALL-position map if position empty",
            "missing_adp": "no value (None)",
        },
        "train_meta": meta,
        "n_train_pairs": len(pairs),
        "positions": {
            pos: {
                "n_pairs": sum(1 for p in pairs if p["position"] == pos),
                "points": by_pos[pos].points,
            }
            for pos in POSITIONS
        },
        "global_fallback": {"points": gmap.points},
        "train_pairs": pairs,
    }


class CalibrationMap:
    def __init__(self, artifact: dict):
        self.artifact = artifact
        self.curve_id = artifact["curve_id"]
        self._pos = {
            pos: PosMap(position=pos, points=list(data["points"]))
            for pos, data in artifact["positions"].items()
        }
        self._global = PosMap(
            position="ALL", points=list(artifact["global_fallback"]["points"])
        )

    @classmethod
    def load(cls, path: Path | None = None) -> CalibrationMap:
        p = path or DEFAULT_ARTIFACT
        return cls(json.loads(p.read_text(encoding="utf-8")))

    def value(self, adp: float | None, position: str | None) -> float | None:
        if adp is None:
            return None
        pos = (position or "").upper()
        pm = self._pos.get(pos)
        if pm is None or not pm.points:
            pm = self._global
        if not pm.points:
            return None
        return round(pm.value_at(float(adp)), 4)


def save_artifact(artifact: dict, path: Path | None = None) -> Path:
    out = path or DEFAULT_ARTIFACT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return out


def curve_meta(artifact: dict | None = None) -> dict:
    if artifact is None:
        return {"curve_id": CURVE_ID, "frozen": True}
    return {
        "curve_id": artifact["curve_id"],
        "calibration_as_of": artifact.get("calibration_as_of"),
        "training_seasons": artifact.get("training_seasons"),
        "n_train_pairs": artifact.get("n_train_pairs"),
        "frozen": True,
        "note": "Do not retune after seeing 2024 D−B / D−C.",
    }
