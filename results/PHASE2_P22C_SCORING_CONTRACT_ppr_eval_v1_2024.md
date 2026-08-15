# Scoring contract `ppr_eval_v1_2024`

**Status:** frozen for P2.2C 2024 FFC12 ADP-structural evaluation.  
**Code:** `src/draftopt/phase2/scoring_contract.py`

Do not edit constants in place after outcome attach. Rule changes → `ppr_eval_v2_*`.

---

## Draft environment

| Field | Value |
| --- | --- |
| Decision snapshot | `2024-preseason-2024-09-01-ffc12` |
| League size | 12 |
| Rounds | 15 |
| Roster preset | `league_default` (K=0 drafted; DST=1) |
| Season window | NFL **REG** weeks only |
| Decision market | FFC ADP (not ESPN) |
| Value signal | `adp_linear_v1_2024_ffc12` (optimizer only) |

## Offense / K PPR

Computed from nflverse weekly box-score counting stats via
`ppr_scoring.week_ppr_points` (not nflverse `fantasy_points_ppr`).

Season total = sum of REG week scores.

## DST (team entity `dst:{TEAM}`)

ESPN-like defaults in `dst_scoring.week_dst_points`:

| Event | Points |
| --- | ---: |
| Sack | 1 |
| INT | 2 |
| Fumble recovery (opp) | 2 |
| Def/ST/FR TD | 6 |
| Safety | 2 |
| Blocked FG/punt/PAT | 2 |
| Points allowed tiers | 10 … −4 (see code) |
| Yards allowed tiers | 5 … −6 (see code) |

Points allowed = opponent’s score from nflverse schedules.  
Yards allowed = opponent’s `passing_yards + rushing_yards` that week.  
Rams: nflverse `LA` ↔ canonical `LAR`.

## Outcome states (invariant)

| State | Score |
| --- | ---: |
| `observed_points` | PPR |
| `observed_zero` | **0** (in identity space; legitimate zero) |
| `missing_identity` | **NOT 0** — coverage failure / exclude |
| `missing_weeks` | **NOT 0** — coverage failure / exclude |
| `not_draftable` | N/A |

**Never** `COALESCE(missing, 0)` in Δ scoring (future commit).

`observed_zero` includes: on season roster but no weekly stat lines.

## Starter construction (for future Δ)

Same greedy FLEX-aware `lineup_ev` as production. Headline Δ uses **starters only**;
bench is recorded but not in the primary comparison.

## Leakage

Outcomes live only in the eval DB. `recommend()` / draft replay must not read them.

## `evaluable`

Outcome attach and coverage gate leave `evaluable=0`. Promotion is a later, explicit step.
