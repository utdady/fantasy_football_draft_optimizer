"""FantasyPros overlay: parse + build without touching marginal."""

from __future__ import annotations

from draftopt.fp_overlay import build_overlay
from draftopt.draft.state import create_draft
from draftopt.sources.fantasypros import parse_overall_rankings, parse_projections


def test_parse_overall_rankings_uses_all_page_only():
    bundle = {
        "pages": {
            "ALL": {
                "players": [
                    {
                        "player_id": 1,
                        "player_name": "A",
                        "player_position_id": "RB",
                        "rank_ecr": 2,
                        "rank_std": "1.5",
                        "rank_min": "1",
                        "rank_max": "5",
                    }
                ]
            },
            "RB": {
                "players": [
                    {
                        "player_id": 1,
                        "player_name": "A",
                        "player_position_id": "RB",
                        "rank_ecr": 1,
                    }
                ]
            },
        }
    }
    rows = parse_overall_rankings(bundle)
    assert len(rows) == 1
    assert rows[0]["ecr"] == 2.0
    assert rows[0]["fantasypros_id"] == "1"


def test_parse_projections_ppr_points():
    bundle = {
        "pages": {
            "QB": {
                "players": [
                    {
                        "fpid": 9,
                        "name": "Josh Allen",
                        "position_id": "QB",
                        "stats": {"points": 300, "points_ppr": 372.3},
                    }
                ]
            }
        }
    }
    rows = parse_projections(bundle)
    assert len(rows) == 1
    assert rows[0]["season_points"] == 372.3


def test_build_overlay_empty_without_fp_api_rows(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    ov = build_overlay(conn, draft_id, recommend=[{"player_id": "1001", "name": "X", "marginal": 1}])
    assert ov["role"] == "overlay"
    assert ov["available"] is False
    assert "does not change TAKE" in ov["disclaimer"].lower() or "Does not change TAKE" in ov["disclaimer"]
