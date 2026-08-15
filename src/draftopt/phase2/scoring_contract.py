"""Frozen P2.2C scoring contract: ppr_eval_v1_2024.

Immutable for the 2024 FFC12 ADP-structural experiment. Changing DST tiers,
FLEX rules, or missing-outcome policy requires ppr_eval_v2_* — do not edit
these constants in place after outcome attach.
"""

from __future__ import annotations

CONTRACT_ID = "ppr_eval_v1_2024"
OUTCOME_SOURCE = "nflverse_computed"
OUTCOME_SEASON = 2024
DECISION_SNAPSHOT_ID = "2024-preseason-2024-09-01-ffc12"

# Draft environment (matches smoke_p22c / materialize)
N_TEAMS = 12
N_ROUNDS = 15
ROSTER_PRESET = "league_default"
SEASON_TYPE = "REG"  # regular season only

# Outcome identity states (evaluator invariant — never COALESCE missing → 0)
OUTCOME_STATES = (
    "observed_points",  # valid stats → PPR > 0
    "observed_zero",  # in identity space; legitimate 0 PPR
    "missing_identity",  # cannot establish in nflverse — NOT 0
    "missing_weeks",  # identity exists; incomplete REG window — NOT 0
    "not_draftable",  # outside evaluated decision pool
)

# ESPN-like skill PPR is implemented in ppr_scoring.week_ppr_points.
# DST (ESPN-like defaults) — see dst_scoring.week_dst_points.
DST_SACK = 1.0
DST_INT = 2.0
DST_FR = 2.0
DST_TD = 6.0
DST_SAFETY = 2.0
DST_BLOCK = 2.0

# Points allowed → fantasy points (inclusive ranges)
DST_PA_TIERS: tuple[tuple[int | None, int | None, float], ...] = (
    (None, 0, 10.0),
    (1, 6, 7.0),
    (7, 13, 4.0),
    (14, 17, 1.0),
    (18, 27, 0.0),
    (28, 34, -1.0),
    (35, 45, -3.0),
    (46, None, -4.0),
)

# Yards allowed → fantasy points
DST_YA_TIERS: tuple[tuple[int | None, int | None, float], ...] = (
    (None, 99, 5.0),
    (100, 199, 3.0),
    (200, 299, 2.0),
    (300, 349, 0.0),
    (350, 399, -1.0),
    (400, 449, -3.0),
    (450, 499, -5.0),
    (500, None, -6.0),
)

# nflverse Rams abbreviation vs our dst:LAR canonical code
NFLVERSE_TEAM_ALIASES = {
    "LA": "LAR",
}
CANON_TO_NFLVERSE_TEAM = {
    "LAR": "LA",
}


def contract_meta() -> dict:
    return {
        "contract_id": CONTRACT_ID,
        "outcome_source": OUTCOME_SOURCE,
        "outcome_season": OUTCOME_SEASON,
        "decision_snapshot_id": DECISION_SNAPSHOT_ID,
        "n_teams": N_TEAMS,
        "n_rounds": N_ROUNDS,
        "roster_preset": ROSTER_PRESET,
        "season_type": SEASON_TYPE,
        "missing_policy": (
            "missing_identity / missing_weeks never score as 0; "
            "only observed_zero and observed_points enter eval_outcomes"
        ),
        "starter_scoring": (
            "Same greedy FLEX-aware lineup_ev as production; bench excluded from "
            "headline Δ (future commit). IR not drafted."
        ),
        "frozen": True,
    }
