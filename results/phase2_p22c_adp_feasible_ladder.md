# P2.2C ADP → ADP-feasible → structural ladder

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

Decomposition of structural vs pure ADP into feasibility gain (adp_feasible − adp_baseline) and valuation gain (adp_structural − adp_feasible) under ppr_eval_v1_2024. Modeled opponents; n=1 season; not a real-league reconstruction.

**Load-bearing comparison is valuation_gain (C−B), not total_vs_baseline (C−A). V3 still blocked. UI stays marginal.**

Flags: valuation_gain_strong — structural >> feasible on full metric

## DST fill rates

| Strategy | DST fill rate |
| --- | ---: |
| `adp_baseline` | 35% |
| `adp_feasible` | 100% |
| `adp_structural` | 100% |

## Full starter PPR

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | +53.70 | +49.20 | 60% |
| `adp_structural` | +130.18 | +112.20 | 80% |

### Causal split

| Gain | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Feasibility (B−A) | +53.70 | +49.20 | 60% | -1.3 | +146.7 |
| **Valuation (C−B)** | **+76.47** | **+54.14** | **67%** | -80.7 | +276.4 |

## Ex-DST

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | -13.76 | +0.00 | 20% |
| `adp_structural` | +54.01 | +22.69 | 60% |

### Causal split

| Gain | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Feasibility (B−A) | -13.76 | +0.00 | 20% | -109.5 | +51.9 |
| **Valuation (C−B)** | **+67.77** | **+42.24** | **65%** | -83.6 | +252.9 |

## Ex-DST + TE

### Mean Δ vs `adp_baseline`

| Strategy | mean Δ vs baseline | median Δ | win rate |
| --- | ---: | ---: | ---: |
| `adp_baseline` | +0.00 | +0.00 | 0% |
| `adp_feasible` | -34.32 | +0.00 | 0% |
| `adp_structural` | +7.01 | -11.70 | 47% |

### Causal split

| Gain | Mean | Median | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Feasibility (B−A) | -34.32 | +0.00 | 0% | -114.0 | +0.0 |
| **Valuation (C−B)** | **+41.33** | **+28.31** | **57%** | -119.0 | +212.3 |

## Status

- Phase 2: 🟢 ladder complete — first evidence of valuation gain beyond feasibility (n=1 season; modeled opponents)
- V3: 🔴 still blocked (need replication / tighter bounds before algorithm work)
- UI: `marginal`
