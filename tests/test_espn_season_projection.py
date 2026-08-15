"""ESPN season projection must prefer config SEASON over prior-year blocks."""

from draftopt.sources.espn import _season_projection, parse


def test_season_projection_prefers_configured_year():
    stats = [
        {
            "seasonId": 2025,
            "scoringPeriodId": 0,
            "statSourceId": 1,
            "statSplitTypeId": 0,
            "appliedTotal": 317.0,
        },
        {
            "seasonId": 2026,
            "scoringPeriodId": 0,
            "statSourceId": 1,
            "statSplitTypeId": 0,
            "appliedTotal": 365.0,
        },
    ]
    assert _season_projection(stats, season=2026) == 365.0
    assert _season_projection(stats, season=2025) == 317.0


def test_season_projection_falls_back_if_target_missing():
    stats = [
        {
            "seasonId": 2025,
            "scoringPeriodId": 0,
            "statSourceId": 1,
            "statSplitTypeId": 0,
            "appliedTotal": 200.0,
        },
    ]
    assert _season_projection(stats, season=2026) == 200.0


def test_parse_uses_target_season():
    payload = {
        "players": [
            {
                "player": {
                    "id": 1,
                    "fullName": "Test Player",
                    "defaultPositionId": 2,
                    "proTeamId": 8,
                    "ownership": {"averageDraftPosition": 1.5},
                    "draftRanksByRankType": {"PPR": {"rank": 1}},
                    "stats": [
                        {
                            "seasonId": 2025,
                            "scoringPeriodId": 0,
                            "statSourceId": 1,
                            "statSplitTypeId": 0,
                            "appliedTotal": 100.0,
                        },
                        {
                            "seasonId": 2026,
                            "scoringPeriodId": 0,
                            "statSourceId": 1,
                            "statSplitTypeId": 0,
                            "appliedTotal": 250.0,
                        },
                    ],
                }
            }
        ]
    }
    rows = parse(payload, season=2026)
    assert len(rows) == 1
    assert rows[0]["season_points"] == 250.0
    assert rows[0]["adp"] == 1.5
