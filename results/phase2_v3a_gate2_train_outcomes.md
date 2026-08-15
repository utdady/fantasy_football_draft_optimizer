# V3-A Gate 2 — train-year outcomes (2021–2023)

- created: `2026-08-15T12:03:17Z`
- scoring rules: `ppr_train_v1_rules_match_ppr_eval_v1`
- source: `nflverse_computed`
- verdict: **pass**

Scoring rules match ppr_eval_v1_2024 (week_ppr_points + DST tiers). Not the 2024 eval contract row. No calibration fit. No 2024 train use.

## Coverage

| Year | FFC | Mapped | Observed | Obs/mapped | Train pairs | missing_id | missing_weeks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | 211 | 209 | 209 | 100.0% | 209 | 0 | 0 |
| 2022 | 157 | 155 | 155 | 100.0% | 155 | 0 | 0 |
| 2023 | 202 | 198 | 198 | 100.0% | 198 | 0 | 0 |

## Checklist

- [x] Actual PPR via same scoring functions as eval contract
- [x] REG weeks only
- [x] Offense + DST identity handling
- [x] missing ≠ zero
- [x] Coverage report (≥90% observed among mapped)

**Next:** Gate 3 — freeze calibration definition (bins, mins, rookies) before any 2024 calibration peek
