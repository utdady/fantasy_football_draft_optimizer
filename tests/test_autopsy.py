"""Autopsy tooling: case dump, analyze stubs, disagreement log."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from draftopt.autopsy import (
    autopsy_analyze,
    crude_survival_prob,
    dump_case,
    log_disagreement,
)
from draftopt.draft.state import DraftError, create_draft


def test_crude_survival_higher_adp_survives_more():
    low = crude_survival_prob(5.0, next_overall=24, n_cpu=22)
    high = crude_survival_prob(40.0, next_overall=24, n_cpu=22)
    assert low is not None and high is not None
    assert high > low


def test_dump_and_analyze(catalog, conn, tmp_path, monkeypatch):
    monkeypatch.setattr("draftopt.autopsy.CASES_DIR", tmp_path / "cases")
    draft_id = create_draft(conn, user_slot=1, user_name="addy")
    payload = dump_case(conn, draft_id, n_recs=3)
    assert payload["control"] == "marginal"
    assert payload["recommend"]
    path = tmp_path / "cases" / Path(payload["path"]).name
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["draft_id"] == draft_id

    report = autopsy_analyze(conn, draft_id, n_top=3)
    assert report["control"] == "marginal"
    assert "disclaimer" in report
    assert report["candidates"]
    assert all("M" in r or not r.get("ok") for r in report["candidates"])
    # Stub must not be implied as production
    assert "diagnostic" in report["disclaimer"].lower() or "stub" in report["disclaimer"].lower()


def test_disagreement_log(catalog, conn, tmp_path, monkeypatch):
    monkeypatch.setattr("draftopt.autopsy.DISAGREE_PATH", tmp_path / "disagree.jsonl")
    draft_id = create_draft(conn, user_slot=1)
    report = autopsy_analyze(conn, draft_id, n_top=3)
    rows = [r for r in report["candidates"] if r.get("ok")]
    assert len(rows) >= 2
    entry = log_disagreement(
        conn,
        draft_id,
        recommended_player_id=rows[0]["player_id"],
        chosen_player_id=rows[1]["player_id"],
        category="opportunity_cost",
        reason="test",
    )
    assert entry["category"] == "opportunity_cost"
    lines = (tmp_path / "disagree.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    with pytest.raises(DraftError):
        log_disagreement(
            conn,
            draft_id,
            recommended_player_id=rows[0]["player_id"],
            chosen_player_id=rows[1]["player_id"],
            category="not_a_real_category",
        )


def test_post_pick_diverge_freezes_take(catalog, conn, tmp_path, monkeypatch):
    monkeypatch.setattr("draftopt.autopsy.CASES_DIR", tmp_path / "cases")
    monkeypatch.setattr("draftopt.autopsy.DISAGREE_PATH", tmp_path / "disagree.jsonl")
    draft_id = create_draft(conn, user_slot=1)
    report = autopsy_analyze(conn, draft_id, n_top=3)
    rows = [r for r in report["candidates"] if r.get("ok")]
    assert len(rows) >= 2
    take = [
        {
            "player_id": rows[0]["player_id"],
            "name": rows[0]["name"],
            "position": rows[0].get("position"),
            "marginal": rows[0].get("M"),
        },
        {
            "player_id": rows[1]["player_id"],
            "name": rows[1]["name"],
            "position": rows[1].get("position"),
            "marginal": rows[1].get("M"),
        },
    ]
    dumped = dump_case(
        conn,
        draft_id,
        trigger="post_pick_diverge",
        chosen_player_id=rows[1]["player_id"],
        take_at_decision=take,
        overall_at_decision=1,
    )
    assert dumped["trigger"] == "post_pick_diverge"
    assert dumped["overall_at_decision"] == 1
    assert dumped["recommend"][0]["player_id"] == rows[0]["player_id"]
    assert dumped["chosen"]["player_id"] == rows[1]["player_id"]
    assert dumped["take_at_decision"][0]["marginal"] == rows[0].get("M")

    entry = log_disagreement(
        conn,
        draft_id,
        recommended_player_id=rows[0]["player_id"],
        chosen_player_id=rows[1]["player_id"],
        category="other",
        skipped_reason=True,
        case_path=dumped["path"],
        take_at_decision=take,
        overall_at_decision=1,
        trigger="post_pick_diverge",
    )
    assert entry["skipped_reason"] is True
    assert entry["trigger"] == "post_pick_diverge"
    assert entry["case_path"] == dumped["path"]
    assert entry["recommended"]["M"] == rows[0].get("M")

