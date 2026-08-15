"""P2.2C outcome coverage gate under ppr_eval_v1_2024 (no Δ, evaluable=0)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from draftopt.config import EVAL_DB_PATH
from draftopt.phase2 import connect_eval
from draftopt.phase2.scoring_contract import (
    CONTRACT_ID,
    DECISION_SNAPSHOT_ID,
    OUTCOME_SEASON,
    OUTCOME_SOURCE,
    contract_meta,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_report(
    *,
    eval_db: Path | None = None,
    snapshot_id: str = DECISION_SNAPSHOT_ID,
    season: int = OUTCOME_SEASON,
    contract_id: str = CONTRACT_ID,
    source: str = OUTCOME_SOURCE,
) -> dict:
    conn = connect_eval(eval_db or EVAL_DB_PATH)
    snap = conn.execute(
        "SELECT snapshot_id, evaluable, validation_status FROM eval_snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if snap is None:
        raise RuntimeError(f"missing snapshot {snapshot_id}")

    pool = [
        dict(r)
        for r in conn.execute(
            """
            SELECT player_id, name, position, team
            FROM eval_snapshot_players WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        ).fetchall()
    ]
    status = {
        r["player_id"]: dict(r)
        for r in conn.execute(
            """
            SELECT player_id, outcome_state, actual_ppr_points, games_played, notes
            FROM eval_outcome_status
            WHERE season = ? AND contract_id = ? AND source = ?
            """,
            (season, contract_id, source),
        ).fetchall()
    }
    # Invariant: no missing_* row may have non-NULL points in status, and
    # missing_* must not appear in eval_outcomes.
    outcome_pids = {
        r["player_id"]
        for r in conn.execute(
            "SELECT player_id FROM eval_outcomes WHERE season = ? AND source = ?",
            (season, source),
        ).fetchall()
    }
    conn.close()

    by_state: Counter[str] = Counter()
    missing_rows: list[dict] = []
    coalesce_violations: list[dict] = []
    offense = [p for p in pool if (p.get("position") or "").upper() != "DST"]
    dst = [p for p in pool if (p.get("position") or "").upper() == "DST"]

    for p in pool:
        pid = p["player_id"]
        st = status.get(pid)
        if st is None:
            by_state["absent_status"] += 1
            missing_rows.append({**p, "outcome_state": "absent_status"})
            continue
        state = st["outcome_state"]
        by_state[state] += 1
        if state in {"missing_identity", "missing_weeks"}:
            missing_rows.append({**p, **st})
            if st.get("actual_ppr_points") is not None:
                coalesce_violations.append(
                    {
                        "player_id": pid,
                        "outcome_state": state,
                        "actual_ppr_points": st["actual_ppr_points"],
                        "reason": "missing_state_has_points",
                    }
                )
            if pid in outcome_pids:
                coalesce_violations.append(
                    {
                        "player_id": pid,
                        "outcome_state": state,
                        "reason": "missing_state_in_eval_outcomes",
                    }
                )
        elif state in {"observed_zero", "observed_points"}:
            if pid not in outcome_pids:
                coalesce_violations.append(
                    {
                        "player_id": pid,
                        "outcome_state": state,
                        "reason": "observed_missing_from_eval_outcomes",
                    }
                )

    n_off = len(offense)
    n_dst = len(dst)
    off_ok = sum(
        1
        for p in offense
        if (status.get(p["player_id"]) or {}).get("outcome_state")
        in {"observed_zero", "observed_points"}
    )
    dst_ok = sum(
        1
        for p in dst
        if (status.get(p["player_id"]) or {}).get("outcome_state")
        in {"observed_zero", "observed_points"}
    )

    reasons: list[str] = []
    if by_state.get("missing_identity", 0) > 0:
        reasons.append("outcome_missing_identity")
    if by_state.get("missing_weeks", 0) > 0:
        reasons.append("outcome_missing_weeks")
    if by_state.get("absent_status", 0) > 0:
        reasons.append("outcome_status_incomplete")
    if coalesce_violations:
        reasons.append("missing_coalesced_or_inconsistent")
    if off_ok < n_off:
        reasons.append("offense_outcome_incomplete")
    if dst_ok < n_dst:
        reasons.append("dst_outcome_incomplete")
    if int(snap["evaluable"] or 0) != 0:
        reasons.append("evaluable_unexpectedly_set")

    gate = "pass" if not reasons else "fail"

    return {
        "stage": "P2.2C_outcome_coverage",
        "created_at": _utcnow(),
        "snapshot_id": snapshot_id,
        "season": season,
        "contract_id": contract_id,
        "source": source,
        "evaluable": int(snap["evaluable"] or 0),
        "contract": contract_meta(),
        "n_pool": len(pool),
        "n_offense": n_off,
        "n_dst": n_dst,
        "offense_observed": off_ok,
        "dst_observed": dst_ok,
        "by_state": dict(by_state),
        "missing_sample": missing_rows[:40],
        "coalesce_violations": coalesce_violations,
        "outcome_coverage_gate": gate,
        "outcome_coverage_gate_reasons": reasons,
        "note": (
            "Outcome coverage only. No strategy Δ. missing ≠ zero invariant checked. "
            "evaluable stays 0 until a later promotion step after Δ methodology is reviewed."
        ),
        "next": (
            "Inspect this report. If gate=pass, next commit is boring Δ: "
            "adp_baseline vs adp_structural on actual starter PPR under this contract."
            if gate == "pass"
            else "Fix missing outcomes / DST weeks; re-attach; re-run this gate."
        ),
    }


def _md(report: dict) -> str:
    lines = [
        "# P2.2C outcome coverage",
        "",
        f"- snapshot: `{report['snapshot_id']}`",
        f"- contract: `{report['contract_id']}`",
        f"- season: {report['season']}",
        f"- evaluable: **{report['evaluable']}**",
        f"- outcome_coverage_gate: **{report['outcome_coverage_gate']}**",
        f"- reasons: {', '.join(report['outcome_coverage_gate_reasons']) or 'none'}",
        "",
        report["note"],
        "",
        "## Counts",
        "",
        f"| Metric | Value |",
        f"| --- | ---: |",
        f"| Pool | {report['n_pool']} |",
        f"| Offense/K observed | {report['offense_observed']}/{report['n_offense']} |",
        f"| DST observed | {report['dst_observed']}/{report['n_dst']} |",
        "",
        "## By outcome_state",
        "",
        "| State | n |",
        "| --- | ---: |",
    ]
    for state, n in sorted(report["by_state"].items()):
        lines.append(f"| `{state}` | {n} |")
    if report["missing_sample"]:
        lines.extend(["", "## Missing / incomplete sample", ""])
        lines.append("| Pos | Name | State | Notes |")
        lines.append("| --- | --- | --- | --- |")
        for m in report["missing_sample"][:25]:
            lines.append(
                f"| {m.get('position')} | {m.get('name')} | "
                f"`{m.get('outcome_state')}` | {m.get('notes') or '—'} |"
            )
    lines.extend(["", f"**Next:** {report['next']}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2C outcome coverage gate")
    parser.add_argument("--eval-db", type=Path, default=None)
    parser.add_argument("--snapshot-id", default=DECISION_SNAPSHOT_ID)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22c_outcome_coverage.md"),
    )
    args = parser.parse_args()
    report = build_report(eval_db=args.eval_db, snapshot_id=args.snapshot_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(md)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
