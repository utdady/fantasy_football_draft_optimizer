# P2.2C Branch B ladder (B−D)

- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- construction: `onestep_continuation_marginal_v1`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

Branch B: identical frozen V3-A values; M_B = M_D(p|R) + C(R∪{p}) (onestep_continuation_marginal_v1). Primary contrast B−D. Gates P∧N required.

**Do not invent B.1.1 or lengthen horizon. Divergence is evidence the mechanism is active, not that it is correct. Positive B−D still requires mandatory where/why audit.**

Flags: b_active_but_b_minus_d_nonpositive — falsified; freeze; no tune; mandatory light where/why still useful

## Pick-change (first-class)

- boards with ≥1 changed pick: **60/60**
- boards identical to D: 0
- total changed picks: 703
- mean changed picks/board: 11.7167
- first divergence round hist: `{1: 60}`
- first divergence D→B pos: `{'QB→WR': 60}`

## Full starter PPR

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1906.90 | 1886.54 |
| `adp_v3bb` | 1849.40 | 1823.86 |

### B−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -57.51 | -53.06 | 37% | -287.84 | -228.24 | +42.04 | +191.95 | -549.46 | +530.48 | 38/60 |

## Ex-DST

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1796.04 | 1776.54 |
| `adp_v3bb` | 1783.76 | 1769.37 |

### B−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -12.27 | -22.03 | 45% | -254.67 | -160.78 | +88.09 | +229.51 | -498.46 | +640.48 | 33/60 |

## Ex-DST + TE

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1592.81 | 1586.89 |
| `adp_v3bb` | 1590.52 | 1596.47 |

### B−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -2.29 | -13.28 | 47% | -231.64 | -122.01 | +108.14 | +228.61 | -524.56 | +508.98 | 32/60 |

## Decision rule (frozen)

| Outcome | Next |
| --- | --- |
| 0/60 pick changes | Policy-inert; reject operationalization |
| Pick changes but B−D ≤ 0 | Active but falsified; freeze; no tune |
| Pick changes + B−D > 0 | Mandatory where/why audit before OC claim |

- UI: `marginal`
- map: frozen
