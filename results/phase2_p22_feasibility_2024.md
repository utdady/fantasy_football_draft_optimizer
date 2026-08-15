# P2.2 feasibility spike — `2024-preseason-2024-09-01-ffc-pending`

**Stage:** A_feasibility (no draft replay; **evaluable=0**)

- validation_status: `source_validation`
- validation_reason: `adp_league_size_mismatch`
- all reasons: `adp_league_size_mismatch, historical_projection_missing`

## Gates

| gate | result |
| --- | --- |
| ffc_adp_provenance | **fail** |
| player_mapping | **pass** |
| outcome_coverage | **pass** (99.4% on full run; see body) |
| historical_projection | **fail** |
| evaluable | **fail** |

## FFC ADP provenance

- requested: year=2024 teams=10
- meta teams/type: 12 / PPR
- draft window: 2024-08-31 → 2024-09-01
- as_of (end_date): `2024-09-01`
- interpretation: FFC meta.end_date (upper bound of draft window in meta); ADP is an aggregate over [start_date, end_date], not a single pick clock.
- players: 205
- gate: **fail** reason=`adp_league_size_mismatch`

## Player mapping (FFC → canonical → gsis)

| Metric | Result |
| --- | ---: |
| FFC players | 205 |
| Automatically mapped | 179 |
| Manually resolved | 0 |
| Unresolved | 26 |
| Coverage | 87.3% |
| Name-only joins | **0** |

## Outcomes (nflverse weekly → computed PPR)

- weekly rows: 18112 (retained in `eval_outcomes_weekly`)
- season players: 1996 (`eval_outcomes`, source=`nflverse_computed`)
- mapped-with-gsis outcome coverage: 178/179 (99.4%) — from full spike run
- note: re-runs with `--skip-outcomes` leave DB totals intact

## Next

- Do **not** set `evaluable=1` until historical projections (Gate 4) pass.
- If FFC provenance failed, try another ADP source — treat fail as success.
