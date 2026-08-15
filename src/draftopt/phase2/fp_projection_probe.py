"""Short FantasyPros projections API probe (P2.2B Gate 4).

Requires env FANTASYPROS_API_KEY. Does not ingest into eval DB.
Hard rule: if response has no verifiable as_of / publish date → FAIL Stage B.

Usage:
  # Prefer local gitignored .env (see .env.example), or:
  set FANTASYPROS_API_KEY=...
  python -m draftopt.phase2.fp_projection_probe --season 2024
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from draftopt.envfile import load_dotenv

FP_PROJECTIONS_URLS = (
    # Free / public tier (current FantasyPros marketing docs)
    "https://api.fantasypros.com/public/v2/json/nfl/{season}/projections",
    # Legacy docs path (may require HOF/production key)
    "https://api.fantasypros.com/v2/json/nfl/{season}/projections",
)

# Keys that might carry temporal provenance in API payloads (case-insensitive scan).
DATEISH_KEYS = (
    "as_of",
    "asof",
    "updated",
    "updated_at",
    "update_date",
    "published",
    "published_at",
    "publish_date",
    "scrape_date",
    "last_updated",
    "last_modified",
    "timestamp",
    "date",
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _find_dateish(obj: Any, path: str = "", found: list[tuple[str, Any]] | None = None) -> list[tuple[str, Any]]:
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if str(k).lower().replace("-", "_") in DATEISH_KEYS or any(
                d in str(k).lower() for d in ("date", "time", "updated", "publish")
            ):
                if not isinstance(v, (dict, list)):
                    found.append((p, v))
            _find_dateish(v, p, found)
    elif isinstance(obj, list) and obj:
        _find_dateish(obj[0], f"{path}[0]", found)
        if len(obj) > 1:
            _find_dateish(obj[-1], f"{path}[-1]", found)
    return found


def _headers(api_key: str) -> dict[str, str]:
    return {
        "x-api-key": api_key,
        "User-Agent": "draftopt/0.1 (personal research; P2.2B projection probe)",
        "Accept": "application/json",
    }


def canary_key_works(api_key: str) -> dict[str, Any]:
    """Hit a cheap public endpoint to distinguish bad key vs projections-only deny."""
    url = "https://api.fantasypros.com/public/v2/json/nfl/players"
    with httpx.Client(timeout=45, follow_redirects=True) as client:
        resp = client.get(
            url,
            headers=_headers(api_key),
            params={"ecr": "included"},
        )
    return {
        "url": url,
        "http_status": resp.status_code,
        "ok": resp.status_code == 200,
    }


def fetch_projections(
    *,
    season: int,
    api_key: str,
    week: int = 0,
    scoring: str = "PPR",
    position: str = "RB",
) -> tuple[int, dict[str, Any] | str, str]:
    headers = _headers(api_key)
    params = {"week": week, "scoring": scoring, "position": position}
    last_status = 0
    last_body: dict[str, Any] | str = ""
    last_url = FP_PROJECTIONS_URLS[0]
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for template in FP_PROJECTIONS_URLS:
            url = template.format(season=season)
            last_url = url
            resp = client.get(url, headers=headers, params=params)
            last_status = resp.status_code
            try:
                last_body = resp.json()
            except Exception:
                last_body = resp.text[:2000]
            if resp.status_code == 200:
                return resp.status_code, last_body, url
    # Prefer a short error body for the report (no secrets).
    return last_status, last_body, last_url


def analyze_payload(status: int, body: dict[str, Any] | str, *, season: int) -> dict[str, Any]:
    report: dict[str, Any] = {
        "probed_at": _utcnow(),
        "season": season,
        "http_status": status,
        "gate": "fail",
        "reason": None,
        "has_players": False,
        "n_players_sample_endpoint": None,
        "dateish_fields": [],
        "verdict": None,
        "notes": [],
    }
    if status == 403:
        report["reason"] = "api_forbidden"
        report["verdict"] = "blocked_auth"
        report["notes"].append("Valid FANTASYPROS_API_KEY required (403 Forbidden).")
        if isinstance(body, dict):
            report["error_body"] = {k: body[k] for k in list(body)[:8]}
        elif isinstance(body, str) and body:
            report["error_body_preview"] = body[:300]
        return report
    if status == 401:
        report["reason"] = "api_unauthorized"
        report["verdict"] = "blocked_auth"
        return report
    if status != 200 or not isinstance(body, dict):
        report["reason"] = "api_error"
        report["verdict"] = "fail"
        report["notes"].append(f"Unexpected status/body type: {status} {type(body)}")
        return report

    players = body.get("players") or body.get("projections") or []
    if isinstance(players, dict):
        players = list(players.values())
    report["has_players"] = bool(players)
    report["n_players_sample_endpoint"] = len(players) if isinstance(players, list) else None
    report["top_keys"] = sorted(body.keys())

    dateish = _find_dateish(body)
    report["dateish_fields"] = [{"path": p, "value": v} for p, v in dateish[:40]]

    # Stage B needs a defensible publish/as_of — season year alone is insufficient.
    usable_dates = [
        d
        for d in dateish
        if d[1] not in (None, "", 0, "0") and str(d[1])[:4] not in ("",)
    ]
    if not report["has_players"]:
        report["reason"] = "empty_projections"
        report["verdict"] = "fail"
        report["notes"].append("200 OK but no player projections in sample response.")
    elif not usable_dates:
        report["reason"] = "projection_as_of_unverified"
        report["verdict"] = "fail_stage_B"
        report["gate"] = "fail"
        report["notes"].append(
            "Payload has players but no clear publish/as_of timestamp. "
            "season={season} + week=0 is not sufficient provenance.".format(season=season)
        )
    else:
        report["gate"] = "pass_pending_review"
        report["verdict"] = "needs_human_date_check"
        report["notes"].append(
            "Date-like fields found — human must confirm they are preseason "
            "publish times ≤ chosen snapshot_date, not pull time or season label."
        )
        report["reason"] = None
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P2.2B — FantasyPros projections API probe",
        "",
        f"- probed_at: `{report.get('probed_at')}`",
        f"- season: **{report.get('season')}**",
        f"- http_status: **{report.get('http_status')}**",
        f"- gate: **{report.get('gate')}**",
        f"- verdict: **{report.get('verdict')}**",
        f"- reason: `{report.get('reason')}`",
        "",
    ]
    canary = report.get("canary_players")
    if canary:
        lines += [
            "## Auth canary (`/nfl/players`)",
            "",
            f"- http_status: **{canary.get('http_status')}**",
            f"- key_appears_valid: **{canary.get('ok')}**",
            "",
        ]
    lines += [
        "## Notes",
        "",
    ]
    for n in report.get("notes") or []:
        lines.append(f"- {n}")
    lines += [
        "",
        "## Date-like fields (sample)",
        "",
    ]
    fields = report.get("dateish_fields") or []
    if not fields:
        lines.append("_None found._")
    else:
        lines.append("| path | value |")
        lines.append("| --- | --- |")
        for f in fields[:25]:
            lines.append(f"| `{f['path']}` | {f['value']!r} |")
    lines += [
        "",
        "## Hard rule",
        "",
        "No verifiable as_of → **reject for Stage B**. Do not convert ECR→points.",
        "Re-run: `python -m draftopt.phase2.fp_projection_probe --season 2024`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="P2.2B FantasyPros projection provenance probe")
    parser.add_argument("--season", type=int, default=2024)
    parser.add_argument("--week", type=int, default=0, help="0 = preseason per FP docs")
    parser.add_argument("--scoring", type=str, default="PPR")
    parser.add_argument("--position", type=str, default="RB")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/phase2_p22b_fp_probe.md"),
    )
    args = parser.parse_args()
    loaded = load_dotenv()
    key = (os.environ.get("FANTASYPROS_API_KEY") or os.environ.get("FP_API_KEY") or "").strip()
    if not key:
        report = {
            "probed_at": _utcnow(),
            "season": args.season,
            "http_status": None,
            "gate": "fail",
            "reason": "api_key_missing",
            "has_players": False,
            "n_players_sample_endpoint": None,
            "dateish_fields": [],
            "verdict": "blocked_no_key",
            "notes": [
                "Set FANTASYPROS_API_KEY in gitignored `.env` (see `.env.example`) "
                "or in the shell, then re-run.",
                f"Checked .env path: {loaded or '(missing)'}.",
                "Without a key the API returns 403; historical as_of cannot be verified.",
                "Docs: GET /public/v2/json/nfl/{season}/projections?week=0&scoring=PPR "
                "(week=0 = preseason). No as_of query parameter is documented — "
                "provenance must come from response fields or fail closed.",
            ],
        }
    else:
        canary = canary_key_works(key)
        status, body, used_url = fetch_projections(
            season=args.season,
            api_key=key,
            week=args.week,
            scoring=args.scoring,
            position=args.position,
        )
        report = analyze_payload(status, body, season=args.season)
        report["canary_players"] = canary
        report["request"] = {
            "week": args.week,
            "scoring": args.scoring,
            "position": args.position,
            "url": used_url,
        }
        if status == 403:
            if canary.get("ok"):
                report["reason"] = "projections_forbidden"
                report["verdict"] = "fail_stage_B"
                report["notes"] = [
                    "API key works on /nfl/players (canary 200), but "
                    f"/{args.season}/projections returned 403 on public+legacy paths.",
                    "Free-tier key cannot access the projections endpoint (or this "
                    "season) under current auth. Stage B via FP projections is blocked.",
                    "No historical projection source meeting provenance requirements "
                    "was confirmed for the 2024 evaluation window via FantasyPros free API.",
                    "Next: stop FP archaeology; open labeled ADP-only structural track.",
                    "Do not paste the key into chat or commit it.",
                ]
            else:
                report["notes"].append(
                    f"Canary /nfl/players also failed (status={canary.get('http_status')}). "
                    "Key may be invalid, not activated, or IP/tier blocked."
                )
                report["notes"].append(
                    "Tried /public/v2/json and /v2/json for projections. "
                    "Do not paste the key into chat or commit it."
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_markdown(report), encoding="utf-8")
    args.out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(to_markdown(report))
    print(f"Wrote {args.out}")
    if report.get("verdict") in {"blocked_no_key", "blocked_auth", "fail", "fail_stage_B"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
