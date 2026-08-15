# P2.2C Phase-2 closeout (symmetry + fork prediction error)

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**

Phase-2 closeout: best-10 fork symmetry vs worst-10, plus fork prediction-error table (curve / marginal / actual). Chooses V3 branch evidence — does not implement V3.

**Core thesis remains preliminary. UI stays marginal. adp_structural has no explicit replacement.**

## 1. Best-10 vs worst-10 fork symmetry

| Metric | Worst-10 | Best-10 |
| --- | ---: | ---: |
| skill-over-QB tag | 6 | 5 |
| mid-TE tag | 4 | 1 |
| C wins fork actual | 1 | 6 |
| C loses fork actual | 9 | 4 |

- Worst C positions: `{'TE': 4, 'WR': 2, 'RB': 4}`
- Best C positions: `{'WR': 4, 'RB': 3, 'TE': 1, 'QB': 2}`
- Worst B positions: `{'RB': 3, 'QB': 5, 'WR': 2}`
- Best B positions: `{'QB': 6, 'RB': 1, 'WR': 3}`
- Worst fork rounds: `{'5': 1, '6': 2, '7': 4, '8': 3}`
- Best fork rounds: `{'5': 2, '6': 6, '7': 1, '8': 1}`

**Symmetry verdict:** symmetric — skill-over-QB appears in both tails (high variance)

**Decision-tree branch (symmetry):** `do_not_fix_te_qb_specifically`

## 2. Worst-10 fork prediction-error table

At first fork: curve = ADP-curve value; marginal = C's raw lineup lift; `pred_error = actual − curve`. `model_marginal_adv` = C.marginal − (B pick's marginal under C's ranking, if shown).

| Slot/seed | R | C pick | C curve | C marg | C act | C err | B pick | B curve | B marg@C | B act | B err | modelΔ | actualΔ | empty? |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1/46 | 7 | Kyle Pitts Sr. (TE) | 209.6 | +209.6 | 131.2 | -78.4 | Nick Chubb (RB) | 224.9 | — | 63.3 | -161.6 | — | +67.9 | Y |
| 8/44 | 8 | Dallas Goedert (TE) | 145.7 | +145.7 | 103.6 | -42.1 | Najee Harris (RB) | 220.8 | +0.0 | 204.6 | -16.2 | +145.7 | -101.0 | Y |
| 10/43 | 6 | Christian Kirk (WR) | 243.2 | +243.2 | 70.9 | -172.3 | Anthony Richardson Sr. (QB) | 244.0 | — | 163.4 | -80.7 | — | -92.5 | N |
| 6/42 | 7 | Zamir White (RB) | 219.4 | +219.4 | 29.3 | -190.1 | Jayden Reed (WR) | 224.7 | — | 197.0 | -27.7 | — | -167.7 | N |
| 2/45 | 8 | David Njoku (TE) | 154.3 | +154.3 | 148.5 | -5.8 | Kyler Murray (QB) | 203.2 | +0.0 | 297.2 | +94.1 | +154.3 | -148.7 | Y |
| 11/43 | 5 | David Montgomery (RB) | 245.2 | +245.2 | 221.7 | -23.5 | Lamar Jackson (QB) | 265.5 | — | 430.4 | +164.8 | — | -208.7 | N |
| 5/44 | 7 | Nick Chubb (RB) | 224.9 | +224.9 | 63.3 | -161.6 | Rashee Rice (WR) | 226.4 | — | 64.9 | -161.5 | — | -1.6 | N |
| 2/46 | 8 | Jake Ferguson (TE) | 177.5 | +177.5 | 104.4 | -73.1 | Austin Ekeler (RB) | 179.9 | +0.0 | 132.3 | -47.6 | +177.5 | -27.9 | Y |
| 5/45 | 6 | George Pickens (WR) | 235.0 | +235.0 | 164.4 | -70.6 | Joe Burrow (QB) | 235.2 | — | 372.8 | +137.6 | — | -208.4 | N |
| 11/46 | 7 | Zack Moss (RB) | 206.5 | +206.5 | 81.9 | -124.6 | Jordan Love (QB) | 208.8 | — | 233.9 | +25.0 | — | -152.0 | N |

### Prediction-error summary (worst forks)

- mean pred_error C=-94.2, B=-7.4 (actual − curve); model preferred C but actual preferred B in 3/10 forks; C pick filled an empty starter slot in 4/10 forks
- mean pred_error C: -94.2
- mean pred_error B: -7.4
- pred_error by pos (C picks): `{'RB': {'n': 4, 'mean_pred_error': -124.9254, 'median_pred_error': -143.0704}, 'WR': {'n': 2, 'mean_pred_error': -121.484, 'median_pred_error': -121.484}, 'TE': {'n': 4, 'mean_pred_error': -49.8487, 'median_pred_error': -57.6061}}`
- pred_error by pos (B picks): `{'QB': {'n': 5, 'mean_pred_error': 68.1801, 'median_pred_error': 94.0836}, 'RB': {'n': 3, 'mean_pred_error': -75.1009, 'median_pred_error': -47.5883}, 'WR': {'n': 2, 'mean_pred_error': -94.5947, 'median_pred_error': -94.5947}}`

**Error-table branch:** `V3-A_candidate_projection_calibration`

## Combined closeout read

### Symmetry

- skill-over-QB: worst **6** vs best **5** → **symmetric — skill-over-QB appears in both tails (high variance)**
- Mid-draft skill-vs-QB forks appear in **both** tails; what differs is whether the actuals paid off (worst C wins fork 1/10; best 6/10).
- Therefore: **do not design V3 as “stop taking TE/skill over QB.”**

### Prediction error (worst forks)

- Mean `actual − curve`: C picks **-94.2**, B picks **-7.4**.
- C’s chosen skill players are systematically **over-projected** on the ADP curve relative to 2024 actuals; B’s QBs in this set are often **under-projected** (positive pred_error).
- Empty-slot fills by C: 4/10 (marginal-construction still a secondary candidate, not ruled out).

**Provisional V3 pointer:** `V3-A_candidate_projection_calibration` (projection/calibration), with symmetry saying the TE/QB *choice type* is high-variance rather than a one-sided positional bug.

```text
Best-10 symmetry → do_not_fix_te_qb_specifically
Fork error table → V3-A candidate (projection calibration)
                 → V3-B still open if empty-slot marginal dominates
```

Neither branch implements V3 until explicitly designed from this evidence.

## Status

> **Core thesis: 🟡 preliminary empirical support**  
> **External validity: 🔴**  
> **V3: 🟡 design justified / 🔴 implementation pending closeout interpretation**  
> **UI: `marginal`**  
> **`evaluable=0`**
