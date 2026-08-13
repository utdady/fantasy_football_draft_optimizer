# Frozen ESPN projection curve audit

## Setup

- **Frozen full pool** (no players drafted)
- teams: **10**
- preset: `league_default`
- starter demand N: `{'QB': 10, 'RB': 29, 'WR': 29, 'TE': 12, 'DST': 10, 'K': 0}`
- source: ESPN `projections_snapshots.season_points`

## Frozen replacement: RB#29 vs WR#29

- RB#29 = **207.83** (`Austin Ekeler`)
- WR#29 = **221.36** (`George Pickens`)
- RB#29 − WR#29 = **-13.53**

This is the static gap VOR sees at pick 1 (before any draft depletion).

## RB ranks 20–40 (replacement N=29)

Replacement player: **#29 Austin Ekeler** (207.83)

| rank | player | proj | Δ from prev | Δ to next |
| ---: | --- | ---: | ---: | ---: |
| 20 | Kenneth Walker | 238.79 | -11.38 | -12.00 |
| 21 | D'Andre Swift | 226.78 | -12.00 | -0.74 |
| 22 | Breece Hall | 226.04 | -0.74 | -2.21 |
| 23 | TreVeyon Henderson | 223.83 | -2.21 | -1.70 |
| 24 | Tony Pollard | 222.13 | -1.70 | -4.90 |
| 25 | Javonte Williams | 217.23 | -4.90 | -0.92 |
| 26 | Aaron Jones | 216.32 | -0.92 | -2.53 |
| 27 | Isiah Pacheco | 213.79 | -2.53 | -0.38 |
| 28 | David Montgomery | 213.40 | -0.38 | -5.58 |
| **29** | **Austin Ekeler** | **207.83** | -5.58 | -0.57 |
| 30 | RJ Harvey | 207.26 | -0.57 | -0.39 |
| 31 | Tyrone Tracy | 206.87 | -0.39 | -7.67 |
| 32 | Dylan Sampson | 199.20 | -7.67 | -5.13 |
| 33 | Jadarian Price | 194.07 | -5.13 | -0.90 |
| 34 | Kenny Gainwell | 193.17 | -0.90 | -5.03 |
| 35 | Travis Etienne | 188.14 | -5.03 | -15.06 |
| 36 | Rhamondre Stevenson | 173.08 | -15.06 | -1.71 |
| 37 | J.K. Dobbins | 171.37 | -1.71 | -7.60 |
| 38 | Jacory Croskey-Merritt | 163.77 | -7.60 | -3.96 |
| 39 | Kaleb Johnson | 159.81 | -3.96 | -20.46 |
| 40 | Cam Skattebo | 139.35 | -20.46 | -2.32 |

Notable step drops in window:

- rank 20->21: drop 12.0 after Kenneth Walker
- rank 35->36: drop 15.1 after Travis Etienne
- rank 39->40: drop 20.5 after Kaleb Johnson

## WR ranks 20–40 (replacement N=29)

Replacement player: **#29 George Pickens** (221.36)

| rank | player | proj | Δ from prev | Δ to next |
| ---: | --- | ---: | ---: | ---: |
| 20 | DJ Moore | 237.95 | -2.05 | -2.69 |
| 21 | Tetairoa McMillan | 235.26 | -2.69 | -0.19 |
| 22 | Mike Evans | 235.07 | -0.19 | -2.55 |
| 23 | Zay Flowers | 232.52 | -2.55 | -1.08 |
| 24 | Jerry Jeudy | 231.44 | -1.08 | -2.26 |
| 25 | Calvin Ridley | 229.18 | -2.26 | -1.59 |
| 26 | Courtland Sutton | 227.59 | -1.59 | -1.06 |
| 27 | Jaylen Waddle | 226.53 | -1.06 | -3.54 |
| 28 | DeVonta Smith | 222.99 | -3.54 | -1.63 |
| **29** | **George Pickens** | **221.36** | -1.63 | -1.73 |
| 30 | Jakobi Meyers | 219.64 | -1.73 | -1.02 |
| 31 | Jameson Williams | 218.62 | -1.02 | -1.57 |
| 32 | Rome Odunze | 217.05 | -1.57 | -4.45 |
| 33 | Keenan Allen | 212.60 | -4.45 | -0.06 |
| 34 | Travis Hunter | 212.54 | -0.06 | -1.41 |
| 35 | Carnell Tate | 211.13 | -1.41 | -1.30 |
| 36 | Chris Olave | 209.82 | -1.30 | -6.50 |
| 37 | Matthew Golden | 203.32 | -6.50 | -0.18 |
| 38 | Deebo Samuel | 203.14 | -0.18 | -0.76 |
| 39 | Cooper Kupp | 202.37 | -0.76 | -1.27 |
| 40 | Michael Pittman | 201.11 | -1.27 | -0.08 |

No large step-drop outliers flagged in this window (vs local median).

## TE ranks 1–30 (replacement N=12)

Replacement player: **#12 Tucker Kraft** (159.96)

| rank | player | proj | Δ from prev | Δ to next |
| ---: | --- | ---: | ---: | ---: |
| 1 | Brock Bowers | 262.19 | — | -2.97 |
| 2 | Trey McBride | 259.22 | -2.97 | -31.50 |
| 3 | George Kittle | 227.72 | -31.50 | -35.95 |
| 4 | Sam LaPorta | 191.77 | -35.95 | -7.24 |
| 5 | T.J. Hockenson | 184.54 | -7.24 | -3.45 |
| 6 | Travis Kelce | 181.08 | -3.45 | -4.70 |
| 7 | David Njoku | 176.39 | -4.70 | -3.01 |
| 8 | Mark Andrews | 173.38 | -3.01 | -4.69 |
| 9 | Evan Engram | 168.69 | -4.69 | -2.63 |
| 10 | Tyler Warren | 166.07 | -2.63 | -3.63 |
| 11 | Kenyon Sadiq | 162.44 | -3.63 | -2.47 |
| **12** | **Tucker Kraft** | **159.96** | -2.47 | -3.09 |
| 13 | Dallas Goedert | 156.88 | -3.09 | -1.68 |
| 14 | Colston Loveland | 155.19 | -1.68 | -4.81 |
| 15 | Jake Ferguson | 150.38 | -4.81 | -2.24 |
| 16 | Hunter Henry | 148.14 | -2.24 | -1.31 |
| 17 | Dalton Kincaid | 146.83 | -1.31 | -3.76 |
| 18 | Kyle Pitts | 143.06 | -3.76 | -1.27 |
| 19 | Zach Ertz | 141.79 | -1.27 | -2.34 |
| 20 | Brenton Strange | 139.46 | -2.34 | -1.11 |
| 21 | Cade Otton | 138.34 | -1.11 | -2.78 |
| 22 | Chig Okonkwo | 135.56 | -2.78 | -0.48 |
| 23 | Jonnu Smith | 135.09 | -0.48 | -1.15 |
| 24 | Pat Freiermuth | 133.94 | -1.15 | -2.39 |
| 25 | Darren Waller | 131.55 | -2.39 | -1.52 |
| 26 | Mason Taylor | 130.03 | -1.52 | -3.97 |
| 27 | Dalton Schultz | 126.05 | -3.97 | -1.94 |
| 28 | Tyler Higbee | 124.11 | -1.94 | -2.06 |
| 29 | Theo Johnson | 122.05 | -2.06 | -4.70 |
| 30 | Juwan Johnson | 117.35 | -4.70 | -1.58 |

Notable step drops in window:

- rank 2->3: drop 31.5 after Trey McBride
- rank 3->4: drop 36.0 after George Kittle

## QB ranks 1–30 (replacement N=10)

Replacement player: **#10 Bo Nix** (301.89)

| rank | player | proj | Δ from prev | Δ to next |
| ---: | --- | ---: | ---: | ---: |
| 1 | Jayden Daniels | 371.59 | — | -3.72 |
| 2 | Josh Allen | 367.87 | -3.72 | -2.38 |
| 3 | Jalen Hurts | 365.49 | -2.38 | -1.69 |
| 4 | Lamar Jackson | 363.80 | -1.69 | -33.34 |
| 5 | Joe Burrow | 330.46 | -33.34 | -5.54 |
| 6 | Patrick Mahomes | 324.92 | -5.54 | -13.96 |
| 7 | Baker Mayfield | 310.96 | -13.96 | -4.03 |
| 8 | Kyler Murray | 306.94 | -4.03 | -0.73 |
| 9 | Brock Purdy | 306.21 | -0.73 | -4.32 |
| **10** | **Bo Nix** | **301.89** | -4.32 | -2.58 |
| 11 | Justin Fields | 299.32 | -2.58 | -13.52 |
| 12 | Dak Prescott | 285.80 | -13.52 | -0.54 |
| 13 | Drake Maye | 285.26 | -0.54 | -0.78 |
| 14 | Justin Herbert | 284.48 | -0.78 | -1.90 |
| 15 | J.J. McCarthy | 282.57 | -1.90 | -2.21 |
| 16 | C.J. Stroud | 280.36 | -2.21 | -0.57 |
| 17 | Caleb Williams | 279.79 | -0.57 | -0.47 |
| 18 | Trevor Lawrence | 279.32 | -0.47 | -3.42 |
| 19 | Tua Tagovailoa | 275.91 | -3.42 | -1.83 |
| 20 | Matthew Stafford | 274.08 | -1.83 | -6.18 |
| 21 | Bryce Young | 267.90 | -6.18 | -3.34 |
| 22 | Jordan Love | 264.55 | -3.34 | -3.35 |
| 23 | Geno Smith | 261.20 | -3.35 | -0.75 |
| 24 | Jared Goff | 260.45 | -0.75 | -3.22 |
| 25 | Cam Ward | 257.24 | -3.22 | -6.10 |
| 26 | Michael Penix | 251.13 | -6.10 | -9.44 |
| 27 | Sam Darnold | 241.69 | -9.44 | -9.08 |
| 28 | Aaron Rodgers | 232.61 | -9.08 | -19.64 |
| 29 | Daniel Jones | 212.97 | -19.64 | -25.62 |
| 30 | Fernando Mendoza | 187.35 | -25.62 | -46.28 |

Notable step drops in window:

- rank 4->5: drop 33.3 after Lamar Jackson
- rank 6->7: drop 14.0 after Patrick Mahomes
- rank 11->12: drop 13.5 after Justin Fields (at/near replacement N)
- rank 26->27: drop 9.4 after Michael Penix
- rank 27->28: drop 9.1 after Sam Darnold
- rank 28->29: drop 19.6 after Aaron Rodgers
- rank 29->30: drop 25.6 after Daniel Jones
- rank 30->31: drop 46.3 after Fernando Mendoza

## Side-by-side RB vs WR (ranks 20–40)

| rank | RB | RB proj | RB Δ→ | WR | WR proj | WR Δ→ |
| ---: | --- | ---: | ---: | --- | ---: | ---: |
| 20 | Kenneth Walker | 238.79 | -12.00 | DJ Moore | 237.95 | -2.69 |
| 21 | D'Andre Swift | 226.78 | -0.74 | Tetairoa McMillan | 235.26 | -0.19 |
| 22 | Breece Hall | 226.04 | -2.21 | Mike Evans | 235.07 | -2.55 |
| 23 | TreVeyon Henderson | 223.83 | -1.70 | Zay Flowers | 232.52 | -1.08 |
| 24 | Tony Pollard | 222.13 | -4.90 | Jerry Jeudy | 231.44 | -2.26 |
| 25 | Javonte Williams | 217.23 | -0.92 | Calvin Ridley | 229.18 | -1.59 |
| 26 | Aaron Jones | 216.32 | -2.53 | Courtland Sutton | 227.59 | -1.06 |
| 27 | Isiah Pacheco | 213.79 | -0.38 | Jaylen Waddle | 226.53 | -3.54 |
| 28 | David Montgomery | 213.40 | -5.58 | DeVonta Smith | 222.99 | -1.63 |
| **29** | **Austin Ekeler** | **207.83** | **-0.57** | **George Pickens** | **221.36** | **-1.73** |
| 30 | RJ Harvey | 207.26 | -0.39 | Jakobi Meyers | 219.64 | -1.02 |
| 31 | Tyrone Tracy | 206.87 | -7.67 | Jameson Williams | 218.62 | -1.57 |
| 32 | Dylan Sampson | 199.20 | -5.13 | Rome Odunze | 217.05 | -4.45 |
| 33 | Jadarian Price | 194.07 | -0.90 | Keenan Allen | 212.60 | -0.06 |
| 34 | Kenny Gainwell | 193.17 | -5.03 | Travis Hunter | 212.54 | -1.41 |
| 35 | Travis Etienne | 188.14 | -15.06 | Carnell Tate | 211.13 | -1.30 |
| 36 | Rhamondre Stevenson | 173.08 | -1.71 | Chris Olave | 209.82 | -6.50 |
| 37 | J.K. Dobbins | 171.37 | -7.60 | Matthew Golden | 203.32 | -0.18 |
| 38 | Jacory Croskey-Merritt | 163.77 | -3.96 | Deebo Samuel | 203.14 | -0.76 |
| 39 | Kaleb Johnson | 159.81 | -20.46 | Cooper Kupp | 202.37 | -1.27 |
| 40 | Cam Skattebo | 139.35 | -2.32 | Michael Pittman | 201.11 | -0.08 |

## Verdict (auto)

- RB#29 is **not** sitting on a flagged discontinuity; neighbors look like a gradually lower curve than WR (structural level gap), not an Ekeler-only cliff.
- Larger RB drops appear **later** (#35, #39) — beyond the replacement cutoff used at pick 1.
- WR window is smooth (no large step outliers).
- Do **not** smooth yet; this report is the raw frozen reference.
