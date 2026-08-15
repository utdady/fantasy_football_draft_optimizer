# P2.2C V3-B ladder (E−D)

- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- construction: `replacement_nextbest_v1`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60

V3-B.0: identical frozen V3-A values; E = D + M_E = M_D − r* (replacement_nextbest_v1). Primary contrast E−D. No map retune.

**Do not invent E.1 after seeing these numbers. Success requires mean, median, WR, and p10 — not mean alone.**

Flags: e_minus_d_nonpositive — construction hypothesis fails cleanly

## Full starter PPR

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1906.90 | 1886.54 |
| `adp_v3b` | 1882.65 | 1885.33 |

### E−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -24.25 | -22.60 | 42% | -204.38 | -151.68 | +92.80 | +190.50 | -585.80 | +341.66 | 35/60 |

## Ex-DST

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1796.04 | 1776.54 |
| `adp_v3b` | 1772.52 | 1771.33 |

### E−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -23.52 | -21.95 | 43% | -204.38 | -146.57 | +92.80 | +190.50 | -585.80 | +341.66 | 34/60 |

## Ex-DST + TE

| Strategy | mean starter | median starter |
| --- | ---: | ---: |
| `adp_v3a` | 1592.81 | 1586.89 |
| `adp_v3b` | 1475.97 | 1484.89 |

### E−D

| Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -116.84 | -143.25 | 27% | -343.96 | -256.32 | +7.36 | +132.98 | -744.20 | +502.20 | 44/60 |

## Decision rule (frozen)

| Outcome | Meaning |
| --- | --- |
| E−D ↑ mean/median/WR and p10 OK | Replacement-aware construction supported (n=1) |
| Mean ↑, p10 worse | Tradeoff failure — do not invent E.1 |
| E−D ≈ 0 | Simple replacement insufficient |
| E−D ≤ 0 | Hypothesis fails cleanly |

- UI: `marginal`
- map: frozen
