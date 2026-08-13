# Divergence trace — RAW / VOR / V2-alpha

## Setup

- slots: `[1, 5, 10]`
- n_sims per slot: **3**
- first user picks traced: **5**
- board drivers: `marginal`
- seed: `0`
- preset: `league_default`
- V2 lookahead: ADP-greedy (frozen V2-alpha)
- Draft CPU between user picks: noisy ADP (`pick_rng`)

## Aggregate

| slot | disagree% | top triples (raw/vor/v2 pos) | V2≠raw pairs | V2 expected q pos |
| --- | ---: | --- | --- | --- |
| 1 | 73% (11/15) | WR/RB/WR×8, QB/RB/WR×3 | QB->WR×3, WR->WR×3 | RB×5, QB×3, WR×3 |
| 5 | 60% (9/15) | WR/RB/WR×6, QB/RB/RB×1, QB/WR/WR×1, QB/RB/WR×1 | QB->WR×2, QB->RB×1, WR->WR×1 | RB×4, QB×3, WR×2 |
| 10 | 60% (9/15) | WR/RB/WR×6, QB/RB/WR×2, QB/RB/RB×1 | QB->WR×2, QB->RB×1 | RB×4, QB×3, WR×2 |

## Disagreement log

### Slot 1

#### seed=0 · board_driver=`marginal` (1 all-agree / 4 disagree)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54
lineup_gain(VOR-space): 131.54

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 118.66
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 90.22

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02
lineup_gain(VOR-space): 147.02

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 78.0
V2 EV (two-pick): 962.07
V2 expected future q: Malik Nabers (WR)

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 79.3

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02
lineup_gain(VOR-space): 147.02

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 79.3
V2 EV (two-pick): 1245.53
V2 expected future q: Bucky Irving (RB)

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup_gain: 270.04
VOR(shadow): 77.31

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 118.07
VOR: 148.63
lineup_gain(VOR-space): 148.63

V2:
Brian Thomas — WR
proj: 270.04
VOR(shadow): 77.31
V2 EV (two-pick): 1782.28
V2 expected future q: Alvin Kamara (RB)

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=1009 · board_driver=`marginal` (1 all-agree / 4 disagree)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54
lineup_gain(VOR-space): 131.54

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 118.66
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 91.53

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24
lineup_gain(VOR-space): 124.24

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 79.3
V2 EV (two-pick): 962.07
V2 expected future q: Malik Nabers (WR)

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 85.8

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 159.81
VOR: 124.24
lineup_gain(VOR-space): 124.24

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 85.8
V2 EV (two-pick): 1245.53
V2 expected future q: Bucky Irving (RB)

next pick: #40
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 5 (overall #41, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup_gain: 270.04
VOR(shadow): 77.31

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 119.18
VOR: 147.52
lineup_gain(VOR-space): 147.52

V2:
Brian Thomas — WR
proj: 270.04
VOR(shadow): 77.31
V2 EV (two-pick): 1782.28
V2 expected future q: Alvin Kamara (RB)

next pick: #60
picks until next (others): 18
wait distance: 19
```

#### seed=2018 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 1 — PICK 1 (overall #1, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54
lineup_gain(VOR-space): 131.54

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 118.66
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #20
picks until next (others): 18
wait distance: 19
```

```
SLOT 1 — PICK 2 (overall #20, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 98.21

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97
lineup_gain(VOR-space): 110.97

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 85.99
V2 EV (two-pick): 962.07
V2 expected future q: Malik Nabers (WR)

next pick: #21
picks until next (others): 0
wait distance: 1
```

```
SLOT 1 — PICK 3 (overall #21, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 86.75

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97
lineup_gain(VOR-space): 110.97

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 86.75
V2 EV (two-pick): 1245.53
V2 expected future q: Bucky Irving (RB)

next pick: #40
picks until next (others): 18
wait distance: 19
```

### Slot 5

#### seed=0 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 207.83
VOR: 131.54
lineup_gain(VOR-space): 131.54

V2:
Bijan Robinson — RB
proj: 339.37
VOR(shadow): 131.54
V2 EV (two-pick): 710.97
V2 expected future q: Jayden Daniels (QB)

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 88.81

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 163.77
VOR: 120.28
lineup_gain(VOR-space): 120.28

V2:
Amon-Ra St. Brown — WR
proj: 290.62
VOR(shadow): 78.08
V2 EV (two-pick): 963.56
V2 expected future q: Malik Nabers (WR)

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 85.8

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02
lineup_gain(VOR-space): 147.02

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 85.8
V2 EV (two-pick): 1246.12
V2 expected future q: Kyren Williams (RB)

next pick: #36
picks until next (others): 10
wait distance: 11
```

#### seed=1009 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Ja'Marr Chase — WR
proj: 340.02
replacement: 218.62
VOR: 121.4
lineup_gain(VOR-space): 121.4

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 121.4
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 98.03

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02
lineup_gain(VOR-space): 147.02

V2:
Malik Nabers — WR
proj: 301.35
VOR(shadow): 98.03
V2 EV (two-pick): 1275.4
V2 expected future q: Kyren Williams (RB)

next pick: #36
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 4 (overall #36, round 4)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 88.1

VOR:
Bucky Irving — RB
proj: 283.47
replacement: 119.18
VOR: 164.29
lineup_gain(VOR-space): 164.29

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 88.1
V2 EV (two-pick): 1563.94
V2 expected future q: Bucky Irving (RB)

next pick: #45
picks until next (others): 8
wait distance: 9
```

#### seed=2018 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 5 — PICK 1 (overall #5, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 199.2
VOR: 126.79
lineup_gain(VOR-space): 126.79

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 120.38
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #16
picks until next (others): 10
wait distance: 11
```

```
SLOT 5 — PICK 2 (overall #16, round 2)

RAW:
CeeDee Lamb — WR
proj: 317.53
lineup_gain: 317.53
VOR(shadow): 107.71

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 173.08
VOR: 110.97
lineup_gain(VOR-space): 110.97

V2:
CeeDee Lamb — WR
proj: 317.53
VOR(shadow): 107.71
V2 EV (two-pick): 990.47
V2 expected future q: Malik Nabers (WR)

next pick: #25
picks until next (others): 8
wait distance: 9
```

```
SLOT 5 — PICK 3 (overall #25, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 98.03

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 139.35
VOR: 144.7
lineup_gain(VOR-space): 144.7

V2:
Malik Nabers — WR
proj: 301.35
VOR(shadow): 98.03
V2 EV (two-pick): 1274.52
V2 expected future q: Kyren Williams (RB)

next pick: #36
picks until next (others): 10
wait distance: 11
```

### Slot 10

#### seed=0 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Bijan Robinson — RB
proj: 339.37
replacement: 199.2
VOR: 140.18
lineup_gain(VOR-space): 140.18

V2:
Bijan Robinson — RB
proj: 339.37
VOR(shadow): 140.18
V2 EV (two-pick): 710.97
V2 expected future q: Jayden Daniels (QB)

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 98.98

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96
lineup_gain(VOR-space): 155.96

V2:
Malik Nabers — WR
proj: 301.35
VOR(shadow): 98.98
V2 EV (two-pick): 1296.37
V2 expected future q: Kyren Williams (RB)

next pick: #31
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 5 (overall #50, round 5)

RAW:
Brian Thomas — WR
proj: 270.04
lineup_gain: 270.04
VOR(shadow): 90.95

VOR:
Alvin Kamara — RB
proj: 266.7
replacement: 109.27
VOR: 157.44
lineup_gain(VOR-space): 157.44

V2:
Brian Thomas — WR
proj: 270.04
VOR(shadow): 90.95
V2 EV (two-pick): 1833.11
V2 expected future q: Alvin Kamara (RB)

next pick: #51
picks until next (others): 0
wait distance: 1
```

#### seed=1009 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 193.17
VOR: 114.36
lineup_gain(VOR-space): 114.36

V2:
CeeDee Lamb — WR
proj: 317.53
VOR(shadow): 104.93
V2 EV (two-pick): 689.12
V2 expected future q: Jayden Daniels (QB)

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
CeeDee Lamb — WR
proj: 317.53
lineup_gain: 317.53
VOR(shadow): 104.93

VOR:
De'Von Achane — RB
proj: 307.53
replacement: 193.17
VOR: 114.36
lineup_gain(VOR-space): 114.36

V2:
CeeDee Lamb — WR
proj: 317.53
VOR(shadow): 104.93
V2 EV (two-pick): 990.47
V2 expected future q: Malik Nabers (WR)

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Nico Collins — WR
proj: 289.12
lineup_gain: 289.12
VOR(shadow): 86.75

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 128.09
VOR: 155.96
lineup_gain(VOR-space): 155.96

V2:
Nico Collins — WR
proj: 289.12
VOR(shadow): 86.75
V2 EV (two-pick): 1262.3
V2 expected future q: Kyren Williams (RB)

next pick: #31
picks until next (others): 0
wait distance: 1
```

#### seed=2018 · board_driver=`marginal` (2 all-agree / 3 disagree)

```
SLOT 10 — PICK 1 (overall #10, round 1)

RAW:
Jayden Daniels — QB
proj: 371.59
lineup_gain: 371.59
VOR(shadow): 69.7

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82
lineup_gain(VOR-space): 132.82

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 127.42
V2 EV (two-pick): 711.61
V2 expected future q: Jayden Daniels (QB)

next pick: #11
picks until next (others): 0
wait distance: 1
```

```
SLOT 10 — PICK 2 (overall #11, round 2)

RAW:
Ja'Marr Chase — WR
proj: 340.02
lineup_gain: 340.02
VOR(shadow): 127.42

VOR:
Saquon Barkley — RB
proj: 325.99
replacement: 193.17
VOR: 132.82
lineup_gain(VOR-space): 132.82

V2:
Ja'Marr Chase — WR
proj: 340.02
VOR(shadow): 127.42
V2 EV (two-pick): 1012.96
V2 expected future q: Malik Nabers (WR)

next pick: #30
picks until next (others): 18
wait distance: 19
```

```
SLOT 10 — PICK 3 (overall #30, round 3)

RAW:
Malik Nabers — WR
proj: 301.35
lineup_gain: 301.35
VOR(shadow): 100.33

VOR:
Kyren Williams — RB
proj: 284.05
replacement: 137.02
VOR: 147.02
lineup_gain(VOR-space): 147.02

V2:
Malik Nabers — WR
proj: 301.35
VOR(shadow): 100.33
V2 EV (two-pick): 1297.01
V2 expected future q: Kyren Williams (RB)

next pick: #31
picks until next (others): 0
wait distance: 1
```

## Reading guide

- Log shows turns where **any** of RAW / VOR / V2 disagree on player_id.
- `V2 expected future q` is the ADP-greedy survivor V2 would take at the next user pick — the opportunity-cost signal.
- Board driver only affects continuation after the logged turn.
