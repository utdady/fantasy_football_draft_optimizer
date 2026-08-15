# P2.2C C−B valuation mechanism

- snapshot: `2024-preseason-2024-09-01-ffc12`
- contract: `ppr_eval_v1_2024`
- evaluable: **0**
- pairs: 60
- source: `results\phase2_p22c_adp_feasible_ladder.json`

Mechanism decomposition of valuation_gain (adp_structural − adp_feasible) under ppr_eval_v1_2024. Attribution only (no re-draft). Modeled opponents; n=1 season.

**Load-bearing quantity is C−B. Left-tail characterization precedes mean chasing. V3 still blocked. UI stays marginal.**

## Charter reminder

> Core thesis: 🟡 preliminary support (C−B > 0 after feasibility + DST controls). External validity 🔴. V3 conceptually justified, implementation blocked pending C−B mechanism. UI: `marginal`.

## Valuation gain (C−B) distribution

| Contract | Mean | Median | SD | WR | z vs 50% | n_neg | min | p10 | p90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | +76.47 | +54.14 | 157.75 | 67% | +2.6 SE | 20 | -282.48 | -80.74 | +276.45 |
| Ex-DST | +67.77 | +42.24 | 154.60 | 65% | +2.3 SE | 21 | -282.90 | -83.58 | +252.93 |
| Ex-DST+TE | +41.33 | +28.31 | 126.96 | 57% | +1.0 SE | 26 | -172.70 | -118.95 | +212.34 |

Under H0 p=0.5, SE ≈ 6.5% for n=60. Ex-DST (+2.3 SE) is the load-bearing win-rate claim; Ex-DST+TE (+1.0 SE) is not distinguishable from chance at this n.

## 1. Position contribution to C−B

Mean starter actual-PPR difference (structural − feasible), attribution only.

| Pos | Mean Δ | Median Δ | WR (pos Δ>0) |
| --- | ---: | ---: | ---: |
| QB | +0.67 | +0.00 | 20% |
| RB | -3.31 | +7.90 | 52% |
| WR | +43.97 | -8.40 | 45% |
| TE | +26.44 | +24.45 | 62% |
| DST | +8.70 | +16.00 | 58% |
| K | +0.00 | +0.00 | 0% |

Sum of mean pos Δ = +76.47 (should ≈ full mean C−B).

## 2. Round / round-band

### Round bands

| Band | Mean Δ | Median Δ | WR |
| --- | ---: | ---: | ---: |
| r1-5 | +32.18 | +0.00 | 33% |
| r6-10 | +26.11 | +41.40 | 55% |
| r11-15 | +18.18 | +12.65 | 57% |

### By draft round (starter contrib)

| Round | Mean Δ |
| --- | ---: |
| 1 | +19.25 |
| 2 | +6.89 |
| 3 | +11.07 |
| 4 | +13.47 |
| 5 | -8.01 |
| 6 | +55.93 |
| 7 | +9.56 |
| 8 | +2.88 |
| 9 | +20.91 |
| 10 | -53.14 |
| 11 | +50.87 |
| 12 | -39.71 |
| 13 | -7.99 |
| 14 | -33.60 |
| 15 | +22.30 |

## 3. Draft slot

| Slot | n | Mean C−B | Median | WR | min | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 5 | +7.97 | +41.52 | 80% | -282.48 | +139.10 |
| 2 | 5 | +52.90 | +78.54 | 60% | -112.14 | +275.70 |
| 3 | 5 | +174.78 | +102.66 | 80% | -24.70 | +397.46 |
| 4 | 5 | +64.26 | +91.68 | 80% | -46.92 | +121.86 |
| 5 | 5 | +38.39 | -4.10 | 40% | -80.46 | +174.82 |
| 6 | 5 | +57.34 | -9.92 | 40% | -138.30 | +283.20 |
| 7 | 5 | +290.05 | +347.26 | 100% | +57.20 | +562.40 |
| 8 | 5 | +22.06 | +33.78 | 80% | -261.90 | +262.82 |
| 9 | 5 | +111.39 | +103.58 | 100% | +32.60 | +210.06 |
| 10 | 5 | -0.81 | -9.80 | 40% | -164.50 | +162.20 |
| 11 | 5 | +38.81 | -34.72 | 40% | -83.24 | +205.20 |
| 12 | 5 | +60.52 | +20.20 | 60% | -30.90 | +266.40 |

## 4. Left tail

Worst 10 pairs by full valuation_gain (mean C−B among them: -128.40).

### Mean pos / band Δ among left-tail pairs

| Pos | Mean Δ in tail |
| --- | ---: |
| QB | -30.94 |
| RB | -62.78 |
| WR | -4.57 |
| TE | -30.51 |
| DST | +0.40 |
| K | +0.00 |

| Band | Mean Δ in tail |
| --- | ---: |
| r1-5 | +61.99 |
| r6-10 | -61.11 |
| r11-15 | -129.28 |

Tail slot counts: `{1: 1, 2: 2, 5: 2, 6: 1, 8: 1, 10: 1, 11: 2}`

### Worst pairs (detail)

#### Slot 1 seed 46 — C−B -282.48 (ex-DST -274.48)

Pos Δ: QB +61.64, RB -257.40, WR +52.78, TE -131.50, DST -8.00, K +0.00

Band Δ: r1-5 -121.92, r6-10 +352.28, r11-15 -512.84

Roster overlap: 7 shared; 8 only structural; 8 only feasible.

Only structural:
- R7 Kyle Pitts Sr. (TE) +131.2
- R8 Tua Tagovailoa (QB) +181.6
- R9 Tyjae Spears (RB) +113.6
- R10 Baltimore Defense (DST) +110.0
- R12 T.J. Hockenson (TE) +86.5
- R13 Joshua Palmer (WR) +107.4
- R14 Dameon Pierce (RB) +43.5
- R15 Quentin Johnston (WR) +174.7

Only feasible:
- R7 Nick Chubb (RB) +63.3
- R8 Jake Ferguson (TE) +104.4
- R9 Chase Brown (RB) +255.0
- R11 Trey Benson (RB) +47.0
- R12 Brock Bowers (TE) +262.7
- R13 Zach Charbonnet (RB) +186.9
- R14 Buffalo Defense (DST) +118.0
- R15 Will Levis (QB) +119.9

#### Slot 8 seed 44 — C−B -261.90 (ex-DST -282.90)

Pos Δ: QB +0.00, RB -83.30, WR -40.50, TE -159.10, DST +21.00, K +0.00

Band Δ: r1-5 +0.00, r6-10 -320.50, r11-15 +58.60

Roster overlap: 7 shared; 8 only structural; 8 only feasible.

Only structural:
- R8 Dallas Goedert (TE) +103.6
- R9 Baltimore Defense (DST) +110.0
- R10 Ezekiel Elliott (RB) +57.5
- R11 Rico Dowdle (RB) +197.8
- R12 Kirk Cousins (QB) +176.3
- R13 Aaron Rodgers (QB) +256.6
- R14 Jordan Addison (WR) +212.5
- R15 Will Levis (QB) +119.9

Only feasible:
- R8 Najee Harris (RB) +204.6
- R9 Jaxon Smith-Njigba (WR) +253.0
- R10 Jerome Ford (RB) +134.0
- R11 Brock Bowers (TE) +262.7
- R12 Ty Chandler (RB) +28.4
- R13 Joshua Palmer (WR) +107.4
- R14 Justin Fields (QB) +119.1
- R15 Cincinnati Defense (DST) +89.0

#### Slot 10 seed 43 — C−B -164.50 (ex-DST -186.50)

Pos Δ: QB +0.00, RB -197.80, WR +25.10, TE -13.80, DST +22.00, K +0.00

Band Δ: r1-5 +0.00, r6-10 +57.00, r11-15 -221.50

Roster overlap: 8 shared; 7 only structural; 7 only feasible.

Only structural:
- R6 Christian Kirk (WR) +70.9
- R8 Jake Ferguson (TE) +104.4
- R9 Baltimore Defense (DST) +110.0
- R11 Khalil Shakir (WR) +182.5
- R12 T.J. Hockenson (TE) +86.5
- R13 Ty Chandler (RB) +28.4
- R15 Jordan Mason (RB) +115.0

Only feasible:
- R6 Anthony Richardson Sr. (QB) +163.4
- R8 Calvin Ridley (WR) +199.2
- R10 Ladd McConkey (WR) +240.9
- R11 Dalton Schultz (TE) +118.2
- R12 Rico Dowdle (RB) +197.8
- R13 Aaron Rodgers (QB) +256.6
- R15 Deshaun Watson (QB) +76.7

#### Slot 6 seed 42 — C−B -138.30 (ex-DST -130.30)

Pos Δ: QB +0.00, RB +130.80, WR -261.10, TE +0.00, DST -8.00, K +0.00

Band Δ: r1-5 +196.50, r6-10 -220.90, r11-15 -113.90

Roster overlap: 9 shared; 6 only structural; 6 only feasible.

Only structural:
- R7 Zamir White (RB) +29.3
- R9 Baltimore Defense (DST) +110.0
- R10 Tyler Lockett (WR) +121.0
- R11 Blake Corum (RB) +33.5
- R13 Trevor Lawrence (QB) +145.2
- R15 Bucky Irving (RB) +244.4

Only feasible:
- R7 Jayden Reed (WR) +197.0
- R9 Tyjae Spears (RB) +113.6
- R10 Jameson Williams (WR) +212.2
- R11 Courtland Sutton (WR) +240.3
- R13 Elijah Mitchell (RB) +0.0
- R15 Buffalo Defense (DST) +118.0

#### Slot 2 seed 45 — C−B -112.14 (ex-DST -92.14)

Pos Δ: QB +0.00, RB +0.00, WR -138.30, TE +46.16, DST -20.00, K +0.00

Band Δ: r1-5 +0.00, r6-10 +258.50, r11-15 -370.64

Roster overlap: 9 shared; 6 only structural; 6 only feasible.

Only structural:
- R8 David Njoku (TE) +148.5
- R10 Baltimore Defense (DST) +110.0
- R11 Blake Corum (RB) +33.5
- R12 Joshua Palmer (WR) +107.4
- R14 Quentin Johnston (WR) +174.7
- R15 Josh Downs (WR) +183.5

Only feasible:
- R9 Devin Singletary (RB) +96.6
- R10 Tyler Lockett (WR) +121.0
- R11 Brian Thomas Jr. (WR) +284.0
- R13 Jordan Addison (WR) +212.5
- R14 Taysom Hill (TE) +102.3
- R15 Pittsburgh Defense (DST) +130.0

#### Slot 11 seed 43 — C−B -83.24 (ex-DST -83.24)

Pos Δ: QB -147.36, RB +76.82, WR -12.70, TE +0.00, DST +0.00, K +0.00

Band Δ: r1-5 +74.36, r6-10 -161.80, r11-15 +4.20

Roster overlap: 9 shared; 6 only structural; 6 only feasible.

Only structural:
- R5 David Montgomery (RB) +221.7
- R6 Christian Kirk (WR) +70.9
- R7 Zamir White (RB) +29.3
- R11 T.J. Hockenson (TE) +86.5
- R12 Tyler Allgeier (RB) +106.2
- R13 Zach Charbonnet (RB) +186.9

Only feasible:
- R5 Lamar Jackson (QB) +430.4
- R6 Anthony Richardson Sr. (QB) +163.4
- R7 Chris Godwin Jr. (WR) +137.8
- R10 Jerome Ford (RB) +134.0
- R11 Rico Dowdle (RB) +197.8
- R12 Trevor Lawrence (QB) +145.2

#### Slot 5 seed 44 — C−B -80.46 (ex-DST -72.46)

Pos Δ: QB -93.22, RB -199.90, WR +174.50, TE +46.16, DST -8.00, K +0.00

Band Δ: r1-5 -127.20, r6-10 +214.06, r11-15 -167.32

Roster overlap: 7 shared; 8 only structural; 8 only feasible.

Only structural:
- R7 Nick Chubb (RB) +63.3
- R8 David Njoku (TE) +148.5
- R9 Baltimore Defense (DST) +110.0
- R10 Romeo Doubs (WR) +132.1
- R11 Brian Thomas Jr. (WR) +284.0
- R12 Ty Chandler (RB) +28.4
- R13 Joshua Palmer (WR) +107.4
- R14 Jordan Addison (WR) +212.5

Only feasible:
- R7 Rashee Rice (WR) +64.9
- R8 Jaylen Warren (RB) +124.1
- R9 Tyjae Spears (RB) +113.6
- R10 DeAndre Hopkins (WR) +147.0
- R11 Mike Williams (WR) +56.8
- R12 Aaron Rodgers (QB) +256.6
- R13 Zach Charbonnet (RB) +186.9
- R15 Buffalo Defense (DST) +118.0

#### Slot 2 seed 46 — C−B -65.60 (ex-DST -86.60)

Pos Δ: QB +0.00, RB +112.10, WR -59.70, TE -139.00, DST +21.00, K +0.00

Band Δ: r1-5 +0.00, r6-10 -22.30, r11-15 -43.30

Roster overlap: 11 shared; 4 only structural; 4 only feasible.

Only structural:
- R10 Baltimore Defense (DST) +110.0
- R12 T.J. Hockenson (TE) +86.5
- R13 Jakobi Meyers (WR) +218.0
- R15 Bucky Irving (RB) +244.4

Only feasible:
- R11 Jameson Williams (WR) +212.2
- R12 Brock Bowers (TE) +262.7
- R13 Jordan Addison (WR) +212.5
- R15 Cincinnati Defense (DST) +89.0

#### Slot 5 seed 45 — C−B -48.40 (ex-DST -40.40)

Pos Δ: QB -57.70, RB -255.00, WR +244.20, TE +28.10, DST -8.00, K +0.00

Band Δ: r1-5 +315.12, r6-10 -568.52, r11-15 +205.00

Roster overlap: 6 shared; 9 only structural; 9 only feasible.

Only structural:
- R7 Raheem Mostert (RB) +70.9
- R8 David Njoku (TE) +148.5
- R9 Baltimore Defense (DST) +110.0
- R10 Brock Purdy (QB) +266.9
- R11 Courtland Sutton (WR) +240.3
- R12 Aaron Rodgers (QB) +256.6
- R13 Jerry Jeudy (WR) +240.9
- R14 Khalil Herbert (RB) +31.5
- R15 Quentin Johnston (WR) +174.7

Only feasible:
- R6 Joe Burrow (QB) +372.8
- R8 Calvin Ridley (WR) +199.2
- R9 Chase Brown (RB) +255.0
- R10 Tyler Lockett (WR) +121.0
- R11 Justin Herbert (QB) +285.4
- R12 Joshua Palmer (WR) +107.4
- R13 Jordan Addison (WR) +212.5
- R14 Cole Kmet (TE) +120.4
- R15 Buffalo Defense (DST) +118.0

#### Slot 11 seed 46 — C−B -47.00 (ex-DST -39.00)

Pos Δ: QB -72.80, RB +45.90, WR -30.00, TE +17.90, DST -8.00, K +0.00

Band Δ: r1-5 +283.02, r6-10 -198.92, r11-15 -131.10

Roster overlap: 8 shared; 7 only structural; 7 only feasible.

Only structural:
- R7 Zack Moss (RB) +81.9
- R8 Jake Ferguson (TE) +104.4
- R9 Baltimore Defense (DST) +110.0
- R11 Tyler Lockett (WR) +121.0
- R12 Khalil Shakir (WR) +182.5
- R13 Justin Fields (QB) +119.1
- R15 Antonio Gibson (RB) +103.4

Only feasible:
- R7 Jordan Love (QB) +233.9
- R8 Kyler Murray (QB) +297.2
- R10 Jayden Daniels (QB) +355.8
- R11 Trey Benson (RB) +47.0
- R12 T.J. Hockenson (TE) +86.5
- R13 Jordan Addison (WR) +212.5
- R15 Buffalo Defense (DST) +118.0

## Status

- Mechanism report: 🟢 complete (attribution; same 60 pairs)
- V3: 🔴 implementation blocked until this report is interpreted
- UI: `marginal`
