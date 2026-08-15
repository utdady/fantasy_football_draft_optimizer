# P2.2C actual-PPR Δ (adp_structural − adp_baseline)

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- slots: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] · n_sims: 5 · seed0: 42
- pairs: 60

**Claim scope:** On the 2024 FFC 12-team preseason snapshot, under the specified simulated draft environment (noisy_adp opponents), ADP-structural produced the reported difference in realized starter PPR vs ADP baseline. This is not a reconstruction of a real 2024 fantasy league.

## Headline

| Metric | Value |
| --- | ---: |
| Mean Δ starter PPR | 130.177 |
| Median Δ starter PPR | 112.2 |
| Stdev Δ | 150.7085 |
| Structural win rate | 0.8 (48-12-0) |

## By draft slot (mean Δ)

| Slot | n | mean Δ | median Δ | win rate |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | +78.86 | +139.10 | 80% |
| 2 | 5 | +102.20 | +87.98 | 80% |
| 3 | 5 | +292.27 | +315.90 | 100% |
| 4 | 5 | +157.29 | +168.68 | 100% |
| 5 | 5 | +123.86 | +139.88 | 80% |
| 6 | 5 | +105.20 | +81.60 | 80% |
| 7 | 5 | +261.74 | +347.26 | 80% |
| 8 | 5 | +95.50 | +106.40 | 80% |
| 9 | 5 | +164.79 | +131.50 | 100% |
| 10 | 5 | +13.49 | +69.94 | 60% |
| 11 | 5 | +72.47 | +28.08 | 60% |
| 12 | 5 | +94.46 | +109.20 | 60% |

## Mean Δ starter points by position (structural − baseline)

| Pos | mean Δ |
| --- | ---: |
| QB | -7.24 |
| RB | -25.11 |
| WR | +39.37 |
| TE | +47.00 |
| DST | +76.17 |

## Mean Δ by draft-round band of starters

| Band | mean Δ |
| --- | ---: |
| r1-5 | +42.09 |
| r6-10 | +61.52 |
| r11-15 | +26.57 |

**Next:** Inspect Δ. n=1 season / modeled opponents. Do not promote evaluable or start V3 from this alone. Optional: mapping-sensitivity rematch.
