# P2.2C right-tail gain-case inspection (best C−B)

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- cases: 10 (best C−B)
- source: `results\phase2_p22c_valuation_cb_mechanism.json`

Decision-point inspection of best C−B pairs (symmetry check vs left tail). Hypotheses only — not V3.

**Structural uses raw marginal on ADP-curve (no explicit replacement). First fork is on a shared board; later picks diverge. UI stays marginal.**

## Aggregate fork fingerprints

- fork tags: `{'structural_skill_over_rb_qb': 5, 'mid_round_fork': 8, 'structural_mid_te': 1, 'early_round_fork': 2, 'fork_pick_itself_large_actual_loss': 2}`
- fork rounds: `{5: 2, 6: 6, 7: 1, 8: 1}`
- C position at fork: `{'WR': 4, 'RB': 3, 'TE': 1, 'QB': 2}`
- B position at fork: `{'QB': 6, 'RB': 1, 'WR': 3}`
- fork pick itself (C vs B actual): C wins 6, C loses 4
- cases with post-fork hindsight regret ≥80 among shown alts: 10/10

### Symmetry note

Compare fork tags / positions to the worst-10 artifact. If TE/skill-over-QB is common here too, the left-tail pattern is high-variance, not a directional bias.

## Slot 7 seed 42 — C−B +562.40

Tags: `structural_skill_over_rb_qb, mid_round_fork`

Pos Δ: QB +0.0, RB +86.5, WR +256.6, TE +170.3, DST +49.0, K +0.0

### First fork — R6 (overall ~66)

- **B chose:** Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- **C chose:** Keenan Allen (WR) · ADP 63.5 · curve 228 · marg +227.8 · actual +184.4
- Actual Δ at fork (C−B pick): 21.04
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Keenan Allen (WR) · ADP 63.5 · curve 228 · marg +227.8 · actual +184.4 ← chosen
2. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
3. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
4. Jayden Reed (WR) · ADP 65.1 · curve 225 · marg +224.7 · actual +197.0
5. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
6. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
7. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · marg +218.2 · actual +137.8
8. Terry McLaurin (WR) · ADP 70.2 · curve 215 · marg +214.7 · actual +267.8

B alternatives at fork (ADP-feasible order):

1. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4 ← chosen
2. Keenan Allen (WR) · ADP 63.5 · curve 228 · actual +184.4
3. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
4. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
5. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
6. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
7. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
8. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +114.2
  - B parallel pick: Javonte Williams (RB) · ADP 77.5 · curve 200 · actual +157.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Diontae Johnson (WR) · ADP 92.1 · curve 172 · actual +89.1
- R10: took Tyler Lockett (WR) · ADP 106.6 · curve 144 · marg +0.0 · actual +121.0; best shown alt Justin Herbert (QB) · ADP 114.6 · curve 128 · marg +0.0 · actual +285.4; regret +164.4
  - B parallel pick: Brock Purdy (QB) · ADP 105.7 · curve 145 · actual +266.9
- R12: took Jaleel McLaughlin (RB) · ADP 126.6 · curve 104 · marg +0.0 · actual +97.2; best shown alt Jerry Jeudy (WR) · ADP 132.9 · curve 92 · marg +0.0 · actual +240.9; regret +143.7
  - B parallel pick: Trevor Lawrence (QB) · ADP 126.7 · curve 104 · actual +145.2
- R14: took Ray Davis (RB) · ADP 147.7 · curve 63 · marg +0.0 · actual +116.1; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +249.7
  - B parallel pick: Cleveland Defense (DST) · ADP 155.1 · curve 49 · actual +61.0
- R15: took Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +121.4
  - B parallel pick: Dameon Pierce (RB) · ADP 151.4 · curve 56 · actual +43.5

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Puka Nacua (WR) 206.6 | Puka Nacua (WR) 206.6 | +0.0 |
| 3 | Y | Josh Allen (QB) 379.04 | Josh Allen (QB) 379.04 | +0.0 |
| 4 | Y | Alvin Kamara (RB) 265.3 | Alvin Kamara (RB) 265.3 | +0.0 |
| 5 | Y | Amari Cooper (WR) 122.7 | Amari Cooper (WR) 122.7 | +0.0 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | Keenan Allen (WR) 184.4 | +21.0 |
| 7 | Y | Najee Harris (RB) 204.6 | Najee Harris (RB) 204.6 | +0.0 |
| 8 | **N** | Javonte Williams (RB) 157.9 | David Njoku (TE) 148.5 | -9.4 |
| 9 | **N** | Diontae Johnson (WR) 89.1 | Baltimore Defense (DST) 110.0 | +20.9 |
| 10 | **N** | Brock Purdy (QB) 266.86 | Tyler Lockett (WR) 121.0 | -145.9 |
| 11 | **N** | Justin Herbert (QB) 285.4 | Brian Thomas Jr. (WR) 284.0 | -1.4 |
| 12 | **N** | Trevor Lawrence (QB) 145.2 | Jaleel McLaughlin (RB) 97.2 | -48.0 |
| 13 | **N** | Brandin Cooks (WR) 69.6 | Pat Freiermuth (TE) 170.3 | +100.7 |
| 14 | **N** | Cleveland Defense (DST) 61.0 | Ray Davis (RB) 116.1 | +55.1 |
| 15 | **N** | Dameon Pierce (RB) 43.5 | Bucky Irving (RB) 244.4 | +200.9 |

## Slot 7 seed 44 — C−B +416.90

Tags: `structural_skill_over_rb_qb, mid_round_fork`

Pos Δ: QB +0.0, RB +130.0, WR +40.8, TE +225.1, DST +21.0, K +0.0

### First fork — R6 (overall ~66)

- **B chose:** Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- **C chose:** Tank Dell (WR) · ADP 57.5 · curve 240 · marg +239.5 · actual +140.0
- Actual Δ at fork (C−B pick): -23.36
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Tank Dell (WR) · ADP 57.5 · curve 240 · marg +239.5 · actual +140.0 ← chosen
2. Keenan Allen (WR) · ADP 63.5 · curve 228 · marg +227.8 · actual +184.4
3. Rashee Rice (WR) · ADP 64.2 · curve 226 · marg +226.4 · actual +64.9
4. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
5. Jayden Reed (WR) · ADP 65.1 · curve 225 · marg +224.7 · actual +197.0
6. George Kittle (TE) · ADP 66.7 · curve 222 · marg +221.5 · actual +236.6
7. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
8. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3

B alternatives at fork (ADP-feasible order):

1. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4 ← chosen
2. Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0
3. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
4. Keenan Allen (WR) · ADP 63.5 · curve 228 · actual +184.4
5. Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9
6. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
7. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
8. George Kittle (TE) · ADP 66.7 · curve 222 · actual +236.6

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R7: took Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3; best shown alt George Kittle (TE) · ADP 66.7 · curve 222 · marg +221.5 · actual +236.6; regret +173.3
  - B parallel pick: Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Jaxon Smith-Njigba (WR) · ADP 90.5 · curve 175 · actual +253.0
- R10: took Romeo Doubs (WR) · ADP 103.0 · curve 151 · marg +0.0 · actual +132.1; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +151.9
  - B parallel pick: DeAndre Hopkins (WR) · ADP 104.5 · curve 148 · actual +147.0
- R12: took Kirk Cousins (QB) · ADP 130.1 · curve 98 · marg +0.0 · actual +176.3; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +80.3
  - B parallel pick: Ty Chandler (RB) · ADP 130.3 · curve 97 · actual +28.4
- R14: took Zach Charbonnet (RB) · ADP 130.7 · curve 96 · marg +0.0 · actual +186.9; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +178.9
  - B parallel pick: Luke Musgrave (TE) · ADP 151.7 · curve 55 · actual +11.5

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Marvin Harrison Jr. (WR) 196.5 | Marvin Harrison Jr. (WR) 196.5 | +0.0 |
| 3 | Y | Isiah Pacheco (RB) 56.9 | Isiah Pacheco (RB) 56.9 | +0.0 |
| 4 | Y | Patrick Mahomes (QB) 283.02 | Patrick Mahomes (QB) 283.02 | +0.0 |
| 5 | Y | Amari Cooper (WR) 122.7 | Amari Cooper (WR) 122.7 | +0.0 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | Tank Dell (WR) 140.0 | -23.4 |
| 7 | **N** | Rashee Rice (WR) 64.9 | Nick Chubb (RB) 63.3 | -1.6 |
| 8 | **N** | Nick Chubb (RB) 63.3 | George Kittle (TE) 236.6 | +173.3 |
| 9 | **N** | Jaxon Smith-Njigba (WR) 253.0 | Baltimore Defense (DST) 110.0 | -143.0 |
| 10 | **N** | DeAndre Hopkins (WR) 147.0 | Romeo Doubs (WR) 132.1 | -14.9 |
| 11 | **N** | Mike Williams (WR) 56.8 | Brian Thomas Jr. (WR) 284.0 | +227.2 |
| 12 | **N** | Ty Chandler (RB) 28.4 | Kirk Cousins (QB) 176.32 | +147.9 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 14 | **N** | Luke Musgrave (TE) 11.5 | Zach Charbonnet (RB) 186.9 | +175.4 |
| 15 | **N** | Cincinnati Defense (DST) 89.0 | Adam Thielen (WR) 139.5 | +50.5 |

## Slot 3 seed 43 — C−B +397.46

Tags: `mid_round_fork`

Pos Δ: QB +0.0, RB +166.7, WR +179.6, TE +46.2, DST +5.0, K +0.0

### First fork — R6 (overall ~70)

- **B chose:** Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- **C chose:** D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5
- Actual Δ at fork (C−B pick): 51.14
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5 ← chosen
2. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
3. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
4. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
5. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
6. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · marg +218.2 · actual +137.8
7. Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9
8. Calvin Ridley (WR) · ADP 74.7 · curve 206 · marg +205.9 · actual +199.2

B alternatives at fork (ADP-feasible order):

1. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4 ← chosen
2. D'Andre Swift (RB) · ADP 56.5 · curve 241 · actual +214.5
3. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
4. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
5. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
6. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
7. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
8. Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +114.2
  - B parallel pick: Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · actual +181.6
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Diontae Johnson (WR) · ADP 92.1 · curve 172 · actual +89.1
- R10: took Tyler Lockett (WR) · ADP 106.6 · curve 144 · marg +0.0 · actual +121.0; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +163.0
  - B parallel pick: Brock Purdy (QB) · ADP 105.7 · curve 145 · actual +266.9
- R15: took Josh Downs (WR) · ADP 155.9 · curve 47 · marg +0.0 · actual +183.5; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +82.5
  - B parallel pick: Taysom Hill (TE) · ADP 155.9 · curve 47 · actual +102.3

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | A.J. Brown (WR) 216.9 | A.J. Brown (WR) 216.9 | +0.0 |
| 3 | Y | De'Von Achane (RB) 299.9 | De'Von Achane (RB) 299.9 | +0.0 |
| 4 | Y | Mike Evans (WR) 240.4 | Mike Evans (WR) 240.4 | +0.0 |
| 5 | Y | Lamar Jackson (QB) 430.38 | Lamar Jackson (QB) 430.38 | +0.0 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | D'Andre Swift (RB) 214.5 | +51.1 |
| 7 | Y | Zay Flowers (WR) 209.5 | Zay Flowers (WR) 209.5 | +0.0 |
| 8 | **N** | Tua Tagovailoa (QB) 181.58 | David Njoku (TE) 148.5 | -33.1 |
| 9 | **N** | Diontae Johnson (WR) 89.1 | Baltimore Defense (DST) 110.0 | +20.9 |
| 10 | **N** | Brock Purdy (QB) 266.86 | Tyler Lockett (WR) 121.0 | -145.9 |
| 11 | **N** | Justin Herbert (QB) 285.4 | Brian Thomas Jr. (WR) 284.0 | -1.4 |
| 12 | **N** | Trevor Lawrence (QB) 145.2 | Rico Dowdle (RB) 197.8 | +52.6 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Kirk Cousins (QB) 176.32 | +68.9 |
| 14 | **N** | Detroit Defense (DST) 105.0 | Jordan Addison (WR) 212.5 | +107.5 |
| 15 | **N** | Taysom Hill (TE) 102.34 | Josh Downs (WR) 183.5 | +81.2 |

## Slot 3 seed 42 — C−B +375.44

Tags: `structural_mid_te, structural_skill_over_rb_qb, mid_round_fork`

Pos Δ: QB -18.5, RB +162.5, WR +162.1, TE +89.4, DST -20.0, K +0.0

### First fork — R8 (overall ~94)

- **B chose:** Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
- **C chose:** David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5
- Actual Δ at fork (C−B pick): 66.6
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=2
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5 ← chosen
2. Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6
3. Dalton Schultz (TE) · ADP 117.9 · curve 121 · marg +121.4 · actual +118.2
4. T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +119.9 · actual +86.5
5. Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7
6. Zack Moss (RB) · ADP 74.4 · curve 206 · marg +0.0 · actual +81.9
7. Jaylen Warren (RB) · ADP 79.6 · curve 196 · marg +0.0 · actual +124.1
8. Xavier Worthy (WR) · ADP 81.9 · curve 192 · marg +0.0 · actual +187.2

B alternatives at fork (ADP-feasible order):

1. Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9 ← chosen
2. Jaylen Warren (RB) · ADP 79.6 · curve 196 · actual +124.1
3. Xavier Worthy (WR) · ADP 81.9 · curve 192 · actual +187.2
4. Keon Coleman (WR) · ADP 88.1 · curve 180 · actual +111.5
5. Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6
6. Diontae Johnson (WR) · ADP 92.1 · curve 172 · actual +89.1
7. Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
8. Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Ladd McConkey (WR) · ADP 98.4 · curve 160 · marg +0.0 · actual +240.9; regret +130.9
  - B parallel pick: Keon Coleman (WR) · ADP 88.1 · curve 180 · actual +111.5
- R12: took Trevor Lawrence (QB) · ADP 126.7 · curve 104 · marg +0.0 · actual +145.2; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +111.4
  - B parallel pick: Elijah Mitchell (RB) · ADP 129.8 · curve 98 · actual +0.0
- R14: took Dameon Pierce (RB) · ADP 151.4 · curve 56 · marg +0.0 · actual +43.5; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +322.3
  - B parallel pick: Pittsburgh Defense (DST) · ADP 157.8 · curve 43 · actual +130.0
- R15: took Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +121.4
  - B parallel pick: Dawson Knox (TE) · ADP 165.9 · curve 28 · actual +59.1

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Marvin Harrison Jr. (WR) 196.5 | Marvin Harrison Jr. (WR) 196.5 | +0.0 |
| 3 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 4 | Y | Stefon Diggs (WR) 121.92 | Stefon Diggs (WR) 121.92 | +0.0 |
| 5 | Y | Aaron Jones Sr. (RB) 241.6 | Aaron Jones Sr. (RB) 241.6 | +0.0 |
| 6 | Y | Anthony Richardson Sr. (QB) 163.36 | Anthony Richardson Sr. (QB) 163.36 | +0.0 |
| 7 | Y | Keenan Allen (WR) 184.4 | Keenan Allen (WR) 184.4 | +0.0 |
| 8 | **N** | Zack Moss (RB) 81.9 | David Njoku (TE) 148.5 | +66.6 |
| 9 | **N** | Keon Coleman (WR) 111.5 | Baltimore Defense (DST) 110.0 | -1.5 |
| 10 | Y | Brock Purdy (QB) 266.86 | Brock Purdy (QB) 266.86 | +0.0 |
| 11 | **N** | Justin Herbert (QB) 285.4 | Brian Thomas Jr. (WR) 284.0 | -1.4 |
| 12 | **N** | Elijah Mitchell (RB) 0.0 | Trevor Lawrence (QB) 145.2 | +145.2 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 14 | **N** | Pittsburgh Defense (DST) 130.0 | Dameon Pierce (RB) 43.5 | -86.5 |
| 15 | **N** | Dawson Knox (TE) 59.1 | Bucky Irving (RB) 244.4 | +185.3 |

## Slot 7 seed 43 — C−B +347.26

Tags: `structural_skill_over_rb_qb, early_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB -51.3, RB +147.1, WR +85.0, TE +144.5, DST +22.0, K +0.0

### First fork — R5 (overall ~55)

- **B chose:** Lamar Jackson (QB) · ADP 44.2 · curve 266 · actual +430.4
- **C chose:** Tee Higgins (WR) · ADP 51.8 · curve 251 · marg +250.7 · actual +222.1
- Actual Δ at fork (C−B pick): -208.28
- C roster need: counts={'QB': 1, 'RB': 1, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=5
- B roster need: counts={'QB': 1, 'RB': 1, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Tee Higgins (WR) · ADP 51.8 · curve 251 · marg +250.7 · actual +222.1 ← chosen
2. Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9
3. D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5
4. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
5. Tank Dell (WR) · ADP 57.5 · curve 240 · marg +239.5 · actual +140.0
6. Dalton Kincaid (TE) · ADP 59.1 · curve 236 · marg +236.4 · actual +100.8
7. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9
8. Keenan Allen (WR) · ADP 63.5 · curve 228 · marg +227.8 · actual +184.4

B alternatives at fork (ADP-feasible order):

1. Lamar Jackson (QB) · ADP 44.2 · curve 266 · actual +430.4 ← chosen
2. Tee Higgins (WR) · ADP 51.8 · curve 251 · actual +222.1
3. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
4. Christian Kirk (WR) · ADP 55.6 · curve 243 · actual +70.9
5. D'Andre Swift (RB) · ADP 56.5 · curve 241 · actual +214.5
6. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
7. Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0
8. Dalton Kincaid (TE) · ADP 59.1 · curve 236 · actual +100.8

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R6: took Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9; best shown alt George Kittle (TE) · ADP 66.7 · curve 222 · marg +221.5 · actual +236.6; regret +165.7
  - B parallel pick: Christian Kirk (WR) · ADP 55.6 · curve 243 · actual +70.9
- R8: took Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +158.3
  - B parallel pick: Jonathon Brooks (RB) · ADP 85.4 · curve 185 · actual +7.5
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Ladd McConkey (WR) · ADP 98.4 · curve 160 · marg +0.0 · actual +240.9; regret +130.9
  - B parallel pick: Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
- R10: took Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · marg +0.0 · actual +57.5; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +226.5
  - B parallel pick: Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9
- R11: took Khalil Shakir (WR) · ADP 117.4 · curve 122 · marg +0.0 · actual +182.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +80.2
  - B parallel pick: Dalton Schultz (TE) · ADP 117.9 · curve 121 · actual +118.2
- R14: took Dallas Defense (DST) · ADP 139.3 · curve 80 · marg +0.0 · actual +88.0; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +277.8
  - B parallel pick: Dallas Defense (DST) · ADP 139.3 · curve 80 · actual +88.0
- R15: took Jordan Mason (RB) · ADP 149.1 · curve 60 · marg +0.0 · actual +115.0; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +151.0
  - B parallel pick: Quentin Johnston (WR) · ADP 152.2 · curve 54 · actual +174.7

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | CeeDee Lamb (WR) 263.4 | CeeDee Lamb (WR) 263.4 | +0.0 |
| 2 | Y | Bijan Robinson (RB) 341.7 | Bijan Robinson (RB) 341.7 | +0.0 |
| 3 | Y | Josh Allen (QB) 379.04 | Josh Allen (QB) 379.04 | +0.0 |
| 4 | Y | Mike Evans (WR) 240.4 | Mike Evans (WR) 240.4 | +0.0 |
| 5 | **N** | Lamar Jackson (QB) 430.38 | Tee Higgins (WR) 222.1 | -208.3 |
| 6 | Y | Christian Kirk (WR) 70.9 | Christian Kirk (WR) 70.9 | +0.0 |
| 7 | **N** | Zamir White (RB) 29.3 | Najee Harris (RB) 204.6 | +175.3 |
| 8 | **N** | Jonathon Brooks (RB) 7.5 | Jake Ferguson (TE) 104.4 | +96.9 |
| 9 | **N** | Ezekiel Elliott (RB) 57.5 | Baltimore Defense (DST) 110.0 | +52.5 |
| 10 | **N** | Rome Odunze (WR) 144.9 | Ezekiel Elliott (RB) 57.5 | -87.4 |
| 11 | **N** | Dalton Schultz (TE) 118.2 | Khalil Shakir (WR) 182.5 | +64.3 |
| 12 | **N** | Curtis Samuel (WR) 63.7 | Brock Bowers (TE) 262.7 | +199.0 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 14 | Y | Dallas Defense (DST) 88.0 | Dallas Defense (DST) 88.0 | +0.0 |
| 15 | **N** | Quentin Johnston (WR) 174.7 | Jordan Mason (RB) 115.0 | -59.7 |

## Slot 6 seed 43 — C−B +283.20

Tags: `mid_round_fork`

Pos Δ: QB +0.0, RB +27.6, WR +182.5, TE +24.1, DST +49.0, K +0.0

### First fork — R6 (overall ~67)

- **B chose:** Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- **C chose:** D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5
- Actual Δ at fork (C−B pick): 51.14
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5 ← chosen
2. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
3. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
4. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
5. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
6. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · marg +218.2 · actual +137.8
7. Terry McLaurin (WR) · ADP 70.2 · curve 215 · marg +214.7 · actual +267.8
8. Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · marg +209.6 · actual +131.2

B alternatives at fork (ADP-feasible order):

1. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4 ← chosen
2. D'Andre Swift (RB) · ADP 56.5 · curve 241 · actual +214.5
3. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
4. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
5. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
6. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
7. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
8. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R7: took Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9; best shown alt Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7; regret +129.8
  - B parallel pick: Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
- R8: took Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +158.3
  - B parallel pick: Christian Watson (WR) · ADP 84.2 · curve 187 · actual +105.3
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Ladd McConkey (WR) · ADP 98.4 · curve 160 · marg +0.0 · actual +240.9; regret +130.9
  - B parallel pick: Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
- R10: took DeAndre Hopkins (WR) · ADP 104.5 · curve 148 · marg +0.0 · actual +147.0; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +137.0
  - B parallel pick: Dallas Goedert (TE) · ADP 105.5 · curve 146 · actual +103.6
- R11: took Khalil Shakir (WR) · ADP 117.4 · curve 122 · marg +0.0 · actual +182.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +80.2
  - B parallel pick: Dalton Schultz (TE) · ADP 117.9 · curve 121 · actual +118.2
- R13: took Ty Chandler (RB) · ADP 130.3 · curve 97 · marg +0.0 · actual +28.4; best shown alt Cole Kmet (TE) · ADP 137.1 · curve 84 · marg +0.0 · actual +120.4; regret +92.0
  - B parallel pick: Zach Charbonnet (RB) · ADP 130.7 · curve 96 · actual +186.9
- R14: took Cole Kmet (TE) · ADP 137.1 · curve 84 · marg +0.0 · actual +120.4; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +245.4
  - B parallel pick: Cole Kmet (TE) · ADP 137.1 · curve 84 · actual +120.4
- R15: took Cleveland Defense (DST) · ADP 155.1 · curve 49 · marg +0.0 · actual +61.0; best shown alt Josh Downs (WR) · ADP 155.9 · curve 47 · marg +0.0 · actual +183.5; regret +122.5
  - B parallel pick: Cleveland Defense (DST) · ADP 155.1 · curve 49 · actual +61.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | CeeDee Lamb (WR) 263.4 | CeeDee Lamb (WR) 263.4 | +0.0 |
| 2 | Y | Bijan Robinson (RB) 341.7 | Bijan Robinson (RB) 341.7 | +0.0 |
| 3 | Y | Drake London (WR) 280.8 | Drake London (WR) 280.8 | +0.0 |
| 4 | Y | Alvin Kamara (RB) 265.3 | Alvin Kamara (RB) 265.3 | +0.0 |
| 5 | Y | Lamar Jackson (QB) 430.38 | Lamar Jackson (QB) 430.38 | +0.0 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | D'Andre Swift (RB) 214.5 | +51.1 |
| 7 | Y | Raheem Mostert (RB) 70.9 | Raheem Mostert (RB) 70.9 | +0.0 |
| 8 | **N** | Christian Watson (WR) 105.3 | Jake Ferguson (TE) 104.4 | -0.9 |
| 9 | **N** | Ezekiel Elliott (RB) 57.5 | Baltimore Defense (DST) 110.0 | +52.5 |
| 10 | **N** | Dallas Goedert (TE) 103.6 | DeAndre Hopkins (WR) 147.0 | +43.4 |
| 11 | **N** | Dalton Schultz (TE) 118.2 | Khalil Shakir (WR) 182.5 | +64.3 |
| 12 | **N** | Curtis Samuel (WR) 63.7 | Brock Bowers (TE) 262.7 | +199.0 |
| 13 | **N** | Zach Charbonnet (RB) 186.9 | Ty Chandler (RB) 28.4 | -158.5 |
| 14 | Y | Cole Kmet (TE) 120.4 | Cole Kmet (TE) 120.4 | +0.0 |
| 15 | Y | Cleveland Defense (DST) 61.0 | Cleveland Defense (DST) 61.0 | +0.0 |

## Slot 2 seed 43 — C−B +275.70

Tags: `mid_round_fork`

Pos Δ: QB +0.0, RB +73.3, WR +113.0, TE +89.4, DST +0.0, K +0.0

### First fork — R7 (overall ~74)

- **B chose:** Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0
- **C chose:** Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9
- Actual Δ at fork (C−B pick): 93.86
- C roster need: counts={'QB': 0, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=3
- B roster need: counts={'QB': 0, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9 ← chosen
2. Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +203.2 · actual +297.2
3. Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · marg +178.7 · actual +181.6
4. Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4
5. Jared Goff (QB) · ADP 94.3 · curve 168 · marg +167.6 · actual +324.5
6. Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +158.0 · actual +355.8
7. David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5
8. Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6

B alternatives at fork (ADP-feasible order):

1. Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0 ← chosen
2. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
3. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
4. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
5. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
6. Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
7. Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
8. Calvin Ridley (WR) · ADP 74.7 · curve 206 · actual +199.2

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +114.2
  - B parallel pick: Keon Coleman (WR) · ADP 88.1 · curve 180 · actual +111.5
- R9: took Jaxon Smith-Njigba (WR) · ADP 90.5 · curve 175 · marg +0.0 · actual +253.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +102.8
  - B parallel pick: Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6
- R10: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +156.9
  - B parallel pick: Brock Purdy (QB) · ADP 105.7 · curve 145 · actual +266.9
- R14: took Detroit Defense (DST) · ADP 148.6 · curve 61 · marg +0.0 · actual +105.0; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +161.0
  - B parallel pick: Detroit Defense (DST) · ADP 148.6 · curve 61 · actual +105.0
- R15: took Cleveland Defense (DST) · ADP 155.1 · curve 49 · marg +0.0 · actual +61.0; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +205.0
  - B parallel pick: Dawson Knox (TE) · ADP 165.9 · curve 28 · actual +59.1

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | A.J. Brown (WR) 216.9 | A.J. Brown (WR) 216.9 | +0.0 |
| 3 | Y | Drake London (WR) 280.8 | Drake London (WR) 280.8 | +0.0 |
| 4 | Y | Mike Evans (WR) 240.4 | Mike Evans (WR) 240.4 | +0.0 |
| 5 | Y | Stefon Diggs (WR) 121.92 | Stefon Diggs (WR) 121.92 | +0.0 |
| 6 | Y | D'Andre Swift (RB) 214.5 | D'Andre Swift (RB) 214.5 | +0.0 |
| 7 | **N** | Tank Dell (WR) 140.0 | Jordan Love (QB) 233.86 | +93.9 |
| 8 | **N** | Keon Coleman (WR) 111.5 | David Njoku (TE) 148.5 | +37.0 |
| 9 | **N** | Tyjae Spears (RB) 113.6 | Jaxon Smith-Njigba (WR) 253.0 | +139.4 |
| 10 | **N** | Brock Purdy (QB) 266.86 | Baltimore Defense (DST) 110.0 | -156.9 |
| 11 | **N** | Blake Corum (RB) 33.5 | Brock Purdy (QB) 266.86 | +233.4 |
| 12 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 13 | **N** | Baltimore Defense (DST) 110.0 | Zach Charbonnet (RB) 186.9 | +76.9 |
| 14 | Y | Detroit Defense (DST) 105.0 | Detroit Defense (DST) 105.0 | +0.0 |
| 15 | **N** | Dawson Knox (TE) 59.1 | Cleveland Defense (DST) 61.0 | +1.9 |

## Slot 12 seed 42 — C−B +266.40

Tags: `structural_skill_over_rb_qb, early_round_fork`

Pos Δ: QB +0.0, RB -116.1, WR +348.6, TE +17.9, DST +16.0, K +0.0

### First fork — R5 (overall ~60)

- **B chose:** C.J. Stroud (QB) · ADP 49.9 · curve 254 · actual +220.4
- **C chose:** Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
- Actual Δ at fork (C−B pick): -10.88
- C roster need: counts={'QB': 1, 'RB': 3, 'WR': 0, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=5
- B roster need: counts={'QB': 1, 'RB': 3, 'WR': 0, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5 ← chosen
2. Tank Dell (WR) · ADP 57.5 · curve 240 · marg +239.5 · actual +140.0
3. George Pickens (WR) · ADP 59.8 · curve 235 · marg +235.0 · actual +164.4
4. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9
5. Keenan Allen (WR) · ADP 63.5 · curve 228 · marg +227.8 · actual +184.4
6. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
7. Rashee Rice (WR) · ADP 64.2 · curve 226 · marg +226.4 · actual +64.9
8. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3

B alternatives at fork (ADP-feasible order):

1. C.J. Stroud (QB) · ADP 49.9 · curve 254 · actual +220.4 ← chosen
2. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
3. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
4. Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0
5. George Pickens (WR) · ADP 59.8 · curve 235 · actual +164.4
6. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · actual +175.9
7. Keenan Allen (WR) · ADP 63.5 · curve 228 · actual +184.4
8. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R7: took Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9; best shown alt Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7; regret +118.8
  - B parallel pick: Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
- R8: took Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4; best shown alt Jordan Love (QB) · ADP 73.2 · curve 209 · marg +0.0 · actual +233.9; regret +129.5
  - B parallel pick: Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +156.9
  - B parallel pick: Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9
- R13: took Chicago Defense (DST) · ADP 147.4 · curve 64 · marg +0.0 · actual +94.0; best shown alt Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; regret +150.4
  - B parallel pick: Chicago Defense (DST) · ADP 147.4 · curve 64 · actual +94.0
- R14: took Ray Davis (RB) · ADP 147.7 · curve 63 · marg +0.0 · actual +116.1; best shown alt Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; regret +128.3
  - B parallel pick: Ray Davis (RB) · ADP 147.7 · curve 63 · actual +116.1
- R15: took Jahan Dotson (WR) · ADP 152.0 · curve 55 · marg +0.0 · actual +41.9; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +323.9
  - B parallel pick: Jahan Dotson (WR) · ADP 152.0 · curve 55 · actual +41.9

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Bijan Robinson (RB) 341.7 | Bijan Robinson (RB) 341.7 | +0.0 |
| 2 | Y | Jonathan Taylor (RB) 244.7 | Jonathan Taylor (RB) 244.7 | +0.0 |
| 3 | Y | James Cook III (RB) 266.7 | James Cook III (RB) 266.7 | +0.0 |
| 4 | Y | Patrick Mahomes (QB) 283.02 | Patrick Mahomes (QB) 283.02 | +0.0 |
| 5 | **N** | C.J. Stroud (QB) 220.38 | Zay Flowers (WR) 209.5 | -10.9 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | Tank Dell (WR) 140.0 | -23.4 |
| 7 | **N** | Jordan Love (QB) 233.86 | Zack Moss (RB) 81.9 | -152.0 |
| 8 | **N** | Zack Moss (RB) 81.9 | Jake Ferguson (TE) 104.4 | +22.5 |
| 9 | **N** | Rome Odunze (WR) 144.9 | Baltimore Defense (DST) 110.0 | -34.9 |
| 10 | Y | Ladd McConkey (WR) 240.9 | Ladd McConkey (WR) 240.9 | +0.0 |
| 11 | **N** | Mike Williams (WR) 56.8 | Brian Thomas Jr. (WR) 284.0 | +227.2 |
| 12 | **N** | T.J. Hockenson (TE) 86.5 | Caleb Williams (QB) 254.54 | +168.0 |
| 13 | Y | Chicago Defense (DST) 94.0 | Chicago Defense (DST) 94.0 | +0.0 |
| 14 | Y | Ray Davis (RB) 116.1 | Ray Davis (RB) 116.1 | +0.0 |
| 15 | Y | Jahan Dotson (WR) 41.9 | Jahan Dotson (WR) 41.9 | +0.0 |

## Slot 8 seed 46 — C−B +262.82

Tags: `mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB +114.7, RB +202.1, WR -78.0, TE +0.0, DST +24.0, K +0.0

### First fork — R6 (overall ~65)

- **B chose:** DJ Moore (WR) · ADP 43.7 · curve 267 · actual +238.1
- **C chose:** Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9
- Actual Δ at fork (C−B pick): -62.2
- C roster need: counts={'QB': 0, 'RB': 0, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 0, 'RB': 0, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9 ← chosen
2. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
3. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
4. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
5. Dak Prescott (QB) · ADP 69.8 · curve 215 · marg +215.5 · actual +116.5
6. Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9
7. Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9
8. Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +203.2 · actual +297.2

B alternatives at fork (ADP-feasible order):

1. DJ Moore (WR) · ADP 43.7 · curve 267 · actual +238.1 ← chosen
2. Tee Higgins (WR) · ADP 51.8 · curve 251 · actual +222.1
3. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · actual +175.9
4. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
5. Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9
6. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
7. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
8. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took Javonte Williams (RB) · ADP 77.5 · curve 200 · marg +200.4 · actual +157.9; best shown alt Chase Brown (RB) · ADP 91.9 · curve 172 · marg +172.3 · actual +255.0; regret +97.1
  - B parallel pick: Javonte Williams (RB) · ADP 77.5 · curve 200 · actual +157.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
- R10: took Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · marg +0.0 · actual +57.5; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +226.5
  - B parallel pick: Ladd McConkey (WR) · ADP 98.4 · curve 160 · actual +240.9
- R12: took Khalil Shakir (WR) · ADP 117.4 · curve 122 · marg +0.0 · actual +182.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +80.2
  - B parallel pick: Dalton Schultz (TE) · ADP 117.9 · curve 121 · actual +118.2
- R14: took Pat Freiermuth (TE) · ADP 135.5 · curve 87 · marg +0.0 · actual +170.3; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +195.5
  - B parallel pick: Khalil Herbert (RB) · ADP 136.4 · curve 85 · actual +31.5

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Tyreek Hill (WR) 218.2 | Tyreek Hill (WR) 218.2 | +0.0 |
| 2 | Y | Justin Jefferson (WR) 317.48 | Justin Jefferson (WR) 317.48 | +0.0 |
| 3 | Y | Deebo Samuel Sr. (WR) 155.6 | Deebo Samuel Sr. (WR) 155.6 | +0.0 |
| 4 | Y | Mike Evans (WR) 240.4 | Mike Evans (WR) 240.4 | +0.0 |
| 5 | Y | Mark Andrews (TE) 188.8 | Mark Andrews (TE) 188.8 | +0.0 |
| 6 | **N** | DJ Moore (WR) 238.1 | Rhamondre Stevenson (RB) 175.9 | -62.2 |
| 7 | **N** | Terry McLaurin (WR) 267.8 | Jordan Love (QB) 233.86 | -33.9 |
| 8 | Y | Javonte Williams (RB) 157.9 | Javonte Williams (RB) 157.9 | +0.0 |
| 9 | **N** | Ezekiel Elliott (RB) 57.5 | Baltimore Defense (DST) 110.0 | +52.5 |
| 10 | **N** | Ladd McConkey (WR) 240.9 | Ezekiel Elliott (RB) 57.5 | -183.4 |
| 11 | **N** | Blake Corum (RB) 33.5 | Chuba Hubbard (RB) 241.6 | +208.1 |
| 12 | **N** | Dalton Schultz (TE) 118.2 | Khalil Shakir (WR) 182.5 | +64.3 |
| 13 | **N** | Justin Fields (QB) 119.14 | Jordan Addison (WR) 212.5 | +93.4 |
| 14 | **N** | Khalil Herbert (RB) 31.5 | Pat Freiermuth (TE) 170.3 | +138.8 |
| 15 | **N** | Kansas City Defense (DST) 94.0 | Buffalo Defense (DST) 118.0 | +24.0 |

## Slot 9 seed 44 — C−B +210.06

Tags: `mid_round_fork`

Pos Δ: QB +139.0, RB +167.2, WR -29.0, TE -88.1, DST +21.0, K +0.0

### First fork — R6 (overall ~64)

- **B chose:** Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
- **C chose:** Joe Burrow (QB) · ADP 59.7 · curve 235 · marg +235.2 · actual +372.8
- Actual Δ at fork (C−B pick): 163.32
- C roster need: counts={'QB': 0, 'RB': 0, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 0, 'RB': 0, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Joe Burrow (QB) · ADP 59.7 · curve 235 · marg +235.2 · actual +372.8 ← chosen
2. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
3. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
4. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
5. Dak Prescott (QB) · ADP 69.8 · curve 215 · marg +215.5 · actual +116.5
6. Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9
7. Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +203.2 · actual +297.2
8. Javonte Williams (RB) · ADP 77.5 · curve 200 · marg +200.4 · actual +157.9

B alternatives at fork (ADP-feasible order):

1. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5 ← chosen
2. Tank Dell (WR) · ADP 57.5 · curve 240 · actual +140.0
3. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
4. Keenan Allen (WR) · ADP 63.5 · curve 228 · actual +184.4
5. Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9
6. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
7. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
8. George Kittle (TE) · ADP 66.7 · curve 222 · actual +236.6

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R7: took Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3; best shown alt Chase Brown (RB) · ADP 91.9 · curve 172 · marg +172.3 · actual +255.0; regret +191.7
  - B parallel pick: Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
- R8: took Jaylen Warren (RB) · ADP 79.6 · curve 196 · marg +196.3 · actual +124.1; best shown alt Chase Brown (RB) · ADP 91.9 · curve 172 · marg +172.3 · actual +255.0; regret +130.9
  - B parallel pick: Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · actual +181.6
- R10: took Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · marg +0.0 · actual +57.5; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +209.4
  - B parallel pick: Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
- R12: took Tyler Allgeier (RB) · ADP 125.1 · curve 107 · marg +0.0 · actual +106.2; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +150.4
  - B parallel pick: Jaleel McLaughlin (RB) · ADP 126.6 · curve 104 · actual +97.2
- R15: took Dontayvion Wicks (WR) · ADP 160.0 · curve 39 · marg +0.0 · actual +110.5; best shown alt Darnell Mooney (WR) · ADP 161.8 · curve 36 · marg +0.0 · actual +193.2; regret +82.7
  - B parallel pick: Cincinnati Defense (DST) · ADP 160.9 · curve 37 · actual +89.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Justin Jefferson (WR) 317.48 | Justin Jefferson (WR) 317.48 | +0.0 |
| 2 | Y | A.J. Brown (WR) 216.9 | A.J. Brown (WR) 216.9 | +0.0 |
| 3 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 4 | Y | Sam LaPorta (TE) 174.6 | Sam LaPorta (TE) 174.6 | +0.0 |
| 5 | Y | Amari Cooper (WR) 122.7 | Amari Cooper (WR) 122.7 | +0.0 |
| 6 | **N** | Zay Flowers (WR) 209.5 | Joe Burrow (QB) 372.82 | +163.3 |
| 7 | **N** | Jayden Reed (WR) 197.0 | Nick Chubb (RB) 63.3 | -133.7 |
| 8 | **N** | Jordan Love (QB) 233.86 | Jaylen Warren (RB) 124.1 | -109.8 |
| 9 | **N** | Tua Tagovailoa (QB) 181.58 | Baltimore Defense (DST) 110.0 | -71.6 |
| 10 | Y | Ezekiel Elliott (RB) 57.5 | Ezekiel Elliott (RB) 57.5 | +0.0 |
| 11 | **N** | Brock Bowers (TE) 262.7 | Rico Dowdle (RB) 197.8 | -64.9 |
| 12 | **N** | Jaleel McLaughlin (RB) 97.2 | Tyler Allgeier (RB) 106.2 | +9.0 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 14 | **N** | Jordan Addison (WR) 212.5 | Jakobi Meyers (WR) 218.0 | +5.5 |
| 15 | **N** | Cincinnati Defense (DST) 89.0 | Dontayvion Wicks (WR) 110.5 | +21.5 |

## Status

- Loss-case inspection: 🟢 artifact written
- V3: 🔴 still blocked — interpret failure mechanism before design
- UI: `marginal`
