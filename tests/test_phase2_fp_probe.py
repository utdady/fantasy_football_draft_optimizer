"""Unit tests for FP projection probe analysis (no network)."""

from draftopt.phase2.fp_projection_probe import analyze_payload


def test_analyze_forbidden():
    r = analyze_payload(403, {"message": "Forbidden"}, season=2024)
    assert r["verdict"] == "blocked_auth"


def test_analyze_players_no_dates_fails():
    body = {"players": [{"player_id": 1, "name": "A", "stats": {"rec": 50}}]}
    r = analyze_payload(200, body, season=2024)
    assert r["verdict"] == "fail_stage_B"
    assert r["reason"] == "projection_as_of_unverified"


def test_analyze_with_updated_needs_review():
    body = {
        "updated_at": "2024-08-25",
        "players": [{"player_id": 1, "name": "A"}],
    }
    r = analyze_payload(200, body, season=2024)
    assert r["verdict"] == "needs_human_date_check"
    assert r["gate"] == "pass_pending_review"
