# P2.2C Branch A ladder (A−D)

- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- construction: `crosspos_empty_need_marginal_v1`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

Branch A: identical frozen V3-A values; A = D + M_A = M_D(p) − M_D(q*) (crosspos_empty_need_marginal_v1). Primary contrast A−D. No map retune.

**Do not invent A.1. Success needs mean/median/WR/p10 and pick changes. 0/60 pick changes → open Branch B design.**

Flags: a_policy_inert — 0/60 boards with pick change; stop A; open Branch B design

## Pick-change (first-class)

- boards with ≥1 changed pick: **0/60**
- boards identical to D: 60
- total changed picks: 0
- mean changed picks/board: 0.0
- first divergence round hist: `{}`
- first divergence D→A pos: `{}`

## Full starter PPR

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1906.90 | 1886.54 |
| `adp_v3ba` | 1906.90 | 1886.54 |

### A−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Ex-DST

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1796.04 | 1776.54 |
| `adp_v3ba` | 1796.04 | 1776.54 |

### A−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Ex-DST + TE

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1592.81 | 1586.89 |
| `adp_v3ba` | 1592.81 | 1586.89 |

### A−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Decision rule (frozen)

| Outcome | Next |
| --- | --- |
| 0/60 pick changes | Stop A; open Branch B design |
| Pick changes but A−D ≤ 0 | Freeze A; no tune; Branch B design |
| A−D positive | Mechanism audit first; no A.1 |

- UI: `marginal`
- map: frozen
