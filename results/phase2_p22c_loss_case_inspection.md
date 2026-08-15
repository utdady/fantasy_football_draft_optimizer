# P2.2C left-tail loss-case inspection

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- cases: 10 (worst C−B)
- source: `results\phase2_p22c_valuation_cb_mechanism.json`

Decision-point inspection of worst C−B pairs: what C chose vs alternatives available, roster need, ADP-curve value, and actual PPR. Hypotheses only — not V3.

**Structural uses raw marginal on ADP-curve (no explicit replacement). First fork is on a shared board; later picks diverge. UI stays marginal.**

## Aggregate fork fingerprints

- fork tags: `{'structural_mid_te': 4, 'structural_skill_over_rb_qb': 6, 'mid_round_fork': 9, 'fork_pick_itself_large_actual_loss': 7, 'early_round_fork': 1}`
- fork rounds: `{5: 1, 6: 2, 7: 4, 8: 3}`
- C position at fork: `{'TE': 4, 'WR': 2, 'RB': 4}`
- B position at fork: `{'RB': 3, 'QB': 5, 'WR': 2}`
- fork pick itself (C vs B actual): C wins 1, C loses 9
- cases with post-fork hindsight regret ≥80 among shown alts: 10/10

### Read (provisional)

- First forks cluster in **R5–R8**, not late DST.
- At the fork, C often takes **TE/WR/RB** while B takes **QB/RB** (skill-over-QB and mid-TE tags).
- The fork pick itself usually **loses** on actual PPR in this worst-10 (C wins only rarely); large **post-fork** regrets also appear in 10/10.
- Early/mid DST-at-fork was **not** the dominant first-split pattern in this worst-10 set (DST timing shows up later on some boards).

### Working hypotheses (to confirm/reject from cases below)

1. **Replacement / scarcity timing** — C fills TE (or similar) via marginal when ADP still prefers QB/RB.
2. **Projection uncertainty** — ADP-curve/marginal ranked the fork pick above players who crushed in 2024 (esp. QB).
3. **Roster-sequence** — mid-draft fork reshapes the later board (always accompanied by post-fork regrets here).
4. **Irreducible late RB/TE variance** — not an optimizer bug.

Do **not** jump to V2 survival from narrative alone.

## Slot 1 seed 46 — C−B -282.48

Tags: `structural_mid_te, structural_skill_over_rb_qb, mid_round_fork`

Pos Δ: QB +61.6, RB -257.4, WR +52.8, TE -131.5, DST -8.0, K +0.0

### First fork — R7 (overall ~73)

- **B chose:** Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
- **C chose:** Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · marg +209.6 · actual +131.2
- Actual Δ at fork (C−B pick): 67.9
- C roster need: counts={'QB': 0, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=3
- B roster need: counts={'QB': 0, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · marg +209.6 · actual +131.2 ← chosen
2. Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +203.2 · actual +297.2
3. Evan Engram (TE) · ADP 79.5 · curve 197 · marg +196.5 · actual +89.5
4. Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · marg +178.7 · actual +181.6
5. Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4
6. Jared Goff (QB) · ADP 94.3 · curve 168 · marg +167.6 · actual +324.5
7. Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +158.0 · actual +355.8
8. David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5

B alternatives at fork (ADP-feasible order):

1. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3 ← chosen
2. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
3. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
4. Terry McLaurin (WR) · ADP 70.2 · curve 215 · actual +267.8
5. Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · actual +131.2
6. Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
7. Calvin Ridley (WR) · ADP 74.7 · curve 206 · actual +199.2
8. Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · marg +178.7 · actual +181.6; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +158.0 · actual +355.8; regret +174.2
  - B parallel pick: Jake Ferguson (TE) · ADP 89.2 · curve 178 · actual +104.4
- R9: took Tyjae Spears (RB) · ADP 91.4 · curve 173 · marg +0.0 · actual +113.6; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +242.2
  - B parallel pick: Chase Brown (RB) · ADP 91.9 · curve 172 · actual +255.0
- R11: took Tyler Lockett (WR) · ADP 106.6 · curve 144 · marg +0.0 · actual +121.0; best shown alt Justin Herbert (QB) · ADP 114.6 · curve 128 · marg +0.0 · actual +285.4; regret +164.4
  - B parallel pick: Trey Benson (RB) · ADP 108.5 · curve 140 · actual +47.0
- R12: took T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +0.0 · actual +86.5; best shown alt Jakobi Meyers (WR) · ADP 131.7 · curve 94 · marg +0.0 · actual +218.0; regret +131.5
  - B parallel pick: Brock Bowers (TE) · ADP 121.7 · curve 114 · actual +262.7
- R13: took Joshua Palmer (WR) · ADP 130.5 · curve 97 · marg +0.0 · actual +107.4; best shown alt Jakobi Meyers (WR) · ADP 131.7 · curve 94 · marg +0.0 · actual +218.0; regret +110.6
  - B parallel pick: Zach Charbonnet (RB) · ADP 130.7 · curve 96 · actual +186.9
- R14: took Dameon Pierce (RB) · ADP 151.4 · curve 56 · marg +0.0 · actual +43.5; best shown alt Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; regret +200.9
  - B parallel pick: Buffalo Defense (DST) · ADP 158.8 · curve 41 · actual +118.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | A.J. Brown (WR) 216.9 | A.J. Brown (WR) 216.9 | +0.0 |
| 3 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 4 | Y | Malik Nabers (WR) 273.6 | Malik Nabers (WR) 273.6 | +0.0 |
| 5 | Y | Stefon Diggs (WR) 121.92 | Stefon Diggs (WR) 121.92 | +0.0 |
| 6 | Y | Raheem Mostert (RB) 70.9 | Raheem Mostert (RB) 70.9 | +0.0 |
| 7 | **N** | Nick Chubb (RB) 63.3 | Kyle Pitts Sr. (TE) 131.2 | +67.9 |
| 8 | **N** | Jake Ferguson (TE) 104.4 | Tua Tagovailoa (QB) 181.58 | +77.2 |
| 9 | **N** | Chase Brown (RB) 255.0 | Tyjae Spears (RB) 113.6 | -141.4 |
| 10 | **N** | Tyler Lockett (WR) 121.0 | Baltimore Defense (DST) 110.0 | -11.0 |
| 11 | **N** | Trey Benson (RB) 47.0 | Tyler Lockett (WR) 121.0 | +74.0 |
| 12 | **N** | Brock Bowers (TE) 262.7 | T.J. Hockenson (TE) 86.5 | -176.2 |
| 13 | **N** | Zach Charbonnet (RB) 186.9 | Joshua Palmer (WR) 107.4 | -79.5 |
| 14 | **N** | Buffalo Defense (DST) 118.0 | Dameon Pierce (RB) 43.5 | -74.5 |
| 15 | **N** | Will Levis (QB) 119.94 | Quentin Johnston (WR) 174.7 | +54.8 |

## Slot 8 seed 44 — C−B -261.90

Tags: `structural_mid_te, structural_skill_over_rb_qb, mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB +0.0, RB -83.3, WR -40.5, TE -159.1, DST +21.0, K +0.0

### First fork — R8 (overall ~89)

- **B chose:** Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
- **C chose:** Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6
- Actual Δ at fork (C−B pick): -101.0
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=2
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6 ← chosen
2. Dalton Schultz (TE) · ADP 117.9 · curve 121 · marg +121.4 · actual +118.2
3. T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +119.9 · actual +86.5
4. Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7
5. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +0.0 · actual +204.6
6. Jaylen Warren (RB) · ADP 79.6 · curve 196 · marg +0.0 · actual +124.1
7. Xavier Worthy (WR) · ADP 81.9 · curve 192 · marg +0.0 · actual +187.2
8. Devin Singletary (RB) · ADP 87.9 · curve 180 · marg +0.0 · actual +96.6

B alternatives at fork (ADP-feasible order):

1. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6 ← chosen
2. Jaylen Warren (RB) · ADP 79.6 · curve 196 · actual +124.1
3. Xavier Worthy (WR) · ADP 81.9 · curve 192 · actual +187.2
4. Devin Singletary (RB) · ADP 87.9 · curve 180 · actual +96.6
5. Keon Coleman (WR) · ADP 88.1 · curve 180 · actual +111.5
6. Tua Tagovailoa (QB) · ADP 88.6 · curve 179 · actual +181.6
7. Jaxon Smith-Njigba (WR) · ADP 90.5 · curve 175 · actual +253.0
8. Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jared Goff (QB) · ADP 94.3 · curve 168 · marg +0.0 · actual +324.5; regret +214.5
  - B parallel pick: Jaxon Smith-Njigba (WR) · ADP 90.5 · curve 175 · actual +253.0
- R10: took Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · marg +0.0 · actual +57.5; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +226.5
  - B parallel pick: Jerome Ford (RB) · ADP 98.5 · curve 159 · actual +134.0
- R12: took Kirk Cousins (QB) · ADP 130.1 · curve 98 · marg +0.0 · actual +176.3; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +80.3
  - B parallel pick: Ty Chandler (RB) · ADP 130.3 · curve 97 · actual +28.4
- R14: took Jordan Addison (WR) · ADP 134.1 · curve 90 · marg +0.0 · actual +212.5; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +153.3
  - B parallel pick: Justin Fields (QB) · ADP 134.7 · curve 89 · actual +119.1

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Marvin Harrison Jr. (WR) 196.5 | Marvin Harrison Jr. (WR) 196.5 | +0.0 |
| 3 | Y | Isiah Pacheco (RB) 56.9 | Isiah Pacheco (RB) 56.9 | +0.0 |
| 4 | Y | Patrick Mahomes (QB) 283.02 | Patrick Mahomes (QB) 283.02 | +0.0 |
| 5 | Y | Amari Cooper (WR) 122.7 | Amari Cooper (WR) 122.7 | +0.0 |
| 6 | Y | Christian Kirk (WR) 70.9 | Christian Kirk (WR) 70.9 | +0.0 |
| 7 | Y | Jayden Reed (WR) 197.0 | Jayden Reed (WR) 197.0 | +0.0 |
| 8 | **N** | Najee Harris (RB) 204.6 | Dallas Goedert (TE) 103.6 | -101.0 |
| 9 | **N** | Jaxon Smith-Njigba (WR) 253.0 | Baltimore Defense (DST) 110.0 | -143.0 |
| 10 | **N** | Jerome Ford (RB) 134.0 | Ezekiel Elliott (RB) 57.5 | -76.5 |
| 11 | **N** | Brock Bowers (TE) 262.7 | Rico Dowdle (RB) 197.8 | -64.9 |
| 12 | **N** | Ty Chandler (RB) 28.4 | Kirk Cousins (QB) 176.32 | +147.9 |
| 13 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 14 | **N** | Justin Fields (QB) 119.14 | Jordan Addison (WR) 212.5 | +93.4 |
| 15 | **N** | Cincinnati Defense (DST) 89.0 | Will Levis (QB) 119.94 | +30.9 |

## Slot 10 seed 43 — C−B -164.50

Tags: `structural_skill_over_rb_qb, mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB +0.0, RB -197.8, WR +25.1, TE -13.8, DST +22.0, K +0.0

### First fork — R6 (overall ~63)

- **B chose:** Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- **C chose:** Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9
- Actual Δ at fork (C−B pick): -92.46
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9 ← chosen
2. D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5
3. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
4. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9
5. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
6. Jayden Reed (WR) · ADP 65.1 · curve 225 · marg +224.7 · actual +197.0
7. George Kittle (TE) · ADP 66.7 · curve 222 · marg +221.5 · actual +236.6
8. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6

B alternatives at fork (ADP-feasible order):

1. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4 ← chosen
2. Christian Kirk (WR) · ADP 55.6 · curve 243 · actual +70.9
3. D'Andre Swift (RB) · ADP 56.5 · curve 241 · actual +214.5
4. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
5. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
6. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · actual +175.9
7. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
8. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +158.3
  - B parallel pick: Calvin Ridley (WR) · ADP 74.7 · curve 206 · actual +199.2
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +156.9
  - B parallel pick: Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9
- R10: took Rome Odunze (WR) · ADP 97.7 · curve 161 · marg +0.0 · actual +144.9; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +139.1
  - B parallel pick: Ladd McConkey (WR) · ADP 98.4 · curve 160 · actual +240.9
- R12: took T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +0.0 · actual +86.5; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +170.1
  - B parallel pick: Rico Dowdle (RB) · ADP 118.9 · curve 119 · actual +197.8
- R13: took Ty Chandler (RB) · ADP 130.3 · curve 97 · marg +0.0 · actual +28.4; best shown alt Jordan Mason (RB) · ADP 149.1 · curve 60 · marg +0.0 · actual +115.0; regret +86.6
  - B parallel pick: Aaron Rodgers (QB) · ADP 130.4 · curve 97 · actual +256.6
- R14: took Dallas Defense (DST) · ADP 139.3 · curve 80 · marg +0.0 · actual +88.0; best shown alt Josh Downs (WR) · ADP 155.9 · curve 47 · marg +0.0 · actual +183.5; regret +95.5
  - B parallel pick: Dallas Defense (DST) · ADP 139.3 · curve 80 · actual +88.0
- R15: took Jordan Mason (RB) · ADP 149.1 · curve 60 · marg +0.0 · actual +115.0; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +151.0
  - B parallel pick: Deshaun Watson (QB) · ADP 149.3 · curve 60 · actual +76.7

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | CeeDee Lamb (WR) 263.4 | CeeDee Lamb (WR) 263.4 | +0.0 |
| 2 | Y | Bijan Robinson (RB) 341.7 | Bijan Robinson (RB) 341.7 | +0.0 |
| 3 | Y | Chris Olave (WR) 76.7 | Chris Olave (WR) 76.7 | +0.0 |
| 4 | Y | Alvin Kamara (RB) 265.3 | Alvin Kamara (RB) 265.3 | +0.0 |
| 5 | Y | Lamar Jackson (QB) 430.38 | Lamar Jackson (QB) 430.38 | +0.0 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | Christian Kirk (WR) 70.9 | -92.5 |
| 7 | Y | Chris Godwin Jr. (WR) 137.8 | Chris Godwin Jr. (WR) 137.8 | +0.0 |
| 8 | **N** | Calvin Ridley (WR) 199.2 | Jake Ferguson (TE) 104.4 | -94.8 |
| 9 | **N** | Rome Odunze (WR) 144.9 | Baltimore Defense (DST) 110.0 | -34.9 |
| 10 | **N** | Ladd McConkey (WR) 240.9 | Rome Odunze (WR) 144.9 | -96.0 |
| 11 | **N** | Dalton Schultz (TE) 118.2 | Khalil Shakir (WR) 182.5 | +64.3 |
| 12 | **N** | Rico Dowdle (RB) 197.8 | T.J. Hockenson (TE) 86.5 | -111.3 |
| 13 | **N** | Aaron Rodgers (QB) 256.58 | Ty Chandler (RB) 28.4 | -228.2 |
| 14 | Y | Dallas Defense (DST) 88.0 | Dallas Defense (DST) 88.0 | +0.0 |
| 15 | **N** | Deshaun Watson (QB) 76.72 | Jordan Mason (RB) 115.0 | +38.3 |

## Slot 6 seed 42 — C−B -138.30

Tags: `mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB +0.0, RB +130.8, WR -261.1, TE +0.0, DST -8.0, K +0.0

### First fork — R7 (overall ~78)

- **B chose:** Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0
- **C chose:** Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
- Actual Δ at fork (C−B pick): -167.7
- C roster need: counts={'QB': 0, 'RB': 1, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6, min_need=3
- B roster need: counts={'QB': 0, 'RB': 1, 'WR': 4, 'TE': 1, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3 ← chosen
2. Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9
3. Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9
4. Jaylen Warren (RB) · ADP 79.6 · curve 196 · marg +196.3 · actual +124.1
5. Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7
6. Jonathon Brooks (RB) · ADP 85.4 · curve 185 · marg +185.0 · actual +7.5
7. Devin Singletary (RB) · ADP 87.9 · curve 180 · marg +180.1 · actual +96.6
8. Austin Ekeler (RB) · ADP 88.0 · curve 180 · marg +179.9 · actual +132.3

B alternatives at fork (ADP-feasible order):

1. Jayden Reed (WR) · ADP 65.1 · curve 225 · actual +197.0 ← chosen
2. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
3. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
4. Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · actual +131.2
5. Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
6. Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
7. Calvin Ridley (WR) · ADP 74.7 · curve 206 · actual +199.2
8. Jaylen Warren (RB) · ADP 79.6 · curve 196 · actual +124.1

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took Jordan Love (QB) · ADP 73.2 · curve 209 · marg +208.8 · actual +233.9; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +158.0 · actual +355.8; regret +122.0
  - B parallel pick: Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6
- R10: took Tyler Lockett (WR) · ADP 106.6 · curve 144 · marg +0.0 · actual +121.0; best shown alt Justin Herbert (QB) · ADP 114.6 · curve 128 · marg +0.0 · actual +285.4; regret +164.4
  - B parallel pick: Jameson Williams (WR) · ADP 107.8 · curve 141 · actual +212.2
- R11: took Blake Corum (RB) · ADP 110.3 · curve 136 · marg +0.0 · actual +33.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +229.2
  - B parallel pick: Courtland Sutton (WR) · ADP 110.8 · curve 135 · actual +240.3
- R14: took Ray Davis (RB) · ADP 147.7 · curve 63 · marg +0.0 · actual +116.1; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +249.7
  - B parallel pick: Ray Davis (RB) · ADP 147.7 · curve 63 · actual +116.1
- R15: took Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +121.4
  - B parallel pick: Buffalo Defense (DST) · ADP 158.8 · curve 41 · actual +118.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Marvin Harrison Jr. (WR) 196.5 | Marvin Harrison Jr. (WR) 196.5 | +0.0 |
| 3 | Y | Travis Kelce (TE) 195.4 | Travis Kelce (TE) 195.4 | +0.0 |
| 4 | Y | Nico Collins (WR) 210.6 | Nico Collins (WR) 210.6 | +0.0 |
| 5 | Y | Brandon Aiyuk (WR) 62.4 | Brandon Aiyuk (WR) 62.4 | +0.0 |
| 6 | Y | Christian Kirk (WR) 70.9 | Christian Kirk (WR) 70.9 | +0.0 |
| 7 | **N** | Jayden Reed (WR) 197.0 | Zamir White (RB) 29.3 | -167.7 |
| 8 | Y | Jordan Love (QB) 233.86 | Jordan Love (QB) 233.86 | +0.0 |
| 9 | **N** | Tyjae Spears (RB) 113.6 | Baltimore Defense (DST) 110.0 | -3.6 |
| 10 | **N** | Jameson Williams (WR) 212.2 | Tyler Lockett (WR) 121.0 | -91.2 |
| 11 | **N** | Courtland Sutton (WR) 240.3 | Blake Corum (RB) 33.5 | -206.8 |
| 12 | Y | Matthew Stafford (QB) 214.58 | Matthew Stafford (QB) 214.58 | +0.0 |
| 13 | **N** | Elijah Mitchell (RB) 0.0 | Trevor Lawrence (QB) 145.2 | +145.2 |
| 14 | Y | Ray Davis (RB) 116.1 | Ray Davis (RB) 116.1 | +0.0 |
| 15 | **N** | Buffalo Defense (DST) 118.0 | Bucky Irving (RB) 244.4 | +126.4 |

## Slot 2 seed 45 — C−B -112.14

Tags: `structural_mid_te, structural_skill_over_rb_qb, mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB +0.0, RB +0.0, WR -138.3, TE +46.2, DST -20.0, K +0.0

### First fork — R8 (overall ~95)

- **B chose:** Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2
- **C chose:** David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5
- Actual Δ at fork (C−B pick): -148.74
- C roster need: counts={'QB': 1, 'RB': 4, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=2
- B roster need: counts={'QB': 1, 'RB': 4, 'WR': 2, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5 ← chosen
2. Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6
3. Dalton Schultz (TE) · ADP 117.9 · curve 121 · marg +121.4 · actual +118.2
4. T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +119.9 · actual +86.5
5. Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7
6. Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +0.0 · actual +297.2
7. Devin Singletary (RB) · ADP 87.9 · curve 180 · marg +0.0 · actual +96.6
8. Keon Coleman (WR) · ADP 88.1 · curve 180 · marg +0.0 · actual +111.5

B alternatives at fork (ADP-feasible order):

1. Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2 ← chosen
2. Devin Singletary (RB) · ADP 87.9 · curve 180 · actual +96.6
3. Keon Coleman (WR) · ADP 88.1 · curve 180 · actual +111.5
4. Jaxon Smith-Njigba (WR) · ADP 90.5 · curve 175 · actual +253.0
5. Chase Brown (RB) · ADP 91.9 · curve 172 · actual +255.0
6. Diontae Johnson (WR) · ADP 92.1 · curve 172 · actual +89.1
7. Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
8. Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R10: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jameson Williams (WR) · ADP 107.8 · curve 141 · marg +0.0 · actual +212.2; regret +102.2
  - B parallel pick: Tyler Lockett (WR) · ADP 106.6 · curve 144 · actual +121.0
- R11: took Blake Corum (RB) · ADP 110.3 · curve 136 · marg +0.0 · actual +33.5; best shown alt Justin Herbert (QB) · ADP 114.6 · curve 128 · marg +0.0 · actual +285.4; regret +251.9
  - B parallel pick: Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · actual +284.0
- R12: took Joshua Palmer (WR) · ADP 130.5 · curve 97 · marg +0.0 · actual +107.4; best shown alt Jordan Addison (WR) · ADP 134.1 · curve 90 · marg +0.0 · actual +212.5; regret +105.1
  - B parallel pick: Zach Charbonnet (RB) · ADP 130.7 · curve 96 · actual +186.9
- R14: took Quentin Johnston (WR) · ADP 152.2 · curve 54 · marg +0.0 · actual +174.7; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +191.1
  - B parallel pick: Taysom Hill (TE) · ADP 155.9 · curve 47 · actual +102.3
- R15: took Josh Downs (WR) · ADP 155.9 · curve 47 · marg +0.0 · actual +183.5; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +182.3
  - B parallel pick: Pittsburgh Defense (DST) · ADP 157.8 · curve 43 · actual +130.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 3 | Y | Isiah Pacheco (RB) 56.9 | Isiah Pacheco (RB) 56.9 | +0.0 |
| 4 | Y | Kenneth Walker (RB) 181.2 | Kenneth Walker (RB) 181.2 | +0.0 |
| 5 | Y | Jalen Hurts (QB) 315.12 | Jalen Hurts (QB) 315.12 | +0.0 |
| 6 | Y | George Pickens (WR) 164.4 | George Pickens (WR) 164.4 | +0.0 |
| 7 | Y | Rhamondre Stevenson (RB) 175.9 | Rhamondre Stevenson (RB) 175.9 | +0.0 |
| 8 | **N** | Kyler Murray (QB) 297.24 | David Njoku (TE) 148.5 | -148.7 |
| 9 | **N** | Devin Singletary (RB) 96.6 | Kyler Murray (QB) 297.24 | +200.6 |
| 10 | **N** | Tyler Lockett (WR) 121.0 | Baltimore Defense (DST) 110.0 | -11.0 |
| 11 | **N** | Brian Thomas Jr. (WR) 284.0 | Blake Corum (RB) 33.5 | -250.5 |
| 12 | **N** | Zach Charbonnet (RB) 186.9 | Joshua Palmer (WR) 107.4 | -79.5 |
| 13 | **N** | Jordan Addison (WR) 212.5 | Zach Charbonnet (RB) 186.9 | -25.6 |
| 14 | **N** | Taysom Hill (TE) 102.34 | Quentin Johnston (WR) 174.7 | +72.4 |
| 15 | **N** | Pittsburgh Defense (DST) 130.0 | Josh Downs (WR) 183.5 | +53.5 |

## Slot 11 seed 43 — C−B -83.24

Tags: `early_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB -147.4, RB +76.8, WR -12.7, TE +0.0, DST +0.0, K +0.0

### First fork — R5 (overall ~59)

- **B chose:** Lamar Jackson (QB) · ADP 44.2 · curve 266 · actual +430.4
- **C chose:** David Montgomery (RB) · ADP 54.6 · curve 245 · marg +245.2 · actual +221.7
- Actual Δ at fork (C−B pick): -208.66
- C roster need: counts={'QB': 1, 'RB': 1, 'WR': 1, 'TE': 1, 'DST': 0, 'K': 0}, slack=6, min_need=5
- B roster need: counts={'QB': 1, 'RB': 1, 'WR': 1, 'TE': 1, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. David Montgomery (RB) · ADP 54.6 · curve 245 · marg +245.2 · actual +221.7 ← chosen
2. Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9
3. D'Andre Swift (RB) · ADP 56.5 · curve 241 · marg +241.5 · actual +214.5
4. Zay Flowers (WR) · ADP 56.8 · curve 241 · marg +240.9 · actual +209.5
5. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · marg +230.7 · actual +175.9
6. Rashee Rice (WR) · ADP 64.2 · curve 226 · marg +226.4 · actual +64.9
7. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
8. Jayden Reed (WR) · ADP 65.1 · curve 225 · marg +224.7 · actual +197.0

B alternatives at fork (ADP-feasible order):

1. Lamar Jackson (QB) · ADP 44.2 · curve 266 · actual +430.4 ← chosen
2. David Montgomery (RB) · ADP 54.6 · curve 245 · actual +221.7
3. Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
4. Christian Kirk (WR) · ADP 55.6 · curve 243 · actual +70.9
5. D'Andre Swift (RB) · ADP 56.5 · curve 241 · actual +214.5
6. Zay Flowers (WR) · ADP 56.8 · curve 241 · actual +209.5
7. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
8. Rhamondre Stevenson (RB) · ADP 62.0 · curve 231 · actual +175.9

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R6: took Christian Kirk (WR) · ADP 55.6 · curve 243 · marg +243.2 · actual +70.9; best shown alt George Kittle (TE) · ADP 66.7 · curve 222 · marg +221.5 · actual +236.6; regret +165.7
  - B parallel pick: Anthony Richardson Sr. (QB) · ADP 55.2 · curve 244 · actual +163.4
- R7: took Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3; best shown alt Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7; regret +171.4
  - B parallel pick: Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
- R8: took Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9; best shown alt Xavier Worthy (WR) · ADP 81.9 · curve 192 · marg +191.8 · actual +187.2; regret +105.3
  - B parallel pick: Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +156.9
  - B parallel pick: Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9
- R10: took Rome Odunze (WR) · ADP 97.7 · curve 161 · marg +0.0 · actual +144.9; best shown alt Chuba Hubbard (RB) · ADP 108.8 · curve 139 · marg +0.0 · actual +241.6; regret +96.7
  - B parallel pick: Jerome Ford (RB) · ADP 98.5 · curve 159 · actual +134.0
- R11: took T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +0.0 · actual +86.5; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +170.1
  - B parallel pick: Rico Dowdle (RB) · ADP 118.9 · curve 119 · actual +197.8
- R12: took Tyler Allgeier (RB) · ADP 125.1 · curve 107 · marg +0.0 · actual +106.2; best shown alt Aaron Rodgers (QB) · ADP 130.4 · curve 97 · marg +0.0 · actual +256.6; regret +150.4
  - B parallel pick: Trevor Lawrence (QB) · ADP 126.7 · curve 104 · actual +145.2
- R14: took NY Jets Defense (DST) · ADP 140.8 · curve 77 · marg +0.0 · actual +89.0; best shown alt Josh Downs (WR) · ADP 155.9 · curve 47 · marg +0.0 · actual +183.5; regret +94.5
  - B parallel pick: NY Jets Defense (DST) · ADP 140.8 · curve 77 · actual +89.0
- R15: took Xavier Legette (WR) · ADP 141.3 · curve 76 · marg +0.0 · actual +125.1; best shown alt Geno Smith (QB) · ADP 159.8 · curve 39 · marg +0.0 · actual +266.0; regret +140.9
  - B parallel pick: Xavier Legette (WR) · ADP 141.3 · curve 76 · actual +125.1

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | CeeDee Lamb (WR) 263.4 | CeeDee Lamb (WR) 263.4 | +0.0 |
| 2 | Y | Bijan Robinson (RB) 341.7 | Bijan Robinson (RB) 341.7 | +0.0 |
| 3 | Y | Sam LaPorta (TE) 174.6 | Sam LaPorta (TE) 174.6 | +0.0 |
| 4 | Y | Patrick Mahomes (QB) 283.02 | Patrick Mahomes (QB) 283.02 | +0.0 |
| 5 | **N** | Lamar Jackson (QB) 430.38 | David Montgomery (RB) 221.72 | -208.7 |
| 6 | **N** | Anthony Richardson Sr. (QB) 163.36 | Christian Kirk (WR) 70.9 | -92.5 |
| 7 | **N** | Chris Godwin Jr. (WR) 137.8 | Zamir White (RB) 29.3 | -108.5 |
| 8 | Y | Zack Moss (RB) 81.9 | Zack Moss (RB) 81.9 | +0.0 |
| 9 | **N** | Rome Odunze (WR) 144.9 | Baltimore Defense (DST) 110.0 | -34.9 |
| 10 | **N** | Jerome Ford (RB) 134.0 | Rome Odunze (WR) 144.9 | +10.9 |
| 11 | **N** | Rico Dowdle (RB) 197.8 | T.J. Hockenson (TE) 86.5 | -111.3 |
| 12 | **N** | Trevor Lawrence (QB) 145.2 | Tyler Allgeier (RB) 106.2 | -39.0 |
| 13 | **N** | Baltimore Defense (DST) 110.0 | Zach Charbonnet (RB) 186.9 | +76.9 |
| 14 | Y | NY Jets Defense (DST) 89.0 | NY Jets Defense (DST) 89.0 | +0.0 |
| 15 | Y | Xavier Legette (WR) 125.1 | Xavier Legette (WR) 125.1 | +0.0 |

## Slot 5 seed 44 — C−B -80.46

Tags: `mid_round_fork`

Pos Δ: QB -93.2, RB -199.9, WR +174.5, TE +46.2, DST -8.0, K +0.0

### First fork — R7 (overall ~77)

- **B chose:** Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9
- **C chose:** Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
- Actual Δ at fork (C−B pick): -1.6
- C roster need: counts={'QB': 1, 'RB': 1, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=3
- B roster need: counts={'QB': 1, 'RB': 1, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3 ← chosen
2. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
3. Javonte Williams (RB) · ADP 77.5 · curve 200 · marg +200.4 · actual +157.9
4. Evan Engram (TE) · ADP 79.5 · curve 197 · marg +196.5 · actual +89.5
5. Jaylen Warren (RB) · ADP 79.6 · curve 196 · marg +196.3 · actual +124.1
6. Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7
7. Jonathon Brooks (RB) · ADP 85.4 · curve 185 · marg +185.0 · actual +7.5
8. Devin Singletary (RB) · ADP 87.9 · curve 180 · marg +180.1 · actual +96.6

B alternatives at fork (ADP-feasible order):

1. Rashee Rice (WR) · ADP 64.2 · curve 226 · actual +64.9 ← chosen
2. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
3. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
4. Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
5. Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2
6. Javonte Williams (RB) · ADP 77.5 · curve 200 · actual +157.9
7. Evan Engram (TE) · ADP 79.5 · curve 197 · actual +89.5
8. Jaylen Warren (RB) · ADP 79.6 · curve 196 · actual +124.1

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +114.2
  - B parallel pick: Jaylen Warren (RB) · ADP 79.6 · curve 196 · actual +124.1
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6
- R10: took Romeo Doubs (WR) · ADP 103.0 · curve 151 · marg +0.0 · actual +132.1; best shown alt Justin Herbert (QB) · ADP 114.6 · curve 128 · marg +0.0 · actual +285.4; regret +153.3
  - B parallel pick: DeAndre Hopkins (WR) · ADP 104.5 · curve 148 · actual +147.0
- R12: took Ty Chandler (RB) · ADP 130.3 · curve 97 · marg +0.0 · actual +28.4; best shown alt Jordan Addison (WR) · ADP 134.1 · curve 90 · marg +0.0 · actual +212.5; regret +184.1
  - B parallel pick: Aaron Rodgers (QB) · ADP 130.4 · curve 97 · actual +256.6
- R13: took Joshua Palmer (WR) · ADP 130.5 · curve 97 · marg +0.0 · actual +107.4; best shown alt Jordan Addison (WR) · ADP 134.1 · curve 90 · marg +0.0 · actual +212.5; regret +105.1
  - B parallel pick: Zach Charbonnet (RB) · ADP 130.7 · curve 96 · actual +186.9
- R14: took Jordan Addison (WR) · ADP 134.1 · curve 90 · marg +0.0 · actual +212.5; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +153.3
  - B parallel pick: Taysom Hill (TE) · ADP 155.9 · curve 47 · actual +102.3
- R15: took Taysom Hill (TE) · ADP 155.9 · curve 47 · marg +0.0 · actual +102.3; best shown alt Darnell Mooney (WR) · ADP 161.8 · curve 36 · marg +0.0 · actual +193.2; regret +90.9
  - B parallel pick: Buffalo Defense (DST) · ADP 158.8 · curve 41 · actual +118.0

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Marvin Harrison Jr. (WR) 196.5 | Marvin Harrison Jr. (WR) 196.5 | +0.0 |
| 3 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 4 | Y | Stefon Diggs (WR) 121.92 | Stefon Diggs (WR) 121.92 | +0.0 |
| 5 | Y | DJ Moore (WR) 238.1 | DJ Moore (WR) 238.1 | +0.0 |
| 6 | Y | Anthony Richardson Sr. (QB) 163.36 | Anthony Richardson Sr. (QB) 163.36 | +0.0 |
| 7 | **N** | Rashee Rice (WR) 64.9 | Nick Chubb (RB) 63.3 | -1.6 |
| 8 | **N** | Jaylen Warren (RB) 124.1 | David Njoku (TE) 148.5 | +24.4 |
| 9 | **N** | Tyjae Spears (RB) 113.6 | Baltimore Defense (DST) 110.0 | -3.6 |
| 10 | **N** | DeAndre Hopkins (WR) 147.0 | Romeo Doubs (WR) 132.1 | -14.9 |
| 11 | **N** | Mike Williams (WR) 56.8 | Brian Thomas Jr. (WR) 284.0 | +227.2 |
| 12 | **N** | Aaron Rodgers (QB) 256.58 | Ty Chandler (RB) 28.4 | -228.2 |
| 13 | **N** | Zach Charbonnet (RB) 186.9 | Joshua Palmer (WR) 107.4 | -79.5 |
| 14 | **N** | Taysom Hill (TE) 102.34 | Jordan Addison (WR) 212.5 | +110.2 |
| 15 | **N** | Buffalo Defense (DST) 118.0 | Taysom Hill (TE) 102.34 | -15.7 |

## Slot 2 seed 46 — C−B -65.60

Tags: `structural_mid_te, structural_skill_over_rb_qb, mid_round_fork`

Pos Δ: QB +0.0, RB +112.1, WR -59.7, TE -139.0, DST +21.0, K +0.0

### First fork — R8 (overall ~95)

- **B chose:** Austin Ekeler (RB) · ADP 88.0 · curve 180 · actual +132.3
- **C chose:** Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4
- Actual Δ at fork (C−B pick): -27.9
- C roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=2
- B roster need: counts={'QB': 1, 'RB': 2, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4 ← chosen
2. David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5
3. Dallas Goedert (TE) · ADP 105.5 · curve 146 · marg +145.7 · actual +103.6
4. Dalton Schultz (TE) · ADP 117.9 · curve 121 · marg +121.4 · actual +118.2
5. T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +119.9 · actual +86.5
6. Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7
7. Austin Ekeler (RB) · ADP 88.0 · curve 180 · marg +0.0 · actual +132.3
8. Tyjae Spears (RB) · ADP 91.4 · curve 173 · marg +0.0 · actual +113.6

B alternatives at fork (ADP-feasible order):

1. Austin Ekeler (RB) · ADP 88.0 · curve 180 · actual +132.3 ← chosen
2. Jake Ferguson (TE) · ADP 89.2 · curve 178 · actual +104.4
3. Tyjae Spears (RB) · ADP 91.4 · curve 173 · actual +113.6
4. Chase Brown (RB) · ADP 91.9 · curve 172 · actual +255.0
5. Diontae Johnson (WR) · ADP 92.1 · curve 172 · actual +89.1
6. Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
7. Rome Odunze (WR) · ADP 97.7 · curve 161 · actual +144.9
8. Brian Robinson (RB) · ADP 97.9 · curve 161 · actual +159.8

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R9: took Austin Ekeler (RB) · ADP 88.0 · curve 180 · marg +0.0 · actual +132.3; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +223.5
  - B parallel pick: Jake Ferguson (TE) · ADP 89.2 · curve 178 · actual +104.4
- R10: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jameson Williams (WR) · ADP 107.8 · curve 141 · marg +0.0 · actual +212.2; regret +102.2
  - B parallel pick: DeAndre Hopkins (WR) · ADP 104.5 · curve 148 · actual +147.0
- R11: took DeAndre Hopkins (WR) · ADP 104.5 · curve 148 · marg +0.0 · actual +147.0; best shown alt Brian Thomas Jr. (WR) · ADP 114.2 · curve 129 · marg +0.0 · actual +284.0; regret +137.0
  - B parallel pick: Jameson Williams (WR) · ADP 107.8 · curve 141 · actual +212.2
- R12: took T.J. Hockenson (TE) · ADP 118.7 · curve 120 · marg +0.0 · actual +86.5; best shown alt Jerry Jeudy (WR) · ADP 132.9 · curve 92 · marg +0.0 · actual +240.9; regret +154.4
  - B parallel pick: Brock Bowers (TE) · ADP 121.7 · curve 114 · actual +262.7
- R14: took Isaiah Likely (TE) · ADP 152.0 · curve 55 · marg +0.0 · actual +123.7; best shown alt Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; regret +120.7
  - B parallel pick: Isaiah Likely (TE) · ADP 152.0 · curve 55 · actual +123.7

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Breece Hall (RB) 240.9 | Breece Hall (RB) 240.9 | +0.0 |
| 2 | Y | A.J. Brown (WR) 216.9 | A.J. Brown (WR) 216.9 | +0.0 |
| 3 | Y | Deebo Samuel Sr. (WR) 155.6 | Deebo Samuel Sr. (WR) 155.6 | +0.0 |
| 4 | Y | Jalen Hurts (QB) 315.12 | Jalen Hurts (QB) 315.12 | +0.0 |
| 5 | Y | Stefon Diggs (WR) 121.92 | Stefon Diggs (WR) 121.92 | +0.0 |
| 6 | Y | Rashee Rice (WR) 64.9 | Rashee Rice (WR) 64.9 | +0.0 |
| 7 | Y | Nick Chubb (RB) 63.3 | Nick Chubb (RB) 63.3 | +0.0 |
| 8 | **N** | Austin Ekeler (RB) 132.3 | Jake Ferguson (TE) 104.4 | -27.9 |
| 9 | **N** | Jake Ferguson (TE) 104.4 | Austin Ekeler (RB) 132.3 | +27.9 |
| 10 | **N** | DeAndre Hopkins (WR) 147.0 | Baltimore Defense (DST) 110.0 | -37.0 |
| 11 | **N** | Jameson Williams (WR) 212.2 | DeAndre Hopkins (WR) 147.0 | -65.2 |
| 12 | **N** | Brock Bowers (TE) 262.7 | T.J. Hockenson (TE) 86.5 | -176.2 |
| 13 | **N** | Jordan Addison (WR) 212.5 | Jakobi Meyers (WR) 218.0 | +5.5 |
| 14 | Y | Isaiah Likely (TE) 123.7 | Isaiah Likely (TE) 123.7 | +0.0 |
| 15 | **N** | Cincinnati Defense (DST) 89.0 | Bucky Irving (RB) 244.4 | +155.4 |

## Slot 5 seed 45 — C−B -48.40

Tags: `structural_skill_over_rb_qb, mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB -57.7, RB -255.0, WR +244.2, TE +28.1, DST -8.0, K +0.0

### First fork — R6 (overall ~68)

- **B chose:** Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8
- **C chose:** George Pickens (WR) · ADP 59.8 · curve 235 · marg +235.0 · actual +164.4
- Actual Δ at fork (C−B pick): -208.42
- C roster need: counts={'QB': 1, 'RB': 3, 'WR': 1, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=4
- B roster need: counts={'QB': 1, 'RB': 3, 'WR': 1, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. George Pickens (WR) · ADP 59.8 · curve 235 · marg +235.0 · actual +164.4 ← chosen
2. Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9
3. Nick Chubb (RB) · ADP 65.0 · curve 225 · marg +224.9 · actual +63.3
4. Najee Harris (RB) · ADP 67.1 · curve 221 · marg +220.8 · actual +204.6
5. Zamir White (RB) · ADP 67.8 · curve 219 · marg +219.4 · actual +29.3
6. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · marg +218.2 · actual +137.8
7. Terry McLaurin (WR) · ADP 70.2 · curve 215 · marg +214.7 · actual +267.8
8. Kyle Pitts Sr. (TE) · ADP 72.8 · curve 210 · marg +209.6 · actual +131.2

B alternatives at fork (ADP-feasible order):

1. Joe Burrow (QB) · ADP 59.7 · curve 235 · actual +372.8 ← chosen
2. George Pickens (WR) · ADP 59.8 · curve 235 · actual +164.4
3. Raheem Mostert (RB) · ADP 64.1 · curve 227 · actual +70.9
4. Nick Chubb (RB) · ADP 65.0 · curve 225 · actual +63.3
5. Najee Harris (RB) · ADP 67.1 · curve 221 · actual +204.6
6. Zamir White (RB) · ADP 67.8 · curve 219 · actual +29.3
7. Chris Godwin Jr. (WR) · ADP 68.4 · curve 218 · actual +137.8
8. Terry McLaurin (WR) · ADP 70.2 · curve 215 · actual +267.8

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R7: took Raheem Mostert (RB) · ADP 64.1 · curve 227 · marg +226.6 · actual +70.9; best shown alt Terry McLaurin (WR) · ADP 70.2 · curve 215 · marg +214.7 · actual +267.8; regret +196.9
  - B parallel pick: George Pickens (WR) · ADP 59.8 · curve 235 · actual +164.4
- R8: took David Njoku (TE) · ADP 101.1 · curve 154 · marg +154.3 · actual +148.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +114.0 · actual +262.7; regret +114.2
  - B parallel pick: Calvin Ridley (WR) · ADP 74.7 · curve 206 · actual +199.2
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Jayden Daniels (QB) · ADP 99.2 · curve 158 · marg +0.0 · actual +355.8; regret +245.8
  - B parallel pick: Chase Brown (RB) · ADP 91.9 · curve 172 · actual +255.0
- R14: took Khalil Herbert (RB) · ADP 136.4 · curve 85 · marg +0.0 · actual +31.5; best shown alt Baker Mayfield (QB) · ADP 156.0 · curve 47 · marg +0.0 · actual +365.8; regret +334.3
  - B parallel pick: Cole Kmet (TE) · ADP 137.1 · curve 84 · actual +120.4

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Christian McCaffrey (RB) 47.8 | Christian McCaffrey (RB) 47.8 | +0.0 |
| 2 | Y | Saquon Barkley (RB) 355.3 | Saquon Barkley (RB) 355.3 | +0.0 |
| 3 | Y | Cooper Kupp (WR) 175.0 | Cooper Kupp (WR) 175.0 | +0.0 |
| 4 | Y | Kenneth Walker (RB) 181.2 | Kenneth Walker (RB) 181.2 | +0.0 |
| 5 | Y | Jalen Hurts (QB) 315.12 | Jalen Hurts (QB) 315.12 | +0.0 |
| 6 | **N** | Joe Burrow (QB) 372.82 | George Pickens (WR) 164.4 | -208.4 |
| 7 | **N** | George Pickens (WR) 164.4 | Raheem Mostert (RB) 70.9 | -93.5 |
| 8 | **N** | Calvin Ridley (WR) 199.2 | David Njoku (TE) 148.5 | -50.7 |
| 9 | **N** | Chase Brown (RB) 255.0 | Baltimore Defense (DST) 110.0 | -145.0 |
| 10 | **N** | Tyler Lockett (WR) 121.0 | Brock Purdy (QB) 266.86 | +145.9 |
| 11 | **N** | Justin Herbert (QB) 285.4 | Courtland Sutton (WR) 240.3 | -45.1 |
| 12 | **N** | Joshua Palmer (WR) 107.4 | Aaron Rodgers (QB) 256.58 | +149.2 |
| 13 | **N** | Jordan Addison (WR) 212.5 | Jerry Jeudy (WR) 240.9 | +28.4 |
| 14 | **N** | Cole Kmet (TE) 120.4 | Khalil Herbert (RB) 31.5 | -88.9 |
| 15 | **N** | Buffalo Defense (DST) 118.0 | Quentin Johnston (WR) 174.7 | +56.7 |

## Slot 11 seed 46 — C−B -47.00

Tags: `mid_round_fork, fork_pick_itself_large_actual_loss`

Pos Δ: QB -72.8, RB +45.9, WR -30.0, TE +17.9, DST -8.0, K +0.0

### First fork — R7 (overall ~83)

- **B chose:** Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9
- **C chose:** Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9
- Actual Δ at fork (C−B pick): -151.96
- C roster need: counts={'QB': 1, 'RB': 1, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6, min_need=3
- B roster need: counts={'QB': 1, 'RB': 1, 'WR': 4, 'TE': 0, 'DST': 0, 'K': 0}, slack=6

C alternatives at fork (decision order):

1. Zack Moss (RB) · ADP 74.4 · curve 206 · marg +206.5 · actual +81.9 ← chosen
2. Javonte Williams (RB) · ADP 77.5 · curve 200 · marg +200.4 · actual +157.9
3. Tony Pollard (RB) · ADP 81.7 · curve 192 · marg +192.2 · actual +200.7
4. Devin Singletary (RB) · ADP 87.9 · curve 180 · marg +180.1 · actual +96.6
5. Austin Ekeler (RB) · ADP 88.0 · curve 180 · marg +179.9 · actual +132.3
6. Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4
7. Tyjae Spears (RB) · ADP 91.4 · curve 173 · marg +173.2 · actual +113.6
8. Chase Brown (RB) · ADP 91.9 · curve 172 · marg +172.3 · actual +255.0

B alternatives at fork (ADP-feasible order):

1. Jordan Love (QB) · ADP 73.2 · curve 209 · actual +233.9 ← chosen
2. Zack Moss (RB) · ADP 74.4 · curve 206 · actual +81.9
3. Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2
4. Javonte Williams (RB) · ADP 77.5 · curve 200 · actual +157.9
5. Tony Pollard (RB) · ADP 81.7 · curve 192 · actual +200.7
6. Hollywood Brown (WR) · ADP 82.2 · curve 191 · actual +18.1
7. Christian Watson (WR) · ADP 84.2 · curve 187 · actual +105.3
8. Devin Singletary (RB) · ADP 87.9 · curve 180 · actual +96.6

### Post-fork large hindsight regrets (C board, ≥80 PPR)

- R8: took Jake Ferguson (TE) · ADP 89.2 · curve 178 · marg +177.5 · actual +104.4; best shown alt Kyler Murray (QB) · ADP 76.1 · curve 203 · marg +0.0 · actual +297.2; regret +192.8
  - B parallel pick: Kyler Murray (QB) · ADP 76.1 · curve 203 · actual +297.2
- R9: took Baltimore Defense (DST) · ADP 131.2 · curve 95 · marg +95.4 · actual +110.0; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +156.9
  - B parallel pick: Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · actual +57.5
- R10: took Ezekiel Elliott (RB) · ADP 96.2 · curve 164 · marg +0.0 · actual +57.5; best shown alt Brock Purdy (QB) · ADP 105.7 · curve 145 · marg +0.0 · actual +266.9; regret +209.4
  - B parallel pick: Jayden Daniels (QB) · ADP 99.2 · curve 158 · actual +355.8
- R11: took Tyler Lockett (WR) · ADP 106.6 · curve 144 · marg +0.0 · actual +121.0; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +141.7
  - B parallel pick: Trey Benson (RB) · ADP 108.5 · curve 140 · actual +47.0
- R12: took Khalil Shakir (WR) · ADP 117.4 · curve 122 · marg +0.0 · actual +182.5; best shown alt Brock Bowers (TE) · ADP 121.7 · curve 114 · marg +0.0 · actual +262.7; regret +80.2
  - B parallel pick: T.J. Hockenson (TE) · ADP 118.7 · curve 120 · actual +86.5
- R14: took Kimani Vidal (RB) · ADP 143.9 · curve 71 · marg +0.0 · actual +32.7; best shown alt Bucky Irving (RB) · ADP 152.9 · curve 53 · marg +0.0 · actual +244.4; regret +211.7
  - B parallel pick: Kimani Vidal (RB) · ADP 143.9 · curve 71 · actual +32.7

### Aligned pick log (divergences marked)

| R | Same? | B | C | Δ actual |
| --- | --- | --- | --- | ---: |
| 1 | Y | Ja'Marr Chase (WR) 403.0 | Ja'Marr Chase (WR) 403.0 | +0.0 |
| 2 | Y | Jonathan Taylor (RB) 244.7 | Jonathan Taylor (RB) 244.7 | +0.0 |
| 3 | Y | Jaylen Waddle (WR) 149.6 | Jaylen Waddle (WR) 149.6 | +0.0 |
| 4 | Y | Patrick Mahomes (QB) 283.02 | Patrick Mahomes (QB) 283.02 | +0.0 |
| 5 | Y | Malik Nabers (WR) 273.6 | Malik Nabers (WR) 273.6 | +0.0 |
| 6 | Y | Tee Higgins (WR) 222.1 | Tee Higgins (WR) 222.1 | +0.0 |
| 7 | **N** | Jordan Love (QB) 233.86 | Zack Moss (RB) 81.9 | -152.0 |
| 8 | **N** | Kyler Murray (QB) 297.24 | Jake Ferguson (TE) 104.4 | -192.8 |
| 9 | **N** | Ezekiel Elliott (RB) 57.5 | Baltimore Defense (DST) 110.0 | +52.5 |
| 10 | **N** | Jayden Daniels (QB) 355.82 | Ezekiel Elliott (RB) 57.5 | -298.3 |
| 11 | **N** | Trey Benson (RB) 47.0 | Tyler Lockett (WR) 121.0 | +74.0 |
| 12 | **N** | T.J. Hockenson (TE) 86.5 | Khalil Shakir (WR) 182.5 | +96.0 |
| 13 | **N** | Jordan Addison (WR) 212.5 | Justin Fields (QB) 119.14 | -93.4 |
| 14 | Y | Kimani Vidal (RB) 32.7 | Kimani Vidal (RB) 32.7 | +0.0 |
| 15 | **N** | Buffalo Defense (DST) 118.0 | Antonio Gibson (RB) 103.4 | -14.6 |

## Status

- Loss-case inspection: 🟢 artifact written
- V3: 🔴 still blocked — interpret failure mechanism before design
- UI: `marginal`
