from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path

import httpx

from draftopt.config import DP_ECR_URL, DP_IDS_URL, HTTP_HEADERS, PPR_ECR_PAGES, RAW_DIR


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_text(url: str, client: httpx.Client | None) -> str:
    own = client is None
    client = client or httpx.Client(headers=HTTP_HEADERS, timeout=120, follow_redirects=True)
    try:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text
    finally:
        if own:
            client.close()


def fetch_ids(client: httpx.Client | None = None) -> str:
    return _get_text(DP_IDS_URL, client)


def fetch_ecr(client: httpx.Client | None = None) -> str:
    return _get_text(DP_ECR_URL, client)


def save_raw(text: str, kind: str, pulled_at: str | None = None) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = (pulled_at or _utcnow()).replace(":", "")
    path = RAW_DIR / f"dynastyprocess_{kind}_{stamp}.csv"
    path.write_text(text, encoding="utf-8")
    return path


def _clean_id(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", "NA", "na", "None", "null"}:
        return None
    if text.endswith(".0"):
        text = text[:-2]
    return text


def parse_ids(csv_text: str) -> list[dict]:
    rows = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for raw in reader:
        sleeper_id = _clean_id(raw.get("sleeper_id"))
        espn_id = _clean_id(raw.get("espn_id"))
        fp_id = _clean_id(raw.get("fantasypros_id"))
        if not (sleeper_id or espn_id or fp_id):
            continue
        pos = (raw.get("position") or "").upper()
        if pos == "DEF":
            pos = "DST"
        if pos == "PK":
            pos = "K"
        rows.append(
            {
                "sleeper_id": sleeper_id,
                "espn_id": espn_id,
                "fantasypros_id": fp_id,
                "name": (raw.get("name") or "").strip(),
                "position": pos or None,
                "team": raw.get("team") or None,
            }
        )
    return rows


def parse_ecr(csv_text: str) -> list[dict]:
    rows = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for raw in reader:
        page = (raw.get("fp_page") or "").strip()
        page_type = (raw.get("page_type") or "").strip()
        keep = page in PPR_ECR_PAGES or page_type in {"redraft-overall", "redraft-k", "redraft-dst"}
        if page_type == "redraft-overall" and "ppr" not in page.lower():
            keep = False
        if not keep:
            continue
        fp_id = _clean_id(raw.get("id"))
        pos = (raw.get("pos") or "").upper()
        if pos == "DEF":
            pos = "DST"
        if pos == "PK":
            pos = "K"

        def num(key: str):
            val = raw.get(key)
            if val in (None, "", "NA"):
                return None
            try:
                return float(val)
            except ValueError:
                return None

        def integer(key: str):
            val = num(key)
            return int(val) if val is not None else None

        rows.append(
            {
                "fantasypros_id": fp_id,
                "name": (raw.get("player") or "").strip(),
                "position": pos or None,
                "team": raw.get("team") or raw.get("tm") or None,
                "ecr": num("ecr"),
                "sd": num("sd"),
                "best": integer("best"),
                "worst": integer("worst"),
                "bye": integer("bye"),
                "scrape_date": raw.get("scrape_date"),
            }
        )
    return rows
