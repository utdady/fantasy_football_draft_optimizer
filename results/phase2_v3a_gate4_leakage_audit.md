# V3-A Gate 4 — leakage audit

**Status:** audit of the V3-A.0 plan against Phase-2 leakage rules.
**No V3 recommend() code yet** — this gate freezes what implementation must prove.

**Parents:** [`V3A_CALIBRATION_DESIGN.md`](V3A_CALIBRATION_DESIGN.md) ·
Gate 3 [`phase2_v3a_gate3_calibration_freeze.md`](phase2_v3a_gate3_calibration_freeze.md)

---

## Temporal boundary (repeated)

> **Training:** 2021–2023  
> **Evaluation:** 2024  
> **No 2024 outcome information may influence calibration, hyperparameters,
> binning, exclusions, or transformation selection.**

| Artifact | as_of / bound | vs 2024 snapshot `2024-09-01` |
| --- | --- | --- |
| FFC ADP 2021 | `2021-09-01` | before |
| FFC ADP 2022 | `2022-09-04` | before |
| FFC ADP 2023 | `2023-09-01` | before |
| Train outcomes | end of REG season Y | used **only** for fit on Y∈{2021,2022,2023} |
| Eval ADP | FFC window end `2024-09-01` | decision-time |
| Eval outcomes | 2024 REG | **scoring only** — never in fit |

**Required inequality for the calibration artifact (when written):**

```text
max(train ADP as_of) = 2023-09-01  <  2024-09-01 = eval snapshot as_of
```

Train **outcomes** are after each year’s ADP as_of (by construction) but are
**not** allowed into the 2024 recommendation path — only into the frozen map
fit offline.

---

## Provenance requirements (implementation must embed)

Every training observation in the fit artifact JSON must carry:

- `train_year`
- `ffc_player_id` / `player_id` / `gsis_id` (as available)
- `adp`, `position`
- `actual_ppr` + `outcome_state` ∈ {observed_points, observed_zero}
- `adp_as_of` (Gate 1 end_date)
- `source`: FFC + nflverse_computed

---

## Recommend-path dependency ban

When `adp_v3a` is implemented, the following must hold:

| Path | Allowed | Forbidden |
| --- | --- | --- |
| Materialize calibrated `season_points` | frozen map + 2024 ADP | 2024 actual PPR |
| `recommend()` / marginal | calibrated projections table | `eval_outcomes*` |
| Draft / CPU | same as P2.2C | outcome DB |
| Scoring Δ | outcomes after draft | feeding back into map |

**Proof (for the implementation PR):**

1. Static: `adp_v3a` / materialize modules must not import outcome loaders used for scoring in the recommend path.
2. Runtime: unit test or audit that opening only the draft DB (no eval outcomes) still produces recommendations.
3. Artifact header must state `calibration_as_of = 2023-09-01` (max train ADP as_of) and `eval_snapshot_as_of = 2024-09-01`.

---

## Checklist

- [x] Train ADP as_of dates all &lt; 2024-09-01 (Gate 1)
- [x] Train/eval year split documented
- [x] Recommend-path outcome-DB ban specified
- [ ] Fit artifact not yet written (next: implement fit **without** reading 2024 outcomes)
- [ ] Recommend() code not yet present — Gate 4 design **pass**; code audit deferred to implementation PR

**Gate 4 design verdict:** **pass** (constraints frozen).  
**Gate 4 code verdict:** **pending** (no V3-A code yet — correct).

**Next:** Implementation PR for V3-A.0 fit + materialize + `adp_v3a` + same-board D−B / D−C — still no UI change.
