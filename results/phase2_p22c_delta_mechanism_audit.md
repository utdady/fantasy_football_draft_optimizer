# P2.2C Δ mechanism audit

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60 (slots [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], n_sims=5, seed0=42)

Same deterministic seed0/slots/n_sims as phase2_p22c_actual_ppr_delta. Attribution drops starter points by position without re-drafting. Not V3. Not UI. n=1 season / modeled opponents.

Flags: dst_delta_mostly_slot_fill_not_identity, ex_dst_still_strongly_positive — skill-position construction signal plausible

## 1. Attribution ladder (structural − baseline)

| Metric | Mean Δ | Median Δ | Win rate | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full starter PPR | +130.18 | +112.20 | 80% | -50.6 | +317.8 |
| Ex-DST | +54.01 | +22.69 | 60% | -90.6 | +254.6 |
| Ex-DST + TE | +7.01 | -11.70 | 47% | -142.1 | +186.4 |

## 2. DST audit

- **DST fill rate:** baseline 21/60 (35%); structural 60/60 (100%)
- **Finding:** ADP baseline drafted DST in only 21/60 pairs; structural in 60/60. Most of the +76 mean DST starter Δ is empty-slot fill (baseline DST starter pts=0), not defense-identity skill among dual-DST drafts (n=21).
- unique baseline DSTs: 7 — Baltimore Defense, Buffalo Defense, Chicago Defense, Cleveland Defense, Dallas Defense, Detroit Defense, Pittsburgh Defense
- unique structural DSTs: 2 — Baltimore Defense, Pittsburgh Defense
- DST Δ mean/median: +12.57 / +16.00
- structural DST wins: 13/21 (baseline wins 3, ties 5)
- top-3 defenses' share of positive DST Δ sum: 1.0

### Top structural DST contributors (sum of positive Δ when structural DST scored more)

| DST | sum Δ | n pairs |
| --- | ---: | ---: |
| Baltimore Defense | +288.0 | 13 |

### Per-pair DST (sample head; full table in JSON)

| slot | seed | baseline | rnd | PPR | structural | rnd | PPR | Δ |
| ---: | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 43 | Baltimore Defense | 13 | 110.0 | Baltimore Defense | 10 | 110.0 | +0.0 |
| 2 | 43 | Baltimore Defense | 13 | 110.0 | Baltimore Defense | 10 | 110.0 | +0.0 |
| 2 | 44 | Cleveland Defense | 15 | 61.0 | Baltimore Defense | 10 | 110.0 | +49.0 |
| 3 | 43 | Detroit Defense | 14 | 105.0 | Baltimore Defense | 9 | 110.0 | +5.0 |
| 4 | 43 | Baltimore Defense | 13 | 110.0 | Baltimore Defense | 9 | 110.0 | +0.0 |
| 5 | 43 | Detroit Defense | 15 | 105.0 | Baltimore Defense | 9 | 110.0 | +5.0 |
| 5 | 46 | Pittsburgh Defense | 15 | 130.0 | Pittsburgh Defense | 15 | 130.0 | +0.0 |
| 6 | 43 | Cleveland Defense | 15 | 61.0 | Baltimore Defense | 9 | 110.0 | +49.0 |
| 6 | 45 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 7 | 43 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 8 | 43 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 9 | 43 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 9 | 46 | Buffalo Defense | 15 | 118.0 | Baltimore Defense | 9 | 110.0 | -8.0 |
| 10 | 42 | Chicago Defense | 13 | 94.0 | Baltimore Defense | 9 | 110.0 | +16.0 |
| 10 | 43 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 11 | 42 | Chicago Defense | 13 | 94.0 | Baltimore Defense | 9 | 110.0 | +16.0 |
| 11 | 43 | Baltimore Defense | 13 | 110.0 | Baltimore Defense | 9 | 110.0 | +0.0 |
| 11 | 46 | Buffalo Defense | 15 | 118.0 | Baltimore Defense | 9 | 110.0 | -8.0 |
| 12 | 42 | Chicago Defense | 13 | 94.0 | Baltimore Defense | 9 | 110.0 | +16.0 |
| 12 | 43 | Dallas Defense | 14 | 88.0 | Baltimore Defense | 9 | 110.0 | +22.0 |
| 12 | 46 | Buffalo Defense | 15 | 118.0 | Baltimore Defense | 9 | 110.0 | -8.0 |

## 3. Full Δ distribution

| min | p10 | p25 | median | p75 | p90 | max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -172.9 | -50.6 | +48.2 | +112.2 | +225.7 | +317.8 | +468.1 |

mean +130.18 · stdev 150.71 · wins 48/60 (80%)

### Histogram (bin width 50)

| Bin | count |
| --- | ---: |
| `[-100,-50)` | 2 |
| `[-200,-150)` | 4 |
| `[-50,0)` | 6 |
| `[0,50)` | 3 |
| `[100,150)` | 11 |
| `[150,200)` | 6 |
| `[200,250)` | 4 |
| `[250,300)` | 6 |
| `[300,350)` | 4 |
| `[400,450)` | 3 |
| `[450,500)` | 1 |
| `[50,100)` | 10 |

## Mean Δ by slot: full vs ex-DST

| Slot | full mean | ex-DST mean | full WR | ex-DST WR |
| ---: | ---: | ---: | ---: | ---: |
| 1 | +78.9 | -9.1 | 80% | 60% |
| 2 | +102.2 | +26.4 | 80% | 60% |
| 3 | +292.3 | +203.3 | 100% | 80% |
| 4 | +157.3 | +69.3 | 100% | 80% |
| 5 | +123.9 | +56.9 | 80% | 60% |
| 6 | +105.2 | +25.0 | 80% | 40% |
| 7 | +261.7 | +169.3 | 80% | 80% |
| 8 | +95.5 | +1.5 | 80% | 60% |
| 9 | +164.8 | +96.0 | 100% | 100% |
| 10 | +13.5 | -61.7 | 60% | 0% |
| 11 | +72.5 | +26.9 | 60% | 40% |
| 12 | +94.5 | +44.5 | 60% | 60% |

## Status

- Phase 2: 🟡 signal detected, mechanism under audit
- V3: 🔴 blocked
- UI: `marginal`
