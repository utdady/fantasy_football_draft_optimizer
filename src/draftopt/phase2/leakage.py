"""Leakage validator for Phase 2 decision-time snapshots.

Hard rule: every decision-feed timestamp must be ≤ snapshot_date.
recommend() must never query eval_outcomes — that is enforced by API design;
this module only validates snapshot row timestamps.
"""

from __future__ import annotations

from dataclasses import dataclass


class LeakageError(ValueError):
    """Raised when decision-time data is newer than the snapshot cutoff."""


@dataclass(frozen=True)
class LeakageFinding:
    snapshot_id: str
    player_id: str
    field: str
    as_of: str
    snapshot_date: str


def _date_only(iso: str) -> str:
    """Normalize to YYYY-MM-DD for lexicographic compare (ISO dates)."""
    s = (iso or "").strip()
    if not s:
        raise LeakageError("empty timestamp")
    return s[:10]


def check_as_of(*, as_of: str, snapshot_date: str, field: str) -> None:
    """Raise LeakageError if as_of > snapshot_date."""
    a = _date_only(as_of)
    d = _date_only(snapshot_date)
    if a > d:
        raise LeakageError(
            f"leakage: {field} as_of={a} > snapshot_date={d}"
        )


def validate_snapshot_player_row(
    *,
    snapshot_id: str,
    snapshot_date: str,
    player_id: str,
    adp_as_of: str,
    proj_as_of: str,
) -> list[LeakageFinding]:
    """
    Return list of leakage findings (empty = clean).
    Does not raise — caller may raise if findings non-empty.
    """
    findings: list[LeakageFinding] = []
    d = _date_only(snapshot_date)
    for field, as_of in (("adp_as_of", adp_as_of), ("proj_as_of", proj_as_of)):
        a = _date_only(as_of)
        if a > d:
            findings.append(
                LeakageFinding(
                    snapshot_id=snapshot_id,
                    player_id=player_id,
                    field=field,
                    as_of=a,
                    snapshot_date=d,
                )
            )
    return findings


def assert_snapshot_clean(
    rows: list[dict],
    *,
    snapshot_id: str,
    snapshot_date: str,
) -> None:
    """
    Validate an iterable of snapshot player dicts.

    Each row must include player_id, adp_as_of, proj_as_of.
    Raises LeakageError on first violation (fail closed).
    """
    for row in rows:
        findings = validate_snapshot_player_row(
            snapshot_id=snapshot_id,
            snapshot_date=snapshot_date,
            player_id=str(row.get("player_id") or ""),
            adp_as_of=str(row.get("adp_as_of") or ""),
            proj_as_of=str(row.get("proj_as_of") or ""),
        )
        if findings:
            f = findings[0]
            raise LeakageError(
                f"leakage in snapshot {f.snapshot_id} player {f.player_id}: "
                f"{f.field}={f.as_of} > snapshot_date={f.snapshot_date}"
            )


def validate_snapshot_table(conn, snapshot_id: str) -> list[LeakageFinding]:
    """
    Scan eval_snapshot_players for a snapshot_id; return all findings.

    Requires eval_* tables (phase2 schema) to exist on `conn`.
    """
    snap = conn.execute(
        "SELECT snapshot_date FROM eval_snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if snap is None:
        raise LookupError(f"unknown snapshot_id: {snapshot_id}")
    snapshot_date = snap["snapshot_date"]
    rows = conn.execute(
        """
        SELECT player_id, adp_as_of, proj_as_of
        FROM eval_snapshot_players
        WHERE snapshot_id = ?
        """,
        (snapshot_id,),
    ).fetchall()
    out: list[LeakageFinding] = []
    for row in rows:
        out.extend(
            validate_snapshot_player_row(
                snapshot_id=snapshot_id,
                snapshot_date=snapshot_date,
                player_id=row["player_id"],
                adp_as_of=row["adp_as_of"],
                proj_as_of=row["proj_as_of"],
            )
        )
    return out
