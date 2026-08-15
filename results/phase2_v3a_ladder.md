# P2.2C V3-A ladder (A/B/C/D)

- structural snapshot: `2024-preseason-2024-09-01-ffc12`
- v3a snapshot: `2024-preseason-2024-09-01-ffc12-v3a`
- curve: `adp_emp_pos_v1_train_2021_2023`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

Same-board A/B/C/D under ppr_eval_v1_2024. D uses calibrated values (train 2021–2023 map); construction identical to structural. Load-bearing: D−B and D−C. Do not retune map from these results.

A/B/C run on draftopt_p22c.db; D on draftopt_p22c_v3a.db (identical ADP, different season_points). UI stays marginal.

Flags: mean_up_left_tail_worse — tradeoff failure mode (do not treat as clean V3-A support)

## DST fill rates

| Strategy | DST fill rate |
| --- | ---: |
| `adp_baseline` | 35% |
| `adp_feasible` | 100% |
| `adp_structural` | 100% |
| `adp_v3a` | 100% |

## Full starter PPR

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | +53.70 | +49.20 | 60% |
| `adp_structural` | +130.18 | +112.20 | 80% |
| `adp_v3a` | +152.26 | +146.61 | 78% |

### Causal / calibration deltas

| Contrast | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| C−B (structural valuation) | +76.47 | +54.14 | 67% | -80.7 | +276.4 |
| **D−B (calibration vs feasible)** | **+98.56** | **+90.73** | **73%** | -182.7 | +298.4 |
| **D−C (calibration vs structural)** | **+22.09** | **+29.96** | **55%** | -268.4 | +259.4 |

Left tail D−C: min=-465.04, p10=-268.432, negative=27/60

## Ex-DST

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | -13.76 | +0.00 | 20% |
| `adp_structural` | +54.01 | +22.69 | 60% |
| `adp_v3a` | +75.83 | +75.69 | 67% |

### Causal / calibration deltas

| Contrast | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| C−B (structural valuation) | +67.77 | +42.24 | 65% | -83.6 | +252.9 |
| **D−B (calibration vs feasible)** | **+89.59** | **+87.38** | **70%** | -213.9 | +300.4 |
| **D−C (calibration vs structural)** | **+21.82** | **+29.96** | **55%** | -268.4 | +259.4 |

Left tail D−C: min=-465.04, p10=-268.432, negative=27/60

## Ex-DST + TE

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | -34.32 | +0.00 | 0% |
| `adp_structural` | +7.01 | -11.70 | 47% |
| `adp_v3a` | -17.40 | -27.99 | 43% |

### Causal / calibration deltas

| Contrast | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| C−B (structural valuation) | +41.33 | +28.31 | 57% | -119.0 | +212.3 |
| **D−B (calibration vs feasible)** | **+16.92** | **+17.38** | **53%** | -270.3 | +268.4 |
| **D−C (calibration vs structural)** | **-24.41** | **-10.70** | **48%** | -322.2 | +237.9 |

Left tail D−C: min=-559.28, p10=-322.224, negative=31/60

## Decision rule (do not retune map)

| Outcome | Meaning |
| --- | --- |
| D−C > 0 and left tail improves | Calibration hypothesis supported (n=1) |
| D−C ≤ 0 | V3-A fails cleanly → revisit construction |
| Only one pocket | Localized hypothesis only |
| Mean ↑, left tail worse | Tradeoff failure mode |

- UI: `marginal`
- evaluable: 0
