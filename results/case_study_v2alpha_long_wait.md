# Case study — V2-alpha long-wait survival (Kyren / Nabers)

## Setup

- seed: `0`
- preset: `league_default`
- board to freeze: `marginal` (raw R1)
- opponent future in EV: **ADP-greedy** (deterministic)
- score: raw `lineup_ev` starter points

## Part 1 — Freeze at overall #20

Roster: Jayden Daniels

- RAW → Malik Nabers (WR)
- VOR → Kyren Williams (RB)
- Literal next pick: #21 (ADP×0 others)

### V2 top recommendations (literal)

- Nico Collins (WR) EV=962.07 q=Malik Nabers — two-pick EV 962.1 (take now → ADP×0 → Malik Nabers WR at #21)
- Malik Nabers (WR) EV=962.07 q=Nico Collins — two-pick EV 962.1 (take now → ADP×0 → Nico Collins WR at #21)
- Kyren Williams (RB) EV=956.99 q=Malik Nabers — two-pick EV 957.0 (take now → ADP×0 → Malik Nabers WR at #21)

### Literal V2 EV (Kyren vs Nabers, ADP×0)

n_cpu = 0
- **A Kyren-first**: Kyren Williams (RB) proj 284.1
  - q after ADP future: Malik Nabers (WR) proj 301.4
  - two-pick EV: **957.0** (one-pick 655.6)
- **B Nabers-first**: Malik Nabers (WR) proj 301.4
  - q after ADP future: Nico Collins (WR) proj 289.1
  - two-pick EV: **962.1** (one-pick 672.9)
- Δ (Nabers − Kyren) = **+5.1**

### Survival counterfactual (same board, ADP×18)

Pretend the next user pick is ~18 opponents away (not the literal #21). This isolates survival without leaving the #20 fork.

n_cpu = 18
- **A Kyren-first**: Kyren Williams (RB) proj 284.1
  - q after ADP future: Bucky Irving (RB) proj 283.5
  - two-pick EV: **939.1** (one-pick 655.6)
- **B Nabers-first**: Malik Nabers (WR) proj 301.4
  - q after ADP future: Kyren Williams (RB) proj 284.1
  - two-pick EV: **957.0** (one-pick 672.9)
- Δ (Nabers − Kyren) = **+17.9**

## Part 2 — Freeze at #21 after Nabers (authentic #21→#40)

After Nabers at #20; branch A = Kyren if available else VOR#21; branch B = raw#21; n_cpu = authentic picks_until_next.

Roster: Jayden Daniels, Malik Nabers

- next pick: #40 (ADP×18 others)
- RAW → Nico Collins (WR)
- VOR → Kyren Williams (RB)

### V2 top recommendations

- Nico Collins (WR) EV=1245.53 q=Bucky Irving wait=18 — two-pick EV 1245.5 (take now → ADP×18 → Bucky Irving RB at #40)
- Kyren Williams (RB) EV=1240.46 q=Bucky Irving wait=18 — two-pick EV 1240.5 (take now → ADP×18 → Bucky Irving RB at #40)
- Bucky Irving (RB) EV=1240.46 q=Kyren Williams wait=18 — two-pick EV 1240.5 (take now → ADP×18 → Kyren Williams RB at #40)

### V2 EV: VOR-ish branch vs raw branch

n_cpu = 18
- **A (Kyren/VOR)**: Kyren Williams (RB) proj 284.1
  - q after ADP future: Bucky Irving (RB) proj 283.5
  - two-pick EV: **1240.5** (one-pick 957.0)
- **B (raw)**: Nico Collins (WR) proj 289.1
  - q after ADP future: Bucky Irving (RB) proj 283.5
  - two-pick EV: **1245.5** (one-pick 962.1)
- Δ (raw branch − A) = **+5.1**

## Reading

- Part 1 literal: with ADP×0, V2's best *q* is raw-marginal among **all** survivors — not forced to be the other fork candidate. Nabers→Nico (two WRs) can beat Kyren→Nabers when WR slots are empty.
- Part 1 ADP×18: survival alone — after 18 ADP-greedy removals, Nabers-first still keeps Kyren as q; Kyren-first is stuck with a second RB (Bucky). Large positive Δ favors securing the scarce WR first.
- Part 2: authentic #21→#40 after Nabers; V2 prefers Nico over Kyren on the same Bucky-at-#40 future (+5.1).
