# Divergence trace — raw marginal vs VOR (disagreements only)

## Setup

- slots: `[1, 5, 10]`
- n_sims per slot: **5**
- first user picks traced: **5**
- board drivers: `marginal, marginal_vor` (each sim runs once per driver; CPU paired by `pick_rng(seed, overall)`)
- seed: `0`
- preset: `league_default`

## What this tests

- **Hypothesis A (snake/opportunity cost):** disagreements cluster at long `picks_until_next` (slot 1 early) and shrink when the wait is short (slot 10).
- **Hypothesis B (RB bias):** disagreements are mostly Raw=WR vs VOR=RB (or similar) even at short waits.
- **Hypothesis C (lineup construction):** position pairs look like scarcity fixes but later diverge via FLEX/roster composition — inspect later picks.

## Aggregate (all board drivers × sims)

Overall rates are dominated by R1 (empty-roster raw QB vs VOR RB). The **later picks (2–5)** rows are the fairer snake-gap check.

| slot | all disagree% | later (picks 2–5) disagree% | later wait buckets | later pos pairs (raw→vor) |
| --- | ---: | ---: | --- | --- |
| 1 | 78% (39/50) | 72% (29/40) | long_14+=14, short_0-5=15 | QB->RB×15, WR->RB×12, QB->WR×2 |
| 5 | 78% (39/50) | 72% (29/40) | mid_6-13=29 | QB->RB×16, WR->RB×11, QB->WR×2 |
| 10 | 80% (40/50) | 75% (30/40) | long_14+=12, short_0-5=18 | QB->RB×15, WR->RB×10, QB->WR×5 |

### By user-pick index

**Slot 1** (R1→R2 others ≈ `18`)

| user pick | agree | disagree | top pairs |
| ---: | ---: | ---: | --- |
| 1 | 0 | 10 | QB->RB×10 |
| 2 | 0 | 10 | WR->RB×5, QB->RB×5 |
| 3 | 0 | 10 | WR->RB×5, QB->RB×5 |
| 4 | 5 | 5 | QB->RB×5 |
| 5 | 6 | 4 | WR->RB×2, QB->WR×2 |

**Slot 5** (R1→R2 others ≈ `10`)

| user pick | agree | disagree | top pairs |
| ---: | ---: | ---: | --- |
| 1 | 0 | 10 | QB->RB×8, QB->WR×2 |
| 2 | 2 | 8 | QB->RB×5, WR->RB×3 |
| 3 | 0 | 10 | WR->RB×5, QB->RB×5 |
| 4 | 3 | 7 | QB->RB×5, WR->RB×2 |
| 5 | 6 | 4 | QB->WR×2, QB->RB×1, WR->RB×1 |

**Slot 10** (R1→R2 others ≈ `0`)

| user pick | agree | disagree | top pairs |
| ---: | ---: | ---: | --- |
| 1 | 0 | 10 | QB->RB×10 |
| 2 | 3 | 7 | QB->RB×4, WR->RB×2, QB->WR×1 |
| 3 | 0 | 10 | WR->RB×5, QB->RB×5 |
| 4 | 5 | 5 | QB->RB×5 |
| 5 | 2 | 8 | QB->WR×4, WR->RB×3, QB->RB×1 |


## Disagreement log

### Slot 1

Snake sanity: others between R1 and R2 at this seat ≈ **18** (`2*(n−k)` with n=10).

#### seed=0 · board_driver=`marginal` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=0 · board_driver=`marginal_vor` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 139.35
VOR: 144.12

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 4 (overall #40, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63

next pick: #41
picks until next (others): 0
wait distance: 1
```

#### seed=1009 · board_driver=`marginal` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.18
VOR: 147.52

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=1009 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 139.35
VOR: 144.12

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 4 (overall #40, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63

next pick: #41
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Nico Collins — WR
proj: 289.12
replacement: 196.36
VOR: 92.76

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=2018 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97

next pick: #40
picks until next (others): 18
wait distance: 19
```

#### seed=2018 · board_driver=`marginal_vor` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 163.77
VOR: 162.22

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 4 (overall #40, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 118.07
VOR: 165.4

next pick: #41
picks until next (others): 0
wait distance: 1
```

#### seed=3027 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #40
picks until next (others): 18
wait distance: 19
```

#### seed=3027 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 137.02
VOR: 146.44

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 4 (overall #40, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63

next pick: #41
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 187.56
VOR: 82.49

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=4036 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24

next pick: #40
picks until next (others): 18
wait distance: 19
```

#### seed=4036 · board_driver=`marginal_vor` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 137.02
VOR: 146.44

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 4 (overall #40, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63

next pick: #41
picks until next (others): 0
wait distance: 1
```

### Slot 5

Snake sanity: others between R1 and R2 at this seat ≈ **10** (`2*(n−k)` with n=10).

#### seed=0 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 163.77
VOR: 120.28

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #36
picks until next (others): 10
wait distance: 11
```

#### seed=0 · board_driver=`marginal_vor` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 171.37
VOR: 112.68

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.58
VOR: 154.89

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.72
VOR: 146.98

next pick: #45
picks until next (others): 8
wait distance: 9
```

#### seed=1009 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Ja'Marr Chase — WR
proj: 340.02
replacement: 218.62
VOR: 121.4

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 119.18
VOR: 164.29

next pick: #45
picks until next (others): 8
wait distance: 9
```

#### seed=1009 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Ja'Marr Chase — WR
proj: 340.02
replacement: 218.62
VOR: 121.4

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 163.77
VOR: 120.28

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.58
VOR: 154.89

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.18
VOR: 147.52

next pick: #45
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 5 (overall #45, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Chuba Hubbard — RB
proj: 258.55
replacement: 109.66
VOR: 148.88

next pick: #56
picks until next (others): 10
wait distance: 11
```

#### seed=2018 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 199.2
VOR: 126.79

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
CeeDee Lamb — WR
proj: 317.53
lineup gain: 317.53

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7

next pick: #36
picks until next (others): 10
wait distance: 11
```

#### seed=2018 · board_driver=`marginal_vor` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 199.2
VOR: 126.79

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 171.37
VOR: 112.68

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 137.02
VOR: 146.44

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.18
VOR: 147.52

next pick: #45
picks until next (others): 8
wait distance: 9
```

#### seed=3027 · board_driver=`marginal` (1 agreements / 4 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 206.87
VOR: 132.51

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Justin Jefferson — WR
proj: 315.86
lineup gain: 315.86

VOR:
Ashton Jeanty — RB
proj: 302.05
replacement: 171.37
VOR: 130.68

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 5 (overall #45, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.18
VOR: 147.52

next pick: #56
picks until next (others): 10
wait distance: 11
```

#### seed=3027 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 206.87
VOR: 132.51

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 163.77
VOR: 143.76

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.09
VOR: 155.38

next pick: #45
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 5 (overall #45, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 179.09
VOR: 90.95

next pick: #56
picks until next (others): 10
wait distance: 11
```

#### seed=4036 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 206.87
VOR: 119.12

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96

next pick: #45
picks until next (others): 8
wait distance: 9
```

#### seed=4036 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 206.87
VOR: 119.12

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Christian McCaffrey — RB
proj: 318.41
replacement: 163.77
VOR: 154.64

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.58
VOR: 155.47

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 119.72
VOR: 163.75

next pick: #45
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 5 (overall #45, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 179.17
VOR: 90.87

next pick: #56
picks until next (others): 10
wait distance: 11
```

### Slot 10

Snake sanity: others between R1 and R2 at this seat ≈ **0** (`2*(n−k)` with n=10).

#### seed=0 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 199.2
VOR: 140.18

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 109.27
VOR: 157.44

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=0 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 199.2
VOR: 140.18

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 194.07
VOR: 131.92

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 4 (overall #31, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 119.72
VOR: 163.75

next pick: #50
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Jalen Hurts — QB
proj: 365.49
lineup gain: 365.49

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 177.77
VOR: 92.27

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=1009 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 193.17
VOR: 114.36

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
CeeDee Lamb — WR
proj: 317.53
lineup gain: 317.53

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 193.17
VOR: 114.36

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup gain: 289.12

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96

next pick: #31
picks until next (others): 0
wait distance: 1
```

#### seed=1009 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 193.17
VOR: 114.36

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Ashton Jeanty — RB
proj: 302.05
replacement: 188.14
VOR: 113.91

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 133.58
VOR: 150.47

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 4 (overall #31, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.58
VOR: 154.89

next pick: #50
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Jalen Hurts — QB
proj: 365.49
lineup gain: 365.49

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 179.17
VOR: 90.87

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=2018 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Ja'Marr Chase — WR
proj: 340.02
lineup gain: 340.02

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #31
picks until next (others): 0
wait distance: 1
```

#### seed=2018 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Ja'Marr Chase — WR
proj: 340.02
replacement: 212.6
VOR: 127.42

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 133.58
VOR: 150.47

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 4 (overall #31, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.58
VOR: 154.89

next pick: #50
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Joe Burrow — QB
proj: 330.46
lineup gain: 330.46

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 109.27
VOR: 157.44

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=3027 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 109.27
VOR: 157.44

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=3027 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Jahmyr Gibbs — RB
proj: 317.28
replacement: 188.14
VOR: 129.14

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 133.58
VOR: 150.47

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 4 (overall #31, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.58
VOR: 154.89

next pick: #50
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 179.09
VOR: 90.95

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=4036 · board_driver=`marginal` (2 agreements / 3 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup gain: 301.35

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 133.58
VOR: 150.47

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup gain: 270.04

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 109.27
VOR: 157.44

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=4036 · board_driver=`marginal_vor` (0 agreements / 5 disagreements in first 5 user picks)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Christian McCaffrey — RB
proj: 318.41
replacement: 188.14
VOR: 130.27

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.58
VOR: 155.47

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 4 (overall #31, round 4)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup gain: 371.59

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 128.09
VOR: 155.38

next pick: #50
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Joe Burrow — QB
proj: 330.46
lineup gain: 330.46

VOR:
Brian Thomas — WR
proj: 270.04
replacement: 179.17
VOR: 90.87

next pick: #51
picks until next (others): 0
wait distance: 1
```

## Reading guide

- `picks_until_next` = other players drafted before your next turn.
- `wait_distance` = `next_user_pick − overall_pick` (slot-1 R1→R2 = 19).
- Board driver only affects *continuation* after a disagreement; each comparison itself is on an identical board state for both strategies.
- Slot 10 still has **long** waits after its turn-around pick (e.g. #11 → #30), so short R1 gap ≠ short gaps all draft.
