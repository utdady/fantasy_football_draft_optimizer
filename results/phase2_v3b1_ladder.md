# P2.2C V3-B.1 ladder (B.1−D)

- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- construction: `crosspos_empty_need_nextbest_v1`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

V3-B.1: identical frozen V3-A values; B.1 = D + M_B1 = M_D − a* (crosspos_empty_need_nextbest_v1). Primary contrast B.1−D. No map retune.

**Do not invent B.1.1 after seeing these numbers. Success requires mean, median, WR, and p10 — not mean alone. Observed: all 60 pick sequences identical to D (n_zero=60).**

Flags: b1_minus_d_identical — scores change but picks match D on all boards; proxy inert (do not invent B.1.1)

## Full starter PPR

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1906.90 | 1886.54 |
| `adp_v3b1` | 1906.90 | 1886.54 |

### B.1−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Ex-DST

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1796.04 | 1776.54 |
| `adp_v3b1` | 1796.04 | 1776.54 |

### B.1−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Ex-DST + TE

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1592.81 | 1586.89 |
| `adp_v3b1` | 1592.81 | 1586.89 |

### B.1−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +0.00 | +0.00 | 0% | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0/60 |

## Decision rule (frozen)

| Outcome | Meaning |
| --- | --- |
| B.1−D ↑ mean/median/WR and p10 OK | Cross-pos OC construction supported (n=1) |
| Mean ↑, p10 worse | Tradeoff failure — do not invent B.1.1 |
| B.1−D ≈ 0 | Cross-pos proxy insufficient |
| B.1−D ≤ 0 | Hypothesis fails cleanly |

- UI: `marginal`
- map: frozen
