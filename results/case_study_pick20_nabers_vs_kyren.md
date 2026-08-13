# Case study — Pick #20 Nabers vs Kyren (one-pick lookahead)

## Setup

- seed: `0`
- slot: **1**
- freeze overall: **#20**
- board driver to freeze: `marginal` (raw R1 already made)
- preset: `league_default`
- pick #21 rule: highest ESPN proj at complementary position
- primary score: raw lineup_ev starter points (ESPN projections)

## Question

At slot 1 pick #20 the wait to #21 is **one pick** (zero others). Does positional VOR's Kyren choice beat the cross-positional alternative Nabers + best RB at #21 on **final two-pick raw starter EV**?

## Freeze state

Current roster EV: **371.6**

- Jayden Daniels (QB) — 371.6

### Strategy recommendations at #20

- RAW → **Malik Nabers** (WR) proj 301.4
- VOR → **Kyren Williams** (RB) proj 284.1

## Branches

### Branch A — VOR choice (Kyren + best WR@21)

- Now: **Kyren Williams** (RB) proj 284.1 (positional VOR 147.0)
- #21: **Malik Nabers** (WR) proj 301.4 — _best remaining WR by ESPN proj_
- Final starter points: **957.0**
- VOR-space starter total (footnote): 309.5

| slot | players | pts |
| --- | --- | ---: |
| QB | Jayden Daniels (371.6) | 371.6 |
| RB | Kyren Williams (284.1) | 284.1 |
| WR | Malik Nabers (301.4) | 301.4 |

- RB starter contribution (RB slots + RB-in-FLEX): **284.1**
- WR starter contribution (WR slots + WR-in-FLEX): **301.4**
- FLEX contribution: **0.0**
- Bench (unused): —

### Branch B — alternative (Nabers + best RB@21)

- Now: **Malik Nabers** (WR) proj 301.4 (positional VOR 90.2)
- #21: **Kyren Williams** (RB) proj 284.1 — _best remaining RB by ESPN proj_
- Final starter points: **957.0**
- VOR-space starter total (footnote): 309.5

| slot | players | pts |
| --- | --- | ---: |
| QB | Jayden Daniels (371.6) | 371.6 |
| RB | Kyren Williams (284.1) | 284.1 |
| WR | Malik Nabers (301.4) | 301.4 |

- RB starter contribution (RB slots + RB-in-FLEX): **284.1**
- WR starter contribution (WR slots + WR-in-FLEX): **301.4**
- FLEX contribution: **0.0**
- Bench (unused): —

## Secondary counterfactual — other fork candidate gone at #21

Counterfactual: complementary #21 cannot be the other fork candidate (as if CPU took them between picks). Relevant when wait > 0; not the literal #20→#21 board.

### Kyren now + best WR ≠ Nabers

- Now: **Kyren Williams** (RB) proj 284.1
- #21: **Nico Collins** (WR) proj 289.1 — _best remaining WR by ESPN proj, excluding the other fork candidate_
- Final starter points: **944.8**

| slot | players | pts |
| --- | --- | ---: |
| QB | Jayden Daniels (371.6) | 371.6 |
| RB | Kyren Williams (284.1) | 284.1 |
| WR | Nico Collins (289.1) | 289.1 |

- RB starter contribution (RB slots + RB-in-FLEX): **284.1**
- WR starter contribution (WR slots + WR-in-FLEX): **289.1**
- FLEX contribution: **0.0**
- Bench (unused): —

### Nabers now + best RB ≠ Kyren

- Now: **Malik Nabers** (WR) proj 301.4
- #21: **Bucky Irving** (RB) proj 283.5 — _best remaining RB by ESPN proj, excluding the other fork candidate_
- Final starter points: **956.4**

| slot | players | pts |
| --- | --- | ---: |
| QB | Jayden Daniels (371.6) | 371.6 |
| RB | Bucky Irving (283.5) | 283.5 |
| WR | Malik Nabers (301.4) | 301.4 |

- RB starter contribution (RB slots + RB-in-FLEX): **283.5**
- WR starter contribution (WR slots + WR-in-FLEX): **301.4**
- FLEX contribution: **0.0**
- Bench (unused): —

**Δ if other gone** (Nabers branch − Kyren branch) = **+11.7**

## Verdict

- Commutative (mutual complements)? **yes**
- Δ (Nabers branch − Kyren branch) = **+0.0**
- Outcome: `commutative_tie`
- With back-to-back picks and both players still available, best WR after Kyren is Nabers and best RB after Nabers is Kyren — the branches draft the same two players (order irrelevant). This fork cannot adjudicate positional VOR; the relevant question is the secondary 'other player gone' gap, or a longer-wait fork.

## Interpretation guide

- If branches are **commutative** (each other's #21 pick) → back-to-back ownership means order cannot change the two-pick roster; this fork does not test VOR vs raw value — look at longer waits or the secondary gap.
- If Nabers branch wins (non-commutative) → positional VOR ≠ final roster value even with no waiting cost → strong case for V2-alpha.
- If Kyren branch wins → VOR's RB preference is justified here.
- Secondary Δ (other gone) approximates the stake when survival matters.
