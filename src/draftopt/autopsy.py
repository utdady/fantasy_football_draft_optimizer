"""Draft-decision autopsy tooling (diagnostic only — does not change TAKE).

Frozen production control: V1 ``marginal`` (M).
Investigative EV sketch (not shipped): EV ≈ M + E[next M | take i]
via ADP-greedy one-step future (same stub as experimental V2-alpha).

See results/AUTOPSY_GATE.md.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from draftopt.config import ROOT
from draftopt.draft.snake import next_user_overall, picks_until_next
from draftopt.draft.state import DraftError, _draft_row, draft_roster, resolve_player, snapshot
from draftopt.lookahead import as_lineup_player, two_pick_ev
from draftopt.lineup import lineup_ev
from draftopt.pool import candidate_pool, remaining_ranked
from draftopt.strategies.marginal import MarginalValueStrategy, _user_roster_players

CASES_DIR = ROOT / "results" / "autopsy_cases"
DISAGREE_PATH = ROOT / "results" / "autopsy_disagreements.jsonl"

DISAGREE_CATEGORIES = frozenset(
    {
        "opportunity_cost",
        "bad_data",
        "roster_construction",
        "human_policy",
        "uncertainty",
        "rec_sensible",
        "other",
    }
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def board_hash(state: dict) -> str:
    picks = [
        f"{p.get('overall')}:{p.get('player_id')}"
        for p in (state.get("picks") or [])
    ]
    raw = "|".join(picks)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def crude_survival_prob(
    adp: float | None,
    *,
    next_overall: int | None,
    n_cpu: int | None,
) -> float | None:
    """
    Diagnostic ADP prior only — not a production survival model.

    P(available at next user pick) ≈ sigmoid((ADP − next_overall) / scale)
    with scale = max(n_cpu/2, 3). Higher ADP than next pick → more likely to survive.
    """
    if next_overall is None or n_cpu is None or n_cpu < 0:
        return None
    if n_cpu == 0:
        return 1.0
    if adp is None:
        return 0.5
    scale = max(float(n_cpu) / 2.0, 3.0)
    x = (float(adp) - float(next_overall)) / scale
    return round(1.0 / (1.0 + math.exp(-x)), 4)


def dump_case(conn, draft_id: str, *, n_recs: int = 10) -> dict:
    """Snapshot board + top-N M recommendations to results/autopsy_cases/."""
    state = snapshot(conn, draft_id)
    recs = MarginalValueStrategy().recommend(conn, draft_id, n=n_recs)
    draft = _draft_row(conn, draft_id)
    overall = int(draft["current_pick"])
    n_teams = int(draft["n_teams"])
    n_rounds = int(draft["n_rounds"])
    user_slot = int(draft["user_slot"])
    nxt = next_user_overall(overall, user_slot, n_teams, n_rounds=n_rounds)
    until = picks_until_next(overall, user_slot, n_teams, n_rounds=n_rounds)

    payload = {
        "created_at": _utcnow(),
        "kind": "case_dump",
        "draft_id": draft_id,
        "board_hash": board_hash(state),
        "pick_mode": state.get("pick_mode"),
        "user_slot": user_slot,
        "user_name": state.get("user_name"),
        "current_pick": state.get("current_pick"),
        "current_team": state.get("current_team"),
        "current_round": state.get("current_round"),
        "is_user_turn": state.get("is_user_turn"),
        "complete": state.get("complete"),
        "n_teams": n_teams,
        "n_rounds": n_rounds,
        "next_user_overall": nxt,
        "picks_until_next": until,
        "control": "marginal",
        "recommend": [
            {
                "player_id": r.get("player_id"),
                "name": r.get("name"),
                "position": r.get("position"),
                "team": r.get("team"),
                "marginal": r.get("marginal"),
                "lineup_before": r.get("lineup_before"),
                "lineup_after": r.get("lineup_after"),
                "adp_espn": r.get("adp_espn"),
                "proj_espn": r.get("proj_espn"),
                "why": r.get("why"),
            }
            for r in recs
        ],
        "picks": [
            {
                "overall": p.get("overall"),
                "team_slot": p.get("team_slot"),
                "player_id": p.get("player_id"),
                "name": p.get("name"),
                "position": p.get("position"),
                "made_by": p.get("made_by"),
            }
            for p in (state.get("picks") or [])
        ],
        "team_labels": state.get("team_labels"),
    }
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{draft_id}_pick{overall}_{payload['board_hash']}.json"
    path = CASES_DIR / fname
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        payload["path"] = str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        payload["path"] = str(path)
    return payload


def _resolve_candidates(conn, draft_id: str, queries: list[str] | None, n_top: int) -> list[dict]:
    pool = {p["player_id"]: p for p in candidate_pool(conn, draft_id, n_adp=80)}
    # Also allow anyone remaining for named queries
    remaining = {p["player_id"]: p for p in remaining_ranked(conn, draft_id)}
    out: list[dict] = []
    seen: set[str] = set()

    if queries:
        for q in queries:
            q = (q or "").strip()
            if not q:
                continue
            try:
                pid = resolve_player(conn, draft_id, q)
            except DraftError:
                # try exact name match in remaining
                fold_q = q.casefold()
                hit = next(
                    (
                        p
                        for p in remaining.values()
                        if (p.get("name") or "").casefold() == fold_q
                    ),
                    None,
                )
                if hit is None:
                    raise DraftError(f"no remaining player matching {q!r}")
                pid = hit["player_id"]
            if pid in seen:
                continue
            player = remaining.get(pid) or pool.get(pid)
            if player is None:
                raise DraftError(f"player {pid} not remaining")
            seen.add(pid)
            out.append(player)

    if not out:
        for r in MarginalValueStrategy().recommend(conn, draft_id, n=n_top):
            pid = r["player_id"]
            if pid in seen:
                continue
            seen.add(pid)
            out.append(remaining.get(pid) or r)

    return out


def autopsy_analyze(
    conn,
    draft_id: str,
    *,
    queries: list[str] | None = None,
    n_top: int = 5,
) -> dict:
    """
    Transparent autopsy table for candidates at the current board.

    Does not write picks. Does not change TAKE. Lookahead stub is ADP-greedy
    (diagnostic only; same family as experimental V2-alpha).
    """
    draft = _draft_row(conn, draft_id)
    state = snapshot(conn, draft_id)
    slots = draft_roster(draft).get("slots") or {}
    n_teams = int(draft["n_teams"])
    n_rounds = int(draft["n_rounds"])
    user_slot = int(draft["user_slot"])
    overall = int(draft["current_pick"])
    nxt = next_user_overall(overall, user_slot, n_teams, n_rounds=n_rounds)
    until = picks_until_next(overall, user_slot, n_teams, n_rounds=n_rounds)
    n_cpu = int(until) if until is not None else 0

    roster = [
        p
        for p in (as_lineup_player(r) for r in _user_roster_players(conn, draft_id))
        if p["projection_quality"] == "high"
    ]
    base = lineup_ev(roster, slots).total
    remaining = remaining_ranked(conn, draft_id)
    candidates = _resolve_candidates(conn, draft_id, queries, n_top)

    rows: list[dict] = []
    for cand in candidates:
        lined = as_lineup_player(cand)
        if lined["projection_quality"] != "high" or lined["season_points"] <= 0:
            rows.append(
                {
                    "player_id": cand.get("player_id"),
                    "name": cand.get("name"),
                    "position": cand.get("position"),
                    "adp_espn": cand.get("adp_espn"),
                    "ok": False,
                    "error": "missing ESPN projection",
                }
            )
            continue

        after = lineup_ev(roster + [lined], slots).total
        m = after - base
        p_surv = crude_survival_prob(
            cand.get("adp_espn"),
            next_overall=nxt,
            n_cpu=until,
        )

        future = None
        next_m = None
        q_name = None
        ev_two = None
        delta = None
        if nxt is not None:
            result = two_pick_ev(
                roster,
                cand,
                remaining,
                slots,
                n_cpu_picks=n_cpu,
                future_policy="adp_greedy",
                n_teams=n_teams,
            )
            if result.get("ok"):
                one = float(result["one_pick"])
                ev = float(result["ev"])
                next_m = round(ev - one, 2)
                ev_two = round(ev - base, 2)  # M + next contribution
                delta = round(ev_two - m, 2)
                q = result.get("q")
                q_name = q.get("name") if q else None
                future = {
                    "policy": "adp_greedy_diagnostic",
                    "n_cpu_picks": n_cpu,
                    "q_name": q_name,
                    "q_position": (q.get("position") if q else None),
                }

        rows.append(
            {
                "player_id": cand.get("player_id"),
                "name": cand.get("name"),
                "position": cand.get("position"),
                "team": cand.get("team"),
                "adp_espn": cand.get("adp_espn"),
                "proj_espn": lined["season_points"],
                "ok": True,
                "M": round(m, 2),
                "lineup_before": round(base, 2),
                "lineup_after": round(after, 2),
                "P_survive_crude": p_surv,
                "E_next_M_stub": next_m,
                "EV_two_pick_stub": ev_two,
                "delta_EV_minus_M": delta,
                "future": future,
            }
        )

    rows_ok = [r for r in rows if r.get("ok")]
    control_best = max(rows_ok, key=lambda r: r["M"], default=None) if rows_ok else None
    stub_best = (
        max(
            (r for r in rows_ok if r.get("EV_two_pick_stub") is not None),
            key=lambda r: r["EV_two_pick_stub"],
            default=None,
        )
        if rows_ok
        else None
    )
    ranking_flipped = False
    if control_best and stub_best:
        ranking_flipped = control_best["player_id"] != stub_best["player_id"]

    report = {
        "created_at": _utcnow(),
        "kind": "autopsy_analyze",
        "draft_id": draft_id,
        "board_hash": board_hash(state),
        "control": "marginal",
        "disclaimer": (
            "Lookahead / survival columns are diagnostic stubs only. "
            "They do not change TAKE. Do not ship without Gate 1–3 in AUTOPSY_GATE.md."
        ),
        "current_pick": overall,
        "user_slot": user_slot,
        "next_user_overall": nxt,
        "picks_until_next": until,
        "lineup_ev_before": round(base, 2),
        "candidates": rows,
        "control_best_id": control_best["player_id"] if control_best else None,
        "control_best_name": control_best["name"] if control_best else None,
        "stub_best_id": stub_best["player_id"] if stub_best else None,
        "stub_best_name": stub_best["name"] if stub_best else None,
        "ranking_flipped_vs_M": ranking_flipped,
    }
    return report


def _resolve_any(conn, draft_id: str, query: str) -> str:
    """Resolve by player_id (even if drafted) or remaining-name search."""
    q = (query or "").strip()
    if not q:
        raise DraftError("empty query")
    by_id = conn.execute(
        "SELECT player_id FROM players WHERE player_id = ?", (q,)
    ).fetchone()
    if by_id:
        return by_id["player_id"]
    return resolve_player(conn, draft_id, q)


def log_disagreement(
    conn,
    draft_id: str,
    *,
    recommended_player_id: str,
    chosen_player_id: str,
    reason: str = "",
    category: str = "other",
) -> dict:
    """Append one Gate-3 disagreement row to results/autopsy_disagreements.jsonl."""
    cat = (category or "other").strip().lower()
    if cat not in DISAGREE_CATEGORIES:
        raise DraftError(
            f"category must be one of {sorted(DISAGREE_CATEGORIES)}"
        )
    state = snapshot(conn, draft_id)
    draft = _draft_row(conn, draft_id)
    recs = MarginalValueStrategy().recommend(conn, draft_id, n=5)
    rec_by_id = {r["player_id"]: r for r in recs}

    def _player_meta(pid: str) -> dict:
        row = conn.execute(
            "SELECT player_id, name, position, team FROM players WHERE player_id = ?",
            (pid,),
        ).fetchone()
        if row is None:
            raise DraftError(f"unknown player {pid}")
        m = rec_by_id.get(pid)
        return {
            "player_id": row["player_id"],
            "name": row["name"],
            "position": row["position"],
            "team": row["team"],
            "M": m.get("marginal") if m else None,
        }

    entry = {
        "created_at": _utcnow(),
        "kind": "disagreement",
        "draft_id": draft_id,
        "board_hash": board_hash(state),
        "current_pick": draft["current_pick"],
        "user_slot": draft["user_slot"],
        "pick_mode": state.get("pick_mode"),
        "is_user_turn": state.get("is_user_turn"),
        "recommended": _player_meta(recommended_player_id),
        "chosen": _player_meta(chosen_player_id),
        "category": cat,
        "reason": (reason or "").strip()[:500],
        "take_top": [
            {
                "player_id": r.get("player_id"),
                "name": r.get("name"),
                "marginal": r.get("marginal"),
            }
            for r in recs[:3]
        ],
    }
    DISAGREE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DISAGREE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    try:
        entry["path"] = str(DISAGREE_PATH.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        entry["path"] = str(DISAGREE_PATH)
    return entry


def format_analyze_markdown(report: dict) -> str:
    lines = [
        f"# Autopsy · draft `{report['draft_id']}` · pick {report['current_pick']}",
        "",
        f"- board_hash: `{report['board_hash']}`",
        f"- control: **{report['control']}**",
        f"- next user overall: {report.get('next_user_overall')}",
        f"- picks until next: {report.get('picks_until_next')}",
        f"- ranking flipped vs M (stub): **{report.get('ranking_flipped_vs_M')}**",
        "",
        report.get("disclaimer", ""),
        "",
        "| Player | Pos | M | P(survive) | E[next M] | EV stub | Δ(EV−M) | next q |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in report.get("candidates") or []:
        if not r.get("ok"):
            lines.append(
                f"| {r.get('name')} | {r.get('position')} | — | — | — | — | — | {r.get('error')} |"
            )
            continue
        fut = r.get("future") or {}
        lines.append(
            "| {name} | {pos} | {M} | {ps} | {en} | {ev} | {d} | {q} |".format(
                name=r.get("name"),
                pos=r.get("position"),
                M=r.get("M"),
                ps=r.get("P_survive_crude") if r.get("P_survive_crude") is not None else "—",
                en=r.get("E_next_M_stub") if r.get("E_next_M_stub") is not None else "—",
                ev=r.get("EV_two_pick_stub") if r.get("EV_two_pick_stub") is not None else "—",
                d=r.get("delta_EV_minus_M") if r.get("delta_EV_minus_M") is not None else "—",
                q=fut.get("q_name") or "—",
            )
        )
    lines.append("")
    lines.append(
        f"Control best: **{report.get('control_best_name')}** · "
        f"Stub best: **{report.get('stub_best_name')}**"
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse

    from draftopt import db

    parser = argparse.ArgumentParser(description="Draft autopsy tooling (diagnostic only)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_case = sub.add_parser("case", help="Dump board + top-N M to results/autopsy_cases/")
    p_case.add_argument("--draft-id", required=True)
    p_case.add_argument("--n", type=int, default=10)

    p_an = sub.add_parser("analyze", help="Transparent M + survival + next-pick stub table")
    p_an.add_argument("--draft-id", required=True)
    p_an.add_argument(
        "--players",
        default="",
        help="Comma-separated names/queries (default: top-N by M)",
    )
    p_an.add_argument("--n", type=int, default=5)
    p_an.add_argument("--out", default="", help="Optional markdown path under results/")

    p_log = sub.add_parser("disagree", help="Append a Gate-3 disagreement to jsonl")
    p_log.add_argument("--draft-id", required=True)
    p_log.add_argument("--recommended", required=True, help="player_id or name")
    p_log.add_argument("--chosen", required=True, help="player_id or name")
    p_log.add_argument("--category", default="other", choices=sorted(DISAGREE_CATEGORIES))
    p_log.add_argument("--reason", default="")

    args = parser.parse_args(argv)
    conn = db.connect()
    db.init(conn)
    try:
        if args.cmd == "case":
            payload = dump_case(conn, args.draft_id, n_recs=args.n)
            print(json.dumps({"path": payload["path"], "board_hash": payload["board_hash"]}, indent=2))
            return 0
        if args.cmd == "analyze":
            queries = [x.strip() for x in args.players.split(",") if x.strip()] or None
            report = autopsy_analyze(
                conn, args.draft_id, queries=queries, n_top=args.n
            )
            md = format_analyze_markdown(report)
            out = args.out.strip()
            if out:
                path = Path(out)
                if not path.is_absolute():
                    path = ROOT / path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(md, encoding="utf-8")
                report_path = path.with_suffix(".json")
                report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                print(md)
                print(f"\nWrote {path} and {report_path}")
            else:
                print(md)
                print(json.dumps({"ranking_flipped_vs_M": report["ranking_flipped_vs_M"]}, indent=2))
            return 0
        if args.cmd == "disagree":
            rec_id = _resolve_any(conn, args.draft_id, args.recommended)
            ch_id = _resolve_any(conn, args.draft_id, args.chosen)
            entry = log_disagreement(
                conn,
                args.draft_id,
                recommended_player_id=rec_id,
                chosen_player_id=ch_id,
                reason=args.reason,
                category=args.category,
            )
            print(json.dumps({"path": entry["path"], "category": entry["category"]}, indent=2))
            return 0
    except DraftError as e:
        print(f"error: {e}", file=__import__("sys").stderr)
        return 1
    finally:
        conn.close()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
