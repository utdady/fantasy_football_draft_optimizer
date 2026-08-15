"""Unit tests for P2.2 feasibility helpers."""

from __future__ import annotations

import pytest

from draftopt.phase2.map_players import map_ffc_players
from draftopt.phase2.ppr_scoring import week_ppr_points
from draftopt.sources.ffc import extract_provenance, parse_adp_players


def test_week_ppr_basic():
    pts = week_ppr_points(
        {
            "passing_yards": 250,
            "passing_tds": 2,
            "passing_interceptions": 1,
            "rushing_yards": 20,
            "receptions": 5,
            "receiving_yards": 60,
            "receiving_tds": 1,
        }
    )
    # 10 + 8 - 2 + 2 + 5 + 6 + 6 = 35
    assert pts == pytest.approx(35.0)


def test_ffc_provenance_dated_teams_ok():
    payload = {
        "meta": {
            "type": "PPR",
            "teams": 10,
            "start_date": "2024-08-20",
            "end_date": "2024-08-25",
            "total_drafts": 100,
        },
        "players": [{"player_id": 1, "name": "A", "position": "RB", "team": "SF", "adp": 1.0}],
    }
    prov = extract_provenance(payload, requested_year=2024, requested_teams=10)
    assert prov["gate"] == "pass"
    assert prov["as_of"] == "2024-08-25"
    assert prov["reason"] is None


def test_ffc_provenance_undated_fails():
    payload = {"meta": {"type": "PPR", "teams": 10}, "players": []}
    prov = extract_provenance(payload, requested_year=2024, requested_teams=10)
    assert prov["gate"] == "fail"
    assert prov["reason"] == "adp_as_of_unverified"


def test_ffc_provenance_teams_mismatch():
    payload = {
        "meta": {
            "teams": 12,
            "start_date": "2024-08-31",
            "end_date": "2024-09-01",
        },
        "players": [],
    }
    prov = extract_provenance(payload, requested_year=2024, requested_teams=10)
    assert prov["gate"] == "fail"
    assert prov["reason"] == "adp_league_size_mismatch"


def test_parse_adp_players():
    rows = parse_adp_players(
        {
            "players": [
                {
                    "player_id": 2434,
                    "name": "Christian McCaffrey",
                    "position": "RB",
                    "team": "SF",
                    "adp": 1.4,
                }
            ]
        }
    )
    assert rows[0]["ffc_player_id"] == "2434"
    assert rows[0]["position"] == "RB"


def test_map_ffc_name_pos_team_no_name_only():
    crosswalk = [
        {
            "player_id": "123",
            "name": "Christian McCaffrey",
            "name_fold": "christianmccaffrey",
            "position": "RB",
            "team": "SF",
            "sleeper_id": "123",
            "espn_id": "1",
            "fantasypros_id": "2",
            "gsis_id": "00-0033280",
        }
    ]
    ffc_players = [
        {
            "ffc_player_id": "2434",
            "name": "Christian McCaffrey",
            "position": "RB",
            "team": "SF",
            "adp": 1.4,
        }
    ]
    report = map_ffc_players(ffc_players, crosswalk)
    assert report["n_mapped"] == 1
    assert report["name_only_joins"] == 0
    assert report["mapped"][0]["method"] == "name_pos_team"
    assert report["mapped"][0]["gsis_id"] == "00-0033280"
