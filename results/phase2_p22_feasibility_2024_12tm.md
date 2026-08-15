# P2.2 feasibility spike — `2024-preseason-2024-09-01-ffc-pending`

**Stage:** A_feasibility (no draft replay; **evaluable=0**)

- validation_status: `source_validation`
- validation_reason: `historical_projection_missing`
- all reasons: `historical_projection_missing`

## Gates

| gate | result |
| --- | --- |
| ffc_adp_provenance | **pass** |
| player_mapping | **pass** |
| outcome_coverage | **skip** |
| historical_projection | **fail** |
| evaluable | **fail** |

## FFC ADP provenance

- requested: year=2024 teams=12
- meta teams/type: 12 / PPR
- draft window: 2024-08-31 → 2024-09-01
- as_of (end_date): `2024-09-01`
- interpretation: FFC meta.end_date (upper bound of draft window in meta); ADP is an aggregate over [start_date, end_date], not a single pick clock.
- players: 205
- gate: **pass** reason=`None`

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

- skipped

## Next

- Do **not** set `evaluable=1` until historical projections (Gate 4) pass.
- If FFC provenance failed, try another ADP source — treat fail as success.
