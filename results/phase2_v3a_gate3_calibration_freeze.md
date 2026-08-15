# V3-A Gate 3 — calibration definition freeze

**Status:** frozen **before** any V3-A fit or 2024 calibration evaluation.

**Parents:** [`V3A_CALIBRATION_DESIGN.md`](V3A_CALIBRATION_DESIGN.md) ·
Gate 1 [`phase2_v3a_gate1_adp_provenance.md`](phase2_v3a_gate1_adp_provenance.md) ·
Gate 2 [`phase2_v3a_gate2_train_outcomes.md`](phase2_v3a_gate2_train_outcomes.md)

**Temporal boundary (do not blur):**

> **Training:** 2021–2023  
> **Evaluation:** 2024  
> **No 2024 outcome information may influence calibration, hyperparameters,
> binning, exclusions, or transformation selection.**

---

## Frozen transform: V3-A.0

| Field | Frozen value |
| --- | --- |
| `curve_id` | `adp_emp_pos_v1_train_2021_2023` |
| Train seasons | **2021, 2022, 2023** |
| Market | FFC 12-team PPR ADP |
| Train as_of | Gate 1 `meta.end_date` per year |
| Eval apply | 2024 FFC ADP at snapshot `2024-preseason-2024-09-01-ffc12` |
| Positions fit separately | QB, RB, WR, TE, DST (K omitted if absent from pool) |
| Unit of observation | one (season, player) with ADP + observed_* actual PPR |
| Exclude from fit | `missing_identity`, `missing_weeks` (never coerce to 0) |

### Binning

- Within each position, bin by ADP using **fixed edges**:
  `[1, 12, 24, 36, 48, 60, 84, 108, 132, 156, 180, +∞)`
- Bin statistic: **mean** actual PPR of train pairs in that bin
- Require **min_n = 5** observations per bin; if fewer, **merge with the
  nearest neighboring bin toward the middle of the ADP range** until
  `min_n` is met (or the position has a single pooled bin)

### Monotone fit

- After bin means: apply **isotonic regression** (non-decreasing in −ADP,
  i.e. value must not increase as ADP worsens)
- Interpolate for ADP between bin centers by **linear interpolation** on the
  isotonic curve; clamp outside to end values

### Rookies / new players / missing historical ADP

- **Eval 2024 players** are scored only from **2024 ADP** through the frozen map
- No special rookie multiplier
- If a 2024 player has ADP but the position map is empty (should not happen):
  fall back to **global (all-position) isotonic map** fit under the same rules
- Players with **missing ADP** at apply time: **no calibrated value** (same as
  structural curve’s None) — not drafted via projection path

### Extrapolation

- ADP &lt; 1 → value at ADP=1
- ADP ≥ last bin edge → last isotonic value (floor)

### Aggregation across train years

- Pool all (year, player) pairs from 2021–2023 **before** binning
- No year weights; no leave-one-year-out in V3-A.0 (that is a later robustness check)

---

## Explicitly not tunable after this freeze

Do **not** change bins, `min_n`, merge rule, isotonic direction, fallback, or
train years after seeing any 2024 D−B / D−C number.

A new `curve_id` is required for any change.

---

## Checklist

- [x] ADP bins/curve edges frozen
- [x] Position handling frozen
- [x] Sample aggregation frozen (pool years)
- [x] Minimum sample rules frozen (`min_n=5` + merge)
- [x] Rookies / new players treatment frozen
- [x] Extrapolation frozen
- [x] Missing historical / missing ADP treatment frozen

**Next:** Gate 4 — leakage audit (`calibration_as_of` &lt; 2024 snapshot; recommend() has zero outcome-DB dependency)
