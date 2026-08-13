# Ablation backtest — slots 1-10 (real ESPN ingest)

## Setup

- n_sims per slot: **50**
- teams: **10**
- preset: `league_default`
- seed: `0`
- slots: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`
- strategies: `adp, greedy, marginal`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- CPU: noisy ADP (not human ESPN managers)

## Notes

- Scored on ESPN preseason projections (not actual season outcomes).
- Opponents use noisy-ADP CPU policy — not human ESPN managers.

## Slot matrix

| slot | adp | greedy | marginal | marginal−adp | win_rate | marginal−greedy | win_vs_greedy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2173.0 | 792.0 | 2423.0 | +250.0 | 100.0% | +1630.9 | 100.0% |
| 2 | 2173.2 | 777.7 | 2427.2 | +254.0 | 100.0% | +1649.5 | 100.0% |
| 3 | 2160.9 | 785.5 | 2432.8 | +271.9 | 100.0% | +1647.3 | 100.0% |
| 4 | 2187.7 | 775.0 | 2439.8 | +252.1 | 98.0% | +1664.8 | 100.0% |
| 5 | 2162.6 | 774.9 | 2444.3 | +281.7 | 100.0% | +1669.3 | 100.0% |
| 6 | 2147.4 | 759.1 | 2449.7 | +302.3 | 100.0% | +1690.6 | 100.0% |
| 7 | 2181.0 | 732.4 | 2451.5 | +270.5 | 100.0% | +1719.0 | 100.0% |
| 8 | 2104.6 | 732.4 | 2449.5 | +344.9 | 100.0% | +1717.0 | 100.0% |
| 9 | 2144.8 | 716.6 | 2447.3 | +302.5 | 98.0% | +1730.7 | 100.0% |
| 10 | 2157.2 | 695.2 | 2446.5 | +289.3 | 100.0% | +1751.3 | 100.0% |

`win_rate` = paired starter-points win rate (not wide-receiver share).

## Position mix (user picks)

### Slot 1

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 17%, RB 33%, WR 34%, TE 8%, DST 8% | R1: RB 100% · R2: RB 52%, WR 36%, TE 12% · R3: QB 10%, RB 60%, WR 10%, TE 20% |
| greedy | QB 90%, RB 5%, WR 5% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 12%, RB 29%, WR 36%, TE 12%, DST 11% | R1: QB 100% · R2: RB 36%, WR 64% · R3: RB 18%, WR 82% |

### Slot 2

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 31%, WR 35%, TE 8%, DST 10% | R1: RB 100% · R2: RB 56%, WR 34%, TE 10% · R3: QB 18%, RB 50%, WR 16%, TE 16% |
| greedy | QB 90%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 13%, RB 29%, WR 35%, TE 14%, DST 10% | R1: QB 100% · R2: RB 46%, WR 54% · R3: RB 18%, WR 82% |

### Slot 3

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 34%, WR 36%, TE 8%, DST 8% | R1: RB 92%, WR 8% · R2: RB 52%, WR 44%, TE 4% · R3: QB 14%, RB 60%, WR 16%, TE 10% |
| greedy | QB 90%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 13%, RB 30%, WR 34%, TE 12%, DST 12% | R1: QB 100% · R2: RB 58%, WR 42% · R3: RB 10%, WR 90% |

### Slot 4

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 32%, WR 37%, TE 8%, DST 8% | R1: RB 82%, WR 18% · R2: RB 50%, WR 46%, TE 4% · R3: QB 18%, RB 48%, WR 20%, TE 14% |
| greedy | QB 90%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 12%, RB 30%, WR 35%, TE 12%, DST 10% | R1: QB 100% · R2: RB 66%, WR 34% · R3: RB 8%, WR 92% |

### Slot 5

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 13%, RB 34%, WR 36%, TE 10%, DST 6% | R1: RB 68%, WR 32% · R2: RB 44%, WR 56% · R3: QB 14%, RB 50%, WR 12%, TE 24% |
| greedy | QB 90%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 13%, RB 30%, WR 32%, TE 13%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 12%, WR 88% |

### Slot 6

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 39%, TE 11%, DST 6% | R1: RB 56%, WR 44% · R2: RB 40%, WR 60% · R3: QB 6%, RB 56%, WR 14%, TE 24% |
| greedy | QB 91%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 14%, RB 30%, WR 36%, TE 11%, DST 10% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 14%, WR 86% |

### Slot 7

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 38%, TE 12%, DST 6% | R1: RB 46%, WR 54% · R2: RB 50%, WR 50% · R3: QB 10%, RB 58%, WR 12%, TE 20% |
| greedy | QB 92%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 14%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 68%, WR 32% · R3: RB 18%, WR 82% |

### Slot 8

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 43%, TE 10%, DST 6% | R1: RB 42%, WR 58% · R2: RB 36%, WR 64% · R3: QB 10%, RB 60%, WR 12%, TE 18% |
| greedy | QB 92%, RB 5%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 13%, RB 30%, WR 33%, TE 13%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 10%, WR 90% |

### Slot 9

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 41%, TE 12%, DST 7% | R1: RB 44%, WR 56% · R2: RB 44%, WR 56% · R3: QB 8%, RB 44%, WR 24%, TE 24% |
| greedy | QB 92%, RB 4%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 13%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 30%, WR 70% |

### Slot 10

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 26%, WR 40%, TE 13%, DST 7% | R1: RB 44%, WR 56% · R2: RB 34%, WR 66% · R3: QB 8%, RB 50%, WR 22%, TE 20% |
| greedy | QB 92%, RB 4%, WR 4% | R1: QB 100% · R2: QB 100% · R3: QB 100% |
| marginal | QB 14%, RB 32%, WR 32%, TE 12%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 32%, WR 68% |

## Aggregate takeaways

- Marginal − ADP mean starter Δ ≈ **+250 to +345** across slots; win rate **98–100%** (slots 4 and 9 had 98%).
- Greedy collapses (~700–800 starter pts) with **~90%+ QB** of all picks and 100% QB in rounds 1–3 — raw ESPN points ≠ draft value under 1-QB / multi-FLEX.
- Marginal overall mix is balanced (~QB 13%, RB 30%, WR 34%, TE 12%, DST 11%) — **not** a “only draft WRs” artifact. Note: marginal R1 is consistently **100% QB** (empty roster + elite ESPN QB proj fills the single QB slot first), then R2–R3 skew RB/WR.
- Caveat unchanged: noisy-ADP CPU + preseason proj scoring, not human ESPN managers or actual season outcomes.

