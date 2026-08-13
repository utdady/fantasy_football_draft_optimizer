# V1 validation — VOR vs ADP/raw across slots 1-10 (real ESPN)

## Setup

- n_sims per slot: **50**
- teams: **10**
- preset: `league_default`
- seed: `0`
- slots: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`
- strategies: `adp, marginal, marginal_vor`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- CPU: noisy ADP (not human ESPN managers)

## Notes

- Scored on ESPN preseason projections (not actual season outcomes).
- Opponents use noisy-ADP CPU policy — not human ESPN managers.

## Slot matrix

| slot | adp | marginal | marginal_vor | vor−adp | vor>adp | vor−raw | vor>raw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2173.0 | 2423.0 | 2439.0 | +266.0 | 100.0% | +16.0 | 66.0% |
| 2 | 2173.2 | 2427.2 | 2445.1 | +271.9 | 100.0% | +17.9 | 72.0% |
| 3 | 2160.9 | 2432.8 | 2447.4 | +286.5 | 100.0% | +14.6 | 66.0% |
| 4 | 2187.7 | 2439.8 | 2447.3 | +259.6 | 100.0% | +7.5 | 56.0% |
| 5 | 2162.6 | 2444.3 | 2443.4 | +280.8 | 100.0% | -0.8 | 38.0% |
| 6 | 2147.4 | 2449.7 | 2441.1 | +293.7 | 100.0% | -8.6 | 38.0% |
| 7 | 2181.0 | 2451.5 | 2438.9 | +257.9 | 98.0% | -12.6 | 32.0% |
| 8 | 2104.6 | 2449.5 | 2433.4 | +328.8 | 100.0% | -16.1 | 24.0% |
| 9 | 2144.8 | 2447.3 | 2429.0 | +284.2 | 100.0% | -18.3 | 18.0% |
| 10 | 2157.2 | 2446.5 | 2433.6 | +276.4 | 98.0% | -12.9 | 30.0% |

`win%` / `vor>adp` / `vor>raw` = paired starter-points win rate (not wide-receiver share).

## Position mix (user picks)

### Slot 1

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 17%, RB 33%, WR 34%, TE 8%, DST 8% | R1: RB 100% · R2: RB 52%, WR 36%, TE 12% · R3: QB 10%, RB 60%, WR 10%, TE 20% |
| marginal | QB 12%, RB 29%, WR 36%, TE 12%, DST 11% | R1: QB 100% · R2: RB 36%, WR 64% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 37%, WR 28%, TE 12%, DST 10% | R1: RB 100% · R2: RB 98%, WR 2% · R3: RB 100% |

### Slot 2

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 31%, WR 35%, TE 8%, DST 10% | R1: RB 100% · R2: RB 56%, WR 34%, TE 10% · R3: QB 18%, RB 50%, WR 16%, TE 16% |
| marginal | QB 13%, RB 29%, WR 35%, TE 14%, DST 10% | R1: QB 100% · R2: RB 46%, WR 54% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 35%, WR 30%, TE 12%, DST 10% | R1: RB 100% · R2: RB 100% · R3: RB 100% |

### Slot 3

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 34%, WR 36%, TE 8%, DST 8% | R1: RB 92%, WR 8% · R2: RB 52%, WR 44%, TE 4% · R3: QB 14%, RB 60%, WR 16%, TE 10% |
| marginal | QB 13%, RB 30%, WR 34%, TE 12%, DST 12% | R1: QB 100% · R2: RB 58%, WR 42% · R3: RB 10%, WR 90% |
| marginal_vor | QB 14%, RB 35%, WR 30%, TE 11%, DST 11% | R1: RB 84%, WR 16% · R2: RB 98%, WR 2% · R3: RB 100% |

### Slot 4

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 32%, WR 37%, TE 8%, DST 8% | R1: RB 82%, WR 18% · R2: RB 50%, WR 46%, TE 4% · R3: QB 18%, RB 48%, WR 20%, TE 14% |
| marginal | QB 12%, RB 30%, WR 35%, TE 12%, DST 10% | R1: QB 100% · R2: RB 66%, WR 34% · R3: RB 8%, WR 92% |
| marginal_vor | QB 13%, RB 34%, WR 30%, TE 12%, DST 11% | R1: RB 74%, WR 26% · R2: RB 100% · R3: RB 100% |

### Slot 5

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 13%, RB 34%, WR 36%, TE 10%, DST 6% | R1: RB 68%, WR 32% · R2: RB 44%, WR 56% · R3: QB 14%, RB 50%, WR 12%, TE 24% |
| marginal | QB 13%, RB 30%, WR 32%, TE 13%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 12%, WR 88% |
| marginal_vor | QB 13%, RB 36%, WR 30%, TE 12%, DST 10% | R1: RB 76%, WR 24% · R2: RB 92%, WR 8% · R3: RB 100% |

### Slot 6

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 39%, TE 11%, DST 6% | R1: RB 56%, WR 44% · R2: RB 40%, WR 60% · R3: QB 6%, RB 56%, WR 14%, TE 24% |
| marginal | QB 14%, RB 30%, WR 36%, TE 11%, DST 10% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 14%, WR 86% |
| marginal_vor | QB 14%, RB 34%, WR 30%, TE 11%, DST 12% | R1: RB 82%, WR 18% · R2: RB 96%, WR 2%, TE 2% · R3: RB 100% |

### Slot 7

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 38%, TE 12%, DST 6% | R1: RB 46%, WR 54% · R2: RB 50%, WR 50% · R3: QB 10%, RB 58%, WR 12%, TE 20% |
| marginal | QB 14%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 68%, WR 32% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 35%, WR 29%, TE 12%, DST 12% | R1: RB 96%, WR 4% · R2: RB 94%, WR 6% · R3: RB 100% |

### Slot 8

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 43%, TE 10%, DST 6% | R1: RB 42%, WR 58% · R2: RB 36%, WR 64% · R3: QB 10%, RB 60%, WR 12%, TE 18% |
| marginal | QB 13%, RB 30%, WR 33%, TE 13%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 10%, WR 90% |
| marginal_vor | QB 13%, RB 36%, WR 28%, TE 13%, DST 11% | R1: RB 90%, WR 10% · R2: RB 96%, WR 4% · R3: RB 100% |

### Slot 9

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 41%, TE 12%, DST 7% | R1: RB 44%, WR 56% · R2: RB 44%, WR 56% · R3: QB 8%, RB 44%, WR 24%, TE 24% |
| marginal | QB 13%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 30%, WR 70% |
| marginal_vor | QB 13%, RB 36%, WR 28%, TE 12%, DST 11% | R1: RB 96%, WR 4% · R2: RB 92%, WR 8% · R3: RB 100% |

### Slot 10

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 26%, WR 40%, TE 13%, DST 7% | R1: RB 44%, WR 56% · R2: RB 34%, WR 66% · R3: QB 8%, RB 50%, WR 22%, TE 20% |
| marginal | QB 14%, RB 32%, WR 32%, TE 12%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 32%, WR 68% |
| marginal_vor | QB 13%, RB 35%, WR 29%, TE 11%, DST 10% | R1: RB 96%, WR 4% · R2: RB 86%, WR 14% · R3: RB 100% |

## Takeaways

1. **VOR vs ADP is robust across seats:** vor−adp ≈ **+258 to +329**, win rate **98–100%** at every slot. No catastrophic late-slot collapse vs ADP.
2. **VOR vs raw marginal is seat-dependent:** ahead at slots **1–4** (+7 to +18, win 56–72%); behind at slots **5–10** (−1 to −18, win 18–38%). The continuous VOR term is not a clear win over raw marginal once the pick seat moves mid/late.
3. **R1 behavior stays differentiated:** raw marginal remains ~100% QB R1; VOR stays RB-heavy R1 (~90–100% RB) even at late slots — the objective difference is real, not slot-1-only.
4. **UI default decision:** safe to treat VOR as beating ADP everywhere; flipping the default over raw `marginal` is a judgment call given the thin/negative vor−raw gap at mid–late seats under this CPU + ESPN scoring.
5. Caveat unchanged: noisy-ADP CPU + preseason projections, not human managers or actual season outcomes.

