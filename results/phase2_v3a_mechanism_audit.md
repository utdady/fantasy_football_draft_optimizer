# V3-A mechanism audit (D−C)

- stage: `V3A_MECHANISM_AUDIT`
- curve: `adp_emp_pos_v1_train_2021_2023`
- evaluable: **0**
- pairs: 60
- source: `results\phase2_v3a_ladder.json`
- classification: `mean_improvement_tail_tradeoff`

Mechanism audit of D−C on frozen V3-A.0 ladder pairs. No resimulation; values joined from structural + calibrated DBs. Map remains f6c5010 artifact; findings are not permission to retune.

**A mechanism finding (e.g. late-QB uplift) is a finding, not a map edit.**

## Interpretation gates

- HINGE: D |error| substantially closer to 0 + D draft tail worse — calibration works at player level; construction interaction implicated (V3-B becomes legitimate to design, not implement yet)
- CAVEAT: D−C positive mass is concentrated (Hypothesis D) — mean improvement is not evenly distributed across boards
- FINDING: every first fork is R1 D=QB vs C=RB/WR — D wins the fork pick on actual (~95%) but mean RB starter Δ is large negative (portfolio / construction interaction). Not a map edit.

## 1. Aggregate D−C

| Contract | Mean | Median | WR | p10 | p25 | p75 | p90 | min | max | n_neg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | +22.09 | +29.96 | 55% | -268.43 | -107.79 | +197.21 | +259.41 | -465.04 | +508.32 | 27/60 |
| Ex-DST | +21.82 | +29.96 | 55% | -268.43 | -107.79 | +193.03 | +259.41 | -465.04 | +508.32 | 27/60 |
| Ex-DST+TE | -24.41 | -10.70 | 48% | -322.22 | -154.47 | +138.37 | +237.88 | -559.28 | +376.90 | 31/60 |

## 2. Concentration

- Σ(D−C) = +1325.18
- flag: **concentrated — top-10 positive drafts ≥50% of positive mass**
- top-5 sum = +1779.06 (share of Σ = 1.3425)
- top-10 sum = +3023.26 (share of Σ = 2.2814; share of positive mass = 0.5336)

### Top-10 drafts by D−C

| Slot | Seed | D−C |
| ---: | ---: | ---: |
| 8 | 44 | +508.32 |
| 1 | 46 | +346.46 |
| 5 | 44 | +335.48 |
| 8 | 46 | +319.30 |
| 8 | 42 | +269.50 |
| 6 | 42 | +261.48 |
| 3 | 42 | +259.18 |
| 3 | 45 | +257.82 |
| 7 | 44 | +236.82 |
| 4 | 42 | +228.90 |

## 3. Position × round × slot

### Mean starter actual Δ (D−C) by position

| Pos | Mean Δ | Median | WR |
| --- | ---: | ---: | ---: |
| QB | +68.74 | +72.86 | 80% |
| RB | -161.67 | -119.25 | 23% |
| WR | +68.51 | +62.35 | 72% |
| TE | +46.23 | +26.80 | 55% |
| DST | +0.27 | +0.00 | 5% |
| K | +0.00 | +0.00 | 0% |

### Mean starter actual Δ by round band

| Band | Mean Δ | Median | WR |
| --- | ---: | ---: | ---: |
| r1-5 | +102.50 | +120.79 | 67% |
| r6-10 | -32.10 | -57.00 | 38% |
| r11-15 | -48.31 | -0.35 | 32% |

### By draft slot

| Slot | Mean D−C | Median | WR |
| ---: | ---: | ---: | ---: |
| 1 | +56.47 | +35.04 | 60% |
| 2 | +55.33 | +33.72 | 80% |
| 3 | +105.96 | +212.26 | 60% |
| 4 | +175.44 | +197.28 | 100% |
| 5 | +23.83 | +13.78 | 60% |
| 6 | -34.08 | -85.10 | 40% |
| 7 | +37.34 | -0.12 | 40% |
| 8 | +126.92 | +269.50 | 60% |
| 9 | -112.91 | -15.46 | 40% |
| 10 | -129.54 | -183.48 | 20% |
| 11 | +39.10 | +50.32 | 60% |
| 12 | -78.82 | -8.20 | 40% |

### Value map shifts (D−C on unique drafted players)

- unique players with both values: 165
- mean value Δ by pos: `{'TE': -21.5616, 'RB': -43.6361, 'WR': -28.71, 'DST': 46.3559, 'QB': 69.3812}`

Biggest upward (D lifts vs C):

| Player | Pos | ADP | C val | D val | Δ |
| --- | --- | ---: | ---: | ---: | ---: |
| Will Levis | QB | 160.00 | 39.11 | 172.09 | +132.98 |
| Baker Mayfield | QB | 156.00 | 46.93 | 178.75 | +131.83 |
| Deshaun Watson | QB | 149.30 | 60.03 | 189.92 | +129.89 |
| Justin Fields | QB | 134.70 | 88.58 | 198.75 | +110.17 |
| Aaron Rodgers | QB | 130.40 | 96.98 | 198.75 | +101.77 |
| Kirk Cousins | QB | 130.10 | 97.57 | 198.75 | +101.18 |
| Trevor Lawrence | QB | 126.70 | 104.22 | 198.75 | +94.53 |
| Matthew Stafford | QB | 123.10 | 111.26 | 198.75 | +87.49 |
| Caleb Williams | QB | 116.70 | 123.77 | 198.75 | +74.98 |
| Taysom Hill | TE | 155.90 | 47.12 | 119.85 | +72.72 |

Biggest downward (D compresses vs C):

| Player | Pos | ADP | C val | D val | Δ |
| --- | --- | ---: | ---: | ---: | ---: |
| Travis Kelce | TE | 24.40 | 304.25 | 191.16 | -113.08 |
| David Montgomery | RB | 54.60 | 245.20 | 134.14 | -111.05 |
| Travis Etienne Jr. | RB | 17.60 | 317.54 | 210.12 | -107.43 |
| D'Andre Swift | RB | 56.50 | 241.48 | 134.14 | -107.34 |
| Isiah Pacheco | RB | 19.80 | 313.24 | 206.15 | -107.09 |
| De'Von Achane | RB | 21.40 | 310.11 | 203.80 | -106.31 |
| Aaron Jones Sr. | RB | 46.00 | 262.01 | 157.80 | -104.21 |
| Sam LaPorta | TE | 29.40 | 294.47 | 190.93 | -103.54 |
| Rachaad White | RB | 29.00 | 295.25 | 192.67 | -102.59 |
| Christian McCaffrey | RB | 1.40 | 349.22 | 247.04 | -102.18 |

## 4. Fork analysis (first C≠D pick)

- forks: 60
- first-fork actual winner counts: `{'D': 57, 'C': 3}`
- D win rate at first fork: 0.95
- regret (C_actual − D_actual): mean=-212.95, median=-246.04, p10=-331.24
- fork rounds: `{'1': 60}`
- C positions: `{'RB': 39, 'WR': 21}`
- D positions: `{'QB': 60}`

### Fork rows (all)

| Slot | Seed | R | C pick | D pick | C val | D val | act C | act D | e_C | e_D | winner | regret_D |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 1 | 43 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 1 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 1 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 1 | 46 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 2 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 2 | 43 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 2 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 2 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 2 | 46 | 1 | Breece Hall (RB) | Josh Allen (QB) | 347.65 | 350.29 | 240.90 | 379.04 | -106.75 | +28.75 | D | -138.14 |
| 3 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 3 | 43 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 3 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 3 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 3 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 4 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 4 | 43 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 4 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 4 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 4 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 5 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 5 | 43 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 5 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 5 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 5 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 6 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 6 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 6 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 6 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 6 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 7 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 7 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 7 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 7 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 7 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 8 | 42 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 8 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 8 | 44 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 8 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 8 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 9 | 42 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 9 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 9 | 44 | 1 | Justin Jefferson (WR) | Josh Allen (QB) | 336.31 | 350.29 | 317.48 | 379.04 | -18.83 | +28.75 | D | -61.56 |
| 9 | 45 | 1 | Christian McCaffrey (RB) | Josh Allen (QB) | 349.22 | 350.29 | 47.80 | 379.04 | -301.42 | +28.75 | D | -331.24 |
| 9 | 46 | 1 | Tyreek Hill (WR) | Josh Allen (QB) | 346.87 | 350.29 | 218.20 | 379.04 | -128.67 | +28.75 | D | -160.84 |
| 10 | 42 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 10 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 10 | 44 | 1 | Justin Jefferson (WR) | Josh Allen (QB) | 336.31 | 350.29 | 317.48 | 379.04 | -18.83 | +28.75 | D | -61.56 |
| 10 | 45 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 10 | 46 | 1 | Ja'Marr Chase (WR) | Josh Allen (QB) | 337.88 | 350.29 | 403.00 | 379.04 | +65.12 | +28.75 | C | +23.96 |
| 11 | 42 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 11 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 11 | 44 | 1 | Jonathan Taylor (RB) | Josh Allen (QB) | 332.79 | 350.29 | 244.70 | 379.04 | -88.09 | +28.75 | D | -134.34 |
| 11 | 45 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 11 | 46 | 1 | Ja'Marr Chase (WR) | Josh Allen (QB) | 337.88 | 350.29 | 403.00 | 379.04 | +65.12 | +28.75 | C | +23.96 |
| 12 | 42 | 1 | Bijan Robinson (RB) | Josh Allen (QB) | 342.37 | 350.29 | 341.70 | 379.04 | -0.67 | +28.75 | D | -37.34 |
| 12 | 43 | 1 | CeeDee Lamb (WR) | Josh Allen (QB) | 344.72 | 350.29 | 263.40 | 379.04 | -81.32 | +28.75 | D | -115.64 |
| 12 | 44 | 1 | Jonathan Taylor (RB) | Josh Allen (QB) | 332.79 | 350.29 | 244.70 | 379.04 | -88.09 | +28.75 | D | -134.34 |
| 12 | 45 | 1 | Justin Jefferson (WR) | Josh Allen (QB) | 336.31 | 350.29 | 317.48 | 379.04 | -18.83 | +28.75 | D | -61.56 |
| 12 | 46 | 1 | Ja'Marr Chase (WR) | Josh Allen (QB) | 337.88 | 350.29 | 403.00 | 379.04 | +65.12 | +28.75 | C | +23.96 |

## 5. Prediction-error comparison (hinge)

e = actual − value. Negative mean ⇒ over-projection. Paired abs improve on D roster: |e_C| − |e_D| > 0 means D closer to actual.

| Set | Mean e | Median e | Mean |e| | Median |e| |
| --- | ---: | ---: | ---: | ---: |
| All C picks (e_C) | -19.47 | -16.02 | 87.80 | 78.41 |
| All D picks (e_D) | +2.27 | -1.96 | 54.30 | 52.07 |
| Fork C pick (e_C) | -179.82 | -215.04 | 186.33 | 215.04 |
| Fork D pick (e_D) | +28.75 | +28.75 | 28.75 | 28.75 |

### Paired |e| on D roster (same player, both maps)

- n=900; |e| better under D: 672 (0.7467); worse: 228
- mean (|e_C| − |e_D|) = +26.74 (positive ⇒ D closer)

## Status

- Map: frozen (`adp_emp_pos_v1_train_2021_2023` / f6c5010)
- V3-B: only if hinge shows better player error + worse draft tail
- UI: `marginal`
