"""2026 draft-readiness: mock draft + failure modes + latency (frozen marginal).

Does not change strategies. Live draftopt.db only. Phase-2 DBs untouched.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx

from draftopt import db
from draftopt.backtest import pick_rng
from draftopt.config import DB_PATH, N_TEAMS, PICK_CLOCK_SECONDS, get_roster_preset
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.state import (
    create_draft,
    is_user_turn,
    record_user_pick,
    snapshot,
    undo_pick,
)
from draftopt.lineup import lineup_ev
from draftopt.pool import remaining_ranked
from draftopt.strategies import get_strategy


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    if len(ys) == 1:
        return ys[0]
    k = (len(ys) - 1) * p
    f = int(k)
    c = min(f + 1, len(ys) - 1)
    if f == c:
        return ys[f]
    return ys[f] + (ys[c] - ys[f]) * (k - f)


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": bool(ok), "detail": detail}


def check_db(conn) -> list[dict]:
    out = []
    n = conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"]
    out.append(_check("players_present", n >= 500, f"n={n}"))
    pulled = conn.execute(
        "SELECT MAX(pulled_at) AS t FROM projections_snapshots WHERE source='espn'"
    ).fetchone()["t"]
    out.append(_check("proj_pulled_at", bool(pulled), f"pulled_at={pulled}"))
    gibbs = conn.execute(
        """
        SELECT ROUND(pr.season_points, 1) AS pts
        FROM players p
        JOIN projections_snapshots pr ON p.player_id = pr.player_id
        WHERE p.name LIKE '%Gibbs%' AND pr.source='espn'
        ORDER BY pr.season_points DESC LIMIT 1
        """
    ).fetchone()
    pts = float(gibbs["pts"]) if gibbs else 0.0
    # 2026 season total should be mid-300s, not ~317 from 2025 latch
    out.append(
        _check(
            "gibbs_2026_proj",
            pts >= 340,
            f"Gibbs season_points={pts} (expect >=340 for 2026)",
        )
    )
    n_adp = conn.execute(
        "SELECT COUNT(*) AS n FROM adp_snapshots WHERE source='espn'"
    ).fetchone()["n"]
    out.append(_check("espn_adp_coverage", n_adp >= 700, f"n_adp={n_adp}"))
    return out


def _advance_cpus(conn, draft_id: str, seed: int) -> None:
    while True:
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        state = snapshot(conn, draft_id)
        if state["complete"] or is_user_turn(draft_row):
            return
        overall = int(draft_row["current_pick"])
        cpu_pick(conn, draft_id, rng=pick_rng(seed, overall), policy="noisy_adp")


def run_full_mock(
    conn,
    *,
    slot: int = 1,
    seed: int = 42,
    preset: str = "league_default",
) -> dict:
    strat = get_strategy("marginal")
    draft_id = create_draft(
        conn, user_slot=slot, user_name="Readiness", roster_preset=preset
    )
    checks: list[dict] = []
    latencies: list[float] = []
    user_picks: list[dict] = []
    issues: list[str] = []

    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if not is_user_turn(draft_row):
            _advance_cpus(conn, draft_id, seed)
            continue

        # Determinism at this state
        t0 = time.perf_counter()
        r1 = strat.recommend(conn, draft_id, n=3)
        latencies.append((time.perf_counter() - t0) * 1000.0)
        r2 = strat.recommend(conn, draft_id, n=3)
        if not r1:
            issues.append(f"empty recommend at overall={draft_row['current_pick']}")
            break
        if r1[0]["player_id"] != r2[0]["player_id"]:
            issues.append(
                f"nondeterministic top1 at overall={draft_row['current_pick']}: "
                f"{r1[0].get('name')} vs {r2[0].get('name')}"
            )

        # Drafted players must not appear in recommendations
        drafted = {
            str(p["player_id"])
            for p in state.get("picks") or []
        }
        leaked = [x for x in r1 if str(x["player_id"]) in drafted]
        if leaked:
            issues.append(f"recommend leaked drafted: {[x['name'] for x in leaked]}")

        pid = r1[0]["player_id"]
        record_user_pick(conn, draft_id, pid, made_by="strategy")
        user_picks.append(
            {
                "overall": int(draft_row["current_pick"]),
                "name": r1[0].get("name"),
                "position": r1[0].get("position"),
                "marginal": r1[0].get("marginal"),
            }
        )

        # Immediate removal
        rem_ids = {str(p["player_id"]) for p in remaining_ranked(conn, draft_id)}
        if str(pid) in rem_ids:
            issues.append(f"picked {r1[0].get('name')} still in remaining")

    state = snapshot(conn, draft_id)
    picks = state.get("picks") or []
    ids = [str(p["player_id"]) for p in picks]
    checks.append(
        _check(
            "full_draft_complete",
            bool(state.get("complete")),
            f"picks={len(picks)} complete={state.get('complete')}",
        )
    )
    checks.append(
        _check(
            "no_duplicate_board_picks",
            len(ids) == len(set(ids)),
            f"unique={len(set(ids))}/{len(ids)}",
        )
    )
    expected_user = int(
        conn.execute(
            "SELECT n_rounds FROM drafts WHERE draft_id=?", (draft_id,)
        ).fetchone()["n_rounds"]
    )
    checks.append(
        _check(
            "user_pick_count",
            len(user_picks) == expected_user,
            f"user_picks={len(user_picks)} expected={expected_user}",
        )
    )
    checks.append(
        _check("recommend_never_empty", not any("empty recommend" in i for i in issues), "")
    )
    checks.append(
        _check(
            "recommend_deterministic",
            not any("nondeterministic" in i for i in issues),
            "",
        )
    )
    checks.append(
        _check(
            "no_drafted_in_recommend",
            not any("leaked drafted" in i for i in issues),
            "",
        )
    )
    checks.append(
        _check(
            "picked_removed_from_pool",
            not any("still in remaining" in i for i in issues),
            "",
        )
    )

    # Final roster + FLEX via lineup_ev
    roster_preset = get_roster_preset(preset)
    slots = roster_preset["slots"]
    user_slot = slot
    user_players = [
        {
            "player_id": str(p["player_id"]),
            "name": p.get("name"),
            "position": (p.get("position") or "").upper(),
            "team": p.get("team"),
            "season_points": float(
                p.get("season_points") or p.get("proj_espn") or 0
            ),
        }
        for p in picks
        if int(p.get("team_slot") or 0) == user_slot
    ]
    # Enrich season_points from DB if missing on pick log
    for up in user_players:
        if up["season_points"]:
            continue
        row = conn.execute(
            """
            SELECT season_points FROM projections_snapshots
            WHERE player_id=? AND source='espn'
            """,
            (up["player_id"],),
        ).fetchone()
        if row and row["season_points"] is not None:
            up["season_points"] = float(row["season_points"])

    try:
        ev = lineup_ev(user_players, slots)
        flex_ok = True
        flex_detail = (
            f"total={ev.total:.1f} starters_slots="
            f"{ {k: len(v) for k, v in ev.starters.items() if v} }"
        )
        # FLEX slots should be filled if we have eligible leftovers
        flex_need = int(slots.get("FLEX") or 0)
        if flex_need and len(ev.starters.get("FLEX") or []) < flex_need:
            # Only fail if enough RB/WR/TE on roster to fill
            skill = sum(
                1
                for p in user_players
                if (p.get("position") or "") in {"RB", "WR", "TE"}
            )
            rb_need = int(slots.get("RB") or 0)
            wr_need = int(slots.get("WR") or 0)
            te_need = int(slots.get("TE") or 0)
            if skill >= rb_need + wr_need + te_need + flex_need:
                flex_ok = False
                flex_detail += " — FLEX underfilled despite enough skill players"
    except Exception as e:  # noqa: BLE001 — readiness probe
        ev = None
        flex_ok = False
        flex_detail = f"lineup_ev error: {e}"

    checks.append(_check("final_lineup_ev_flex", flex_ok, flex_detail))

    pos_counts = Counter((p.get("position") or "").upper() for p in user_players)
    return {
        "draft_id": draft_id,
        "slot": slot,
        "seed": seed,
        "user_picks": user_picks,
        "pos_counts": dict(pos_counts),
        "n_board_picks": len(picks),
        "latency_ms": {
            "n": len(latencies),
            "mean": round(statistics.mean(latencies), 2) if latencies else None,
            "p50": round(_pct(latencies, 0.50), 2) if latencies else None,
            "p95": round(_pct(latencies, 0.95), 2) if latencies else None,
            "max": round(max(latencies), 2) if latencies else None,
        },
        "checks": checks,
        "issues": issues,
        "clock_seconds": PICK_CLOCK_SECONDS,
        "comfortable_vs_clock": (
            latencies
            and _pct(latencies, 0.95) < (PICK_CLOCK_SECONDS * 1000 * 0.05)
        ),
    }


def failure_mode_snipe_and_undo(conn, *, seed: int = 7) -> dict:
    """Pick #2 instead of #1; undo; verify restore + deterministic recommend."""
    checks = []
    draft_id = create_draft(
        conn, user_slot=1, user_name="Snipe", roster_preset="league_default"
    )
    _advance_cpus(conn, draft_id, seed)
    r = get_strategy("marginal").recommend(conn, draft_id, n=3)
    checks.append(_check("snipe_has_alts", len(r) >= 2, f"n_recs={len(r)}"))
    if len(r) < 2:
        return {"checks": checks, "draft_id": draft_id}

    top1, top2 = r[0], r[1]
    # "Target sniped" simulation: take second choice
    record_user_pick(conn, draft_id, top2["player_id"], made_by="user")
    rem = {str(p["player_id"]) for p in remaining_ranked(conn, draft_id)}
    checks.append(
        _check(
            "alt_pick_removes_chosen",
            str(top2["player_id"]) not in rem,
            top2.get("name"),
        )
    )
    checks.append(
        _check(
            "skipped_target_still_available",
            str(top1["player_id"]) in rem,
            top1.get("name"),
        )
    )

    undo_pick(conn, draft_id)
    rem2 = {str(p["player_id"]) for p in remaining_ranked(conn, draft_id)}
    checks.append(
        _check(
            "undo_restores_both",
            str(top1["player_id"]) in rem2 and str(top2["player_id"]) in rem2,
            "",
        )
    )
    r_again = get_strategy("marginal").recommend(conn, draft_id, n=1)
    checks.append(
        _check(
            "undo_recommend_stable",
            bool(r_again) and r_again[0]["player_id"] == top1["player_id"],
            f"got={r_again[0].get('name') if r_again else None}",
        )
    )
    return {"draft_id": draft_id, "checks": checks, "top1": top1.get("name"), "took": top2.get("name")}


def failure_mode_late_board(conn, *, seed: int = 11) -> dict:
    """Latency + recommend at late user picks (pick 10+)."""
    draft_id = create_draft(
        conn, user_slot=5, user_name="Late", roster_preset="league_default"
    )
    strat = get_strategy("marginal")
    user_seen = 0
    late_lat: list[float] = []
    last_name = None
    while True:
        state = snapshot(conn, draft_id)
        if state["complete"]:
            break
        draft_row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)
        ).fetchone()
        if not is_user_turn(draft_row):
            _advance_cpus(conn, draft_id, seed)
            continue
        user_seen += 1
        t0 = time.perf_counter()
        recs = strat.recommend(conn, draft_id, n=1)
        ms = (time.perf_counter() - t0) * 1000.0
        if user_seen >= 8:
            late_lat.append(ms)
        if not recs:
            return {
                "checks": [_check("late_recommend", False, f"empty at user_pick={user_seen}")],
            }
        last_name = recs[0].get("name")
        record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="strategy")

    return {
        "draft_id": draft_id,
        "last_pick": last_name,
        "late_latency_ms": {
            "n": len(late_lat),
            "p50": round(_pct(late_lat, 0.50), 2) if late_lat else None,
            "p95": round(_pct(late_lat, 0.95), 2) if late_lat else None,
            "max": round(max(late_lat), 2) if late_lat else None,
        },
        "checks": [
            _check("late_draft_complete", True, f"user_picks={user_seen}"),
            _check(
                "late_latency_under_1s_p95",
                bool(late_lat) and _pct(late_lat, 0.95) < 1000,
                f"p95={_pct(late_lat, 0.95):.1f}" if late_lat else "no samples",
            ),
        ],
    }


def http_smoke(base: str = "http://127.0.0.1:8001") -> dict:
    checks = []
    try:
        with httpx.Client(timeout=30.0) as client:
            st = client.get(f"{base}/api/status")
            checks.append(
                _check("http_status", st.status_code == 200, f"code={st.status_code}")
            )
            if st.status_code != 200:
                return {"checks": checks, "base": base}
            body = st.json()
            checks.append(
                _check(
                    "http_players",
                    int(body.get("players") or 0) >= 500,
                    f"players={body.get('players')}",
                )
            )
            created = client.post(
                f"{base}/api/drafts",
                json={"user_slot": 1, "user_name": "HTTP", "roster_preset": "league_default"},
            )
            checks.append(
                _check("http_create_draft", created.status_code == 200, f"code={created.status_code}")
            )
            data = created.json()
            draft_id = (data.get("state") or {}).get("draft_id")
            recs = data.get("recommend") or []
            checks.append(
                _check("http_initial_recommend", len(recs) >= 1, f"n={len(recs)}")
            )
            # Advance CPUs then autopick a few user turns
            for _ in range(40):
                snap = client.get(
                    f"{base}/api/drafts/{draft_id}", params={"strategy": "marginal"}
                ).json()
                state = snap.get("state") or {}
                if state.get("complete"):
                    break
                if not state.get("is_user_turn"):
                    client.post(f"{base}/api/drafts/{draft_id}/cpu")
                    continue
                t0 = time.perf_counter()
                ap = client.post(
                    f"{base}/api/drafts/{draft_id}/autopick",
                    params={"strategy": "marginal"},
                )
                ms = (time.perf_counter() - t0) * 1000.0
                checks.append(
                    _check(
                        "http_autopick",
                        ap.status_code == 200,
                        f"code={ap.status_code} ms={ms:.1f}",
                    )
                )
                if ap.status_code != 200:
                    break
                # only one user pick for smoke after first
                if len([c for c in checks if c["check"] == "http_autopick" and c["ok"]]) >= 2:
                    break
            return {"base": base, "draft_id": draft_id, "checks": checks, "top": recs[0].get("name") if recs else None}
    except Exception as e:  # noqa: BLE001
        checks.append(_check("http_reachable", False, str(e)))
        return {"base": base, "checks": checks}


def run(*, http_base: str | None = "http://127.0.0.1:8001") -> dict:
    conn = db.connect(DB_PATH)
    db.init(conn)
    report: dict = {
        "stage": "SHIP_2026_DRAFT_READINESS",
        "created_at": _utcnow(),
        "db_path": str(DB_PATH),
        "strategy": "marginal",
        "n_teams": N_TEAMS,
        "claim": (
            "Product readiness for 2026 live DB with frozen marginal. "
            "Not a construction / Phase-2 ladder."
        ),
        "db_checks": check_db(conn),
        "full_mock": run_full_mock(conn, slot=1, seed=42),
        "snipe_undo": failure_mode_snipe_and_undo(conn, seed=7),
        "late_board": failure_mode_late_board(conn, seed=11),
    }
    conn.close()
    if http_base:
        report["http_smoke"] = http_smoke(http_base)

    all_checks: list[dict] = []
    all_checks.extend(report["db_checks"])
    for key in ("full_mock", "snipe_undo", "late_board", "http_smoke"):
        block = report.get(key) or {}
        all_checks.extend(block.get("checks") or [])
    report["summary"] = {
        "n_checks": len(all_checks),
        "n_pass": sum(1 for c in all_checks if c["ok"]),
        "n_fail": sum(1 for c in all_checks if not c["ok"]),
        "all_pass": all(c["ok"] for c in all_checks) if all_checks else False,
        "failed": [c for c in all_checks if not c["ok"]],
    }
    return report


def _md(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# 2026 draft readiness (frozen `marginal`)",
        "",
        f"- created: `{report['created_at']}`",
        f"- db: `{report['db_path']}`",
        f"- strategy: **{report['strategy']}** · teams: {report['n_teams']}",
        f"- checks: **{s['n_pass']}/{s['n_checks']} pass**",
        "",
        report["claim"],
        "",
        "## Verdict",
        "",
        (
            "**PASS — ready for continued mock-draft UX polish / rookie overlay next.**"
            if s["all_pass"]
            else "**FAIL — fix product issues before feature work.**"
        ),
        "",
    ]
    if s["failed"]:
        lines.extend(["### Failures", ""])
        for c in s["failed"]:
            lines.append(f"- `{c['check']}`: {c['detail']}")
        lines.append("")

    fm = report["full_mock"]
    lat = fm.get("latency_ms") or {}
    lines.extend(
        [
            "## Full 10-team mock (slot 1, seed 42)",
            "",
            f"- complete checks embedded; board picks: {fm.get('n_board_picks')}",
            f"- user pos mix: `{fm.get('pos_counts')}`",
            f"- recommend latency ms: p50={lat.get('p50')} p95={lat.get('p95')} "
            f"max={lat.get('max')} (clock={fm.get('clock_seconds')}s)",
            f"- comfortable vs 5% of clock: **{fm.get('comfortable_vs_clock')}**",
            "",
            "### User picks",
            "",
        ]
    )
    for p in fm.get("user_picks") or []:
        lines.append(
            f"- overall {p['overall']}: {p['name']} ({p['position']}) "
            f"M={p.get('marginal')}"
        )
    lines.extend(["", "## Failure modes", ""])
    for key, title in (
        ("snipe_undo", "Snipe / skip-target + undo"),
        ("late_board", "Late-board recommend + latency"),
        ("http_smoke", "HTTP API smoke (`/api`)"),
    ):
        block = report.get(key) or {}
        lines.append(f"### {title}")
        lines.append("")
        for c in block.get("checks") or []:
            mark = "PASS" if c["ok"] else "FAIL"
            lines.append(f"- {mark} `{c['check']}` {c.get('detail') or ''}")
        if key == "late_board" and block.get("late_latency_ms"):
            lines.append(f"- late latency: `{block['late_latency_ms']}`")
        lines.append("")

    lines.extend(
        [
            "## DB gates",
            "",
        ]
    )
    for c in report.get("db_checks") or []:
        mark = "PASS" if c["ok"] else "FAIL"
        lines.append(f"- {mark} `{c['check']}` {c.get('detail') or ''}")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "- If PASS: more harsh UI timing / human mock; then rookie overlay (not in formula).",
            "- Do **not** reopen V3 construction.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="2026 draft readiness (marginal)")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/SHIP_2026_DRAFT_READINESS.md"),
    )
    parser.add_argument(
        "--http-base",
        default="http://127.0.0.1:8001",
        help="API base; empty string to skip HTTP smoke",
    )
    args = parser.parse_args()
    http_base = args.http_base.strip() or None
    report = run(http_base=http_base)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    md = _md(report)
    args.out.write_text(md, encoding="utf-8")
    args.out.with_suffix(".json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(md)
    print(f"Wrote {args.out}")
    if not report["summary"]["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
