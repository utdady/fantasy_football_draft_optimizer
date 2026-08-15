# V3-B.0 failure mechanism audit

- stage: `V3B0_FAILURE_AUDIT`
- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- construction: `replacement_nextbest_v1` (falsified)
- evaluable: **0**
- pairs: 60
- source: `results\phase2_v3b_ladder.json`

Descriptive audit of why V3-B.0 E−D failed. First D≠E divergence is the anchor; decision-time M_D/r*/M_E joined via targeted replay. No new objective; not E.1.

**Failure → mechanism audit → hypothesis → design contract → implementation. Do not tweak r* after this report.**

## Findings

- E−D mean=-24.25 on 60 boards (60 diverge at ≥1 pick).
- First-fork bands: {'r1-5': 60}
- Top first-fork transitions: [('WR->RB', 45), ('WR->TE', 12), ('QB->RB', 3)]
- At first fork, mean M_D(D)−M_D(E)=+34.68 (positive ⇒ E left higher M_D on the table).
- Mean fraction of pool with |M_E|≤1 at first fork: 4.7%.
- Pool r*/v at first forks: mean=1.300, median=1.253.
- Starter TE E−D mean=+93.32; RB mean=+269.80; WR mean=-383.97.

## 1. Decision divergence

- boards with ≥1 D≠E pick: 60
- mean changed picks / board: 10.7167
- first-fork bands: `{'r1-5': 60}`
- first-fork rounds: `{'1': 3, '2': 22, '3': 10, '4': 25}`
- D positions at first fork: `{'WR': 57, 'QB': 3}`
- E positions at first fork: `{'RB': 48, 'TE': 12}`
- transitions: `{'WR->RB': 45, 'WR->TE': 12, 'QB->RB': 3}`

## 2. Outcome attribution

- first-fork actual E−D: mean=+10.67, WR(E)=0.45

| Pos | Mean starter E−D | Median | WR |
| --- | ---: | ---: | ---: |
| QB | -2.67 | +0.00 | 0% |
| RB | +269.80 | +272.55 | 90% |
| WR | -383.97 | -381.00 | 3% |
| TE | +93.32 | +108.50 | 68% |
| DST | -0.73 | +0.00 | 2% |
| K | +0.00 | +0.00 | 0% |

| Band | Mean starter E−D | Median | WR |
| --- | ---: | ---: | ---: |
| r1-5 | +144.91 | +117.80 | 87% |
| r6-10 | +3.10 | +0.00 | 47% |
| r11-15 | -172.27 | -190.75 | 25% |

## 3. Immediate-value sacrifice (first fork)

- joined boards: 60
- mean M_D(D)−M_D(E): +34.68
- mean M_E(E)−M_E(D): +13.68
- mean fork actual E−D: +10.67

| Slot | Seed | R | D pick | E pick | M_D(D) | M_D(E) | r*(D) | r*(E) | M_E(D) | M_E(E) | act D | act E | Δact |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 42 | 2 | Davante Adams (WR) | Travis Etienne Jr. (RB) | 246.65 | 210.12 | 242.01 | 200.58 | 4.64 | 9.54 | 241.30 | 130.20 | -111.10 |
| 1 | 43 | 2 | Drake London (WR) | Jonathan Taylor (RB) | 242.01 | 236.06 | 227.46 | 210.12 | 14.55 | 25.94 | 280.80 | 244.70 | -36.10 |
| 1 | 44 | 4 | Brandon Aiyuk (WR) | Aaron Jones Sr. (RB) | 197.49 | 157.80 | 194.20 | 134.14 | 3.29 | 23.66 | 62.40 | 241.60 | +179.20 |
| 1 | 45 | 4 | DJ Moore (WR) | Kenneth Walker (RB) | 210.62 | 181.13 | 206.14 | 153.07 | 4.48 | 28.06 | 238.10 | 181.20 | -56.90 |
| 1 | 46 | 2 | Drake London (WR) | Jonathan Taylor (RB) | 242.01 | 236.06 | 237.37 | 210.12 | 4.64 | 25.94 | 280.80 | 244.70 | -36.10 |
| 2 | 42 | 2 | Davante Adams (WR) | Travis Etienne Jr. (RB) | 246.65 | 210.12 | 242.01 | 200.58 | 4.64 | 9.54 | 241.30 | 130.20 | -111.10 |
| 2 | 43 | 2 | Drake London (WR) | Jonathan Taylor (RB) | 242.01 | 236.06 | 227.46 | 210.12 | 14.55 | 25.94 | 280.80 | 244.70 | -36.10 |
| 2 | 44 | 4 | Brandon Aiyuk (WR) | Mark Andrews (TE) | 197.49 | 190.39 | 194.20 | 184.49 | 3.29 | 5.90 | 62.40 | 188.80 | +126.40 |
| 2 | 45 | 4 | DJ Moore (WR) | Mark Andrews (TE) | 210.62 | 190.39 | 206.14 | 164.28 | 4.48 | 26.11 | 238.10 | 188.80 | -49.30 |
| 2 | 46 | 2 | Drake London (WR) | Jonathan Taylor (RB) | 242.01 | 236.06 | 237.37 | 210.12 | 4.64 | 25.94 | 280.80 | 244.70 | -36.10 |
| 3 | 42 | 4 | Stefon Diggs (WR) | Trey McBride (TE) | 215.69 | 184.49 | 210.62 | 164.28 | 5.07 | 20.21 | 121.92 | 243.80 | +121.88 |
| 3 | 43 | 2 | Davante Adams (WR) | Jonathan Taylor (RB) | 246.65 | 236.06 | 242.01 | 210.12 | 4.64 | 25.94 | 241.30 | 244.70 | +3.40 |
| 3 | 44 | 3 | Drake London (WR) | Derrick Henry (RB) | 242.01 | 215.77 | 237.37 | 210.12 | 4.64 | 5.65 | 280.80 | 336.40 | +55.60 |
| 3 | 45 | 4 | DK Metcalf (WR) | Mark Andrews (TE) | 215.69 | 190.39 | 210.62 | 164.28 | 5.07 | 26.11 | 191.20 | 188.80 | -2.40 |
| 3 | 46 | 2 | Davante Adams (WR) | Jonathan Taylor (RB) | 246.65 | 236.06 | 242.01 | 210.12 | 4.64 | 25.94 | 241.30 | 244.70 | +3.40 |
| 4 | 42 | 4 | DK Metcalf (WR) | Trey McBride (TE) | 215.69 | 184.49 | 215.69 | 164.28 | -0.00 | 20.21 | 191.20 | 243.80 | +52.60 |
| 4 | 43 | 4 | Mike Evans (WR) | Mark Andrews (TE) | 215.69 | 190.39 | 215.69 | 164.28 | -0.00 | 26.11 | 240.40 | 188.80 | -51.60 |
| 4 | 44 | 3 | Deebo Samuel Sr. (WR) | Derrick Henry (RB) | 237.37 | 215.77 | 227.46 | 203.80 | 9.91 | 11.97 | 155.60 | 336.40 | +180.80 |
| 4 | 45 | 4 | Malik Nabers (WR) | James Cook III (RB) | 215.69 | 190.66 | 215.69 | 153.07 | -0.00 | 37.59 | 273.60 | 266.70 | -6.90 |
| 4 | 46 | 4 | Nico Collins (WR) | Aaron Jones Sr. (RB) | 215.69 | 157.80 | 215.69 | 134.14 | -0.00 | 23.66 | 210.60 | 241.60 | +31.00 |
| 5 | 42 | 4 | Malik Nabers (WR) | Aaron Jones Sr. (RB) | 215.69 | 157.80 | 215.69 | 134.14 | -0.00 | 23.66 | 273.60 | 241.60 | -32.00 |
| 5 | 43 | 3 | Drake London (WR) | Josh Jacobs (RB) | 242.01 | 200.58 | 227.46 | 182.21 | 14.55 | 18.37 | 280.80 | 293.10 | +12.30 |
| 5 | 44 | 4 | DJ Moore (WR) | Mark Andrews (TE) | 210.62 | 190.39 | 206.14 | 184.49 | 4.48 | 5.90 | 238.10 | 188.80 | -49.30 |
| 5 | 45 | 4 | Malik Nabers (WR) | Kenneth Walker (RB) | 215.69 | 181.13 | 215.69 | 153.07 | -0.00 | 28.06 | 273.60 | 181.20 | -92.40 |
| 5 | 46 | 3 | Drake London (WR) | Mark Andrews (TE) | 242.01 | 190.39 | 237.37 | 184.49 | 4.64 | 5.90 | 280.80 | 188.80 | -92.00 |
| 6 | 42 | 4 | Nico Collins (WR) | Trey McBride (TE) | 215.69 | 184.49 | 215.69 | 164.28 | -0.00 | 20.21 | 210.60 | 243.80 | +33.20 |
| 6 | 43 | 3 | Chris Olave (WR) | De'Von Achane (RB) | 227.46 | 203.80 | 215.69 | 182.21 | 11.77 | 21.59 | 76.70 | 299.90 | +223.20 |
| 6 | 44 | 4 | DJ Moore (WR) | Kenneth Walker (RB) | 210.62 | 181.13 | 206.14 | 157.80 | 4.48 | 23.33 | 238.10 | 181.20 | -56.90 |
| 6 | 45 | 2 | Garrett Wilson (WR) | Jonathan Taylor (RB) | 269.39 | 236.06 | 250.06 | 210.12 | 19.33 | 25.94 | 251.90 | 244.70 | -7.20 |
| 6 | 46 | 2 | Cooper Kupp (WR) | Bijan Robinson (RB) | 250.06 | 247.04 | 246.65 | 236.06 | 3.41 | 10.98 | 175.00 | 341.70 | +166.70 |
| 7 | 42 | 4 | Malik Nabers (WR) | Alvin Kamara (RB) | 215.69 | 187.07 | 215.69 | 157.80 | -0.00 | 29.27 | 273.60 | 265.30 | -8.30 |
| 7 | 43 | 4 | Mike Evans (WR) | Aaron Jones Sr. (RB) | 215.69 | 157.80 | 215.69 | 134.14 | -0.00 | 23.66 | 240.40 | 241.60 | +1.20 |
| 7 | 44 | 4 | Malik Nabers (WR) | Kenneth Walker (RB) | 215.69 | 181.13 | 215.69 | 157.80 | -0.00 | 23.33 | 273.60 | 181.20 | -92.40 |
| 7 | 45 | 2 | Garrett Wilson (WR) | Jonathan Taylor (RB) | 269.39 | 236.06 | 250.06 | 215.77 | 19.33 | 20.29 | 251.90 | 244.70 | -7.20 |
| 7 | 46 | 3 | Jaylen Waddle (WR) | De'Von Achane (RB) | 218.48 | 203.80 | 215.69 | 192.67 | 2.79 | 11.13 | 149.60 | 299.90 | +150.30 |
| 8 | 42 | 4 | Nico Collins (WR) | Mark Andrews (TE) | 215.69 | 190.39 | 215.69 | 184.49 | -0.00 | 5.90 | 210.60 | 188.80 | -21.80 |
| 8 | 43 | 4 | DeVonta Smith (WR) | Joe Mixon (RB) | 215.69 | 182.21 | 215.69 | 157.80 | -0.00 | 24.41 | 199.40 | 240.50 | +41.10 |
| 8 | 44 | 4 | Malik Nabers (WR) | Kenneth Walker (RB) | 215.69 | 181.13 | 215.69 | 157.80 | -0.00 | 23.33 | 273.60 | 181.20 | -92.40 |
| 8 | 45 | 2 | A.J. Brown (WR) | Derrick Henry (RB) | 272.75 | 215.77 | 269.39 | 210.12 | 3.36 | 5.65 | 216.90 | 336.40 | +119.50 |
| 8 | 46 | 4 | Malik Nabers (WR) | Aaron Jones Sr. (RB) | 215.69 | 157.80 | 215.69 | 134.14 | -0.00 | 23.66 | 273.60 | 241.60 | -32.00 |
| 9 | 42 | 3 | Nico Collins (WR) | James Cook III (RB) | 215.69 | 190.66 | 215.69 | 187.07 | -0.00 | 3.59 | 210.60 | 266.70 | +56.10 |
| 9 | 43 | 4 | Mike Evans (WR) | Joe Mixon (RB) | 215.69 | 182.21 | 215.69 | 157.80 | -0.00 | 24.41 | 240.40 | 240.50 | +0.10 |
| 9 | 44 | 2 | Marvin Harrison Jr. (WR) | Jonathan Taylor (RB) | 262.66 | 236.06 | 250.06 | 215.77 | 12.60 | 20.29 | 196.50 | 244.70 | +48.20 |
| 9 | 45 | 2 | Garrett Wilson (WR) | Jonathan Taylor (RB) | 269.39 | 236.06 | 262.66 | 215.77 | 6.73 | 20.29 | 251.90 | 244.70 | -7.20 |
| 9 | 46 | 2 | Tyreek Hill (WR) | Jonathan Taylor (RB) | 285.09 | 236.06 | 272.75 | 210.12 | 12.34 | 25.94 | 218.20 | 244.70 | +26.50 |
| 10 | 42 | 2 | Garrett Wilson (WR) | Saquon Barkley (RB) | 269.39 | 231.07 | 260.70 | 215.77 | 8.69 | 15.30 | 251.90 | 355.30 | +103.40 |
| 10 | 43 | 4 | DeVonta Smith (WR) | Mark Andrews (TE) | 215.69 | 190.39 | 215.69 | 184.49 | -0.00 | 5.90 | 199.40 | 188.80 | -10.60 |
| 10 | 44 | 4 | Jaylen Waddle (WR) | Aaron Jones Sr. (RB) | 218.48 | 157.80 | 215.69 | 153.07 | 2.79 | 4.73 | 149.60 | 241.60 | +92.00 |
| 10 | 45 | 2 | A.J. Brown (WR) | Jahmyr Gibbs (RB) | 272.75 | 237.39 | 262.66 | 215.77 | 10.09 | 21.62 | 216.90 | 362.90 | +146.00 |
| 10 | 46 | 2 | Ja'Marr Chase (WR) | Jonathan Taylor (RB) | 283.13 | 236.06 | 272.75 | 210.12 | 10.38 | 25.94 | 403.00 | 244.70 | -158.30 |
| 11 | 42 | 3 | Nico Collins (WR) | James Cook III (RB) | 215.69 | 190.66 | 215.69 | 181.13 | -0.00 | 9.53 | 210.60 | 266.70 | +56.10 |
| 11 | 43 | 1 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 336.50 | 231.07 | 13.79 | 15.97 | 379.04 | 341.70 | -37.34 |
| 11 | 44 | 2 | Garrett Wilson (WR) | Jonathan Taylor (RB) | 269.39 | 236.06 | 262.66 | 215.77 | 6.73 | 20.29 | 251.90 | 244.70 | -7.20 |
| 11 | 45 | 2 | Justin Jefferson (WR) | Jonathan Taylor (RB) | 280.88 | 236.06 | 272.75 | 215.77 | 8.13 | 20.29 | 317.48 | 244.70 | -72.78 |
| 11 | 46 | 2 | Ja'Marr Chase (WR) | Saquon Barkley (RB) | 283.13 | 231.07 | 272.75 | 210.12 | 10.38 | 20.95 | 403.00 | 355.30 | -47.70 |
| 12 | 42 | 2 | Marvin Harrison Jr. (WR) | Bijan Robinson (RB) | 262.66 | 247.04 | 260.70 | 236.06 | 1.96 | 10.98 | 196.50 | 341.70 | +145.20 |
| 12 | 43 | 1 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 336.50 | 231.07 | 13.79 | 15.97 | 379.04 | 341.70 | -37.34 |
| 12 | 44 | 1 | Josh Allen (QB) | Jonathan Taylor (RB) | 350.29 | 236.06 | 336.50 | 215.77 | 13.79 | 20.29 | 379.04 | 244.70 | -134.34 |
| 12 | 45 | 3 | Nico Collins (WR) | Mark Andrews (TE) | 215.69 | 190.39 | 215.69 | 164.28 | -0.00 | 26.11 | 210.60 | 188.80 | -21.80 |
| 12 | 46 | 3 | Jaylen Waddle (WR) | James Cook III (RB) | 218.48 | 190.66 | 215.69 | 182.21 | 2.79 | 8.45 | 149.60 | 266.70 | +117.10 |

## 4. New-hole analysis

Roster pick-count Δ (E−D), not starter points. ex-DST+TE E−D≈−117 elevates TE scrutiny.

- mean roster count Δ (E−D): `{'QB': -1.0667, 'RB': 1.5667, 'WR': -2.8833, 'TE': 1.2833, 'DST': 1.1, 'K': 0.0}`
- starter TE E−D: mean=+93.32, median=+108.50
- starter RB E−D: mean=+269.80, median=+272.55

## 5. Replacement-collapse diagnostic

At first-fork decision pools: r*/v and fraction with |M_E|≤1. High r*/v + near-zero M_E ⇒ absolute valuation collapsed.

- r*/v (pool at first forks): mean=1.30, median=1.25, p10=1.00, p90=1.69
- |M_E|≤1 fraction by board: mean=0.05, median=0.05

## Status

- V3-B.0: 🔴 falsified (`5a2d4fc`)
- E.1: 🔴 not opened
- UI: `marginal`
- map: frozen
