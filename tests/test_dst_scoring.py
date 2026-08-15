"""Unit tests for ppr_eval_v1_2024 DST scoring."""

from draftopt.phase2.dst_scoring import week_dst_points
from draftopt.phase2.scoring_contract import CONTRACT_ID


def test_contract_id_frozen():
    assert CONTRACT_ID == "ppr_eval_v1_2024"


def test_dst_week_shutout_low_yards():
    # 0 PA → +10; 50 YA → +5; 3 sacks → +3; 1 INT → +2
    pts = week_dst_points(
        points_allowed=0,
        yards_allowed=50,
        def_row={"def_sacks": 3, "def_interceptions": 1},
    )
    assert pts == 10 + 5 + 3 + 2


def test_dst_week_high_pa_penalty():
    pts = week_dst_points(
        points_allowed=40,
        yards_allowed=450,
        def_row={},
    )
    # PA 35-45 → -3; YA 450-499 → -5
    assert pts == -3 + -5
