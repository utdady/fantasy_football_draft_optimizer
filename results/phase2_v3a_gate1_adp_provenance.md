# V3-A Gate 1 — historical ADP provenance (2021–2023)

- created: `2026-08-15T12:00:25Z`
- market: FFC 12-team PPR
- verdict: **pass**
- dating gate: **pass**
- mapping gate (≥95%): **pass**

Prerequisite for V3-A.0. No calibration fit. No 2024 outcome peek.

## Per-year provenance

| Year | Dating | as_of | Window | Teams | Players | Mapped | Coverage | Raw |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2021 | pass | `2021-09-01` | 2021-08-31 → 2021-09-01 | 12 | 211 | 209 | 99.1% | `C:\Users\addyb\fantasy_football_draft_optimizer\data\raw\ffc_adp_ppr_12tm_2021.json` |
| 2022 | pass | `2022-09-04` | 2022-09-03 → 2022-09-04 | 12 | 157 | 155 | 98.7% | `C:\Users\addyb\fantasy_football_draft_optimizer\data\raw\ffc_adp_ppr_12tm_2022.json` |
| 2023 | pass | `2023-09-01` | 2023-08-30 → 2023-09-01 | 12 | 202 | 198 | 98.0% | `C:\Users\addyb\fantasy_football_draft_optimizer\data\raw\ffc_adp_ppr_12tm_2023.json` |

## Checklist

- [x] Concrete preseason/as_of date per year
- [x] Documented source (FFC API / attribution)
- [x] Player identity mapping (≥95% to gsis/crosswalk)
- [x] No post-draft info in ADP payload (window ends at meta.end_date)
- [x] Same market definition: FFC 12-team PPR (matches 2024 eval market size)

**Next:** Gate 2 — historical outcomes for train years under same PPR rules

If dating fails: **stop**. Do not substitute ECR or undated ADP.
