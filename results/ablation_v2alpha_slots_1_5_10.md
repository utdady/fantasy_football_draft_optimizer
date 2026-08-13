# Ablation backtest results

## Setup

- n_sims per slot: **20**
- teams: **10**
- preset: `league_default`
- seed: `0`
- slots: `[1, 5, 10]`
- strategies: `adp, marginal, marginal_vor, marginal_v2`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- CPU: noisy ADP (not human ESPN managers)

## Notes

- Scored on ESPN preseason projections (not actual season outcomes).
- Opponents use noisy-ADP CPU policy — not human ESPN managers.
- `marginal_v2` is experimental V2-alpha: scores candidates by raw two-pick EV under a **deterministic ADP-greedy** future to the next user pick (lookahead ≠ the noisy CPU that actually drafts in the sim).
- UI default remains raw `marginal`.

## Slot matrix

| slot | adp | marginal | marginal_vor | marginal_v2 | vor−adp | vor>adp | vor−raw | vor>raw | v2−raw | v2>raw | v2−vor | v2>vor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2186.4 | 2428.9 | 2438.2 | 2500.2 | +251.8 | 100.0% | +9.3 | 60.0% | +71.3 | 100.0% | +62.0 | 100.0% |
| 5 | 2147.0 | 2443.5 | 2442.0 | 2506.4 | +295.0 | 100.0% | -1.5 | 40.0% | +62.9 | 95.0% | +64.4 | 95.0% |
| 10 | 2175.2 | 2447.9 | 2437.5 | 2484.2 | +262.3 | 100.0% | -10.4 | 30.0% | +36.3 | 85.0% | +46.8 | 100.0% |

`win%` / `vor>adp` / `vor>raw` / `v2>raw` / `v2>vor` = paired starter-points win rate (not wide-receiver share).

## Position mix (user picks)

### Slot 1

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 17%, RB 32%, WR 34%, TE 8%, DST 8% | R1: RB 100% · R2: RB 55%, WR 30%, TE 15% · R3: QB 15%, RB 60%, WR 5%, TE 20% |
| marginal | QB 13%, RB 31%, WR 35%, TE 12%, DST 9% | R1: QB 100% · R2: RB 45%, WR 55% · R3: RB 20%, WR 80% |
| marginal_vor | QB 12%, RB 37%, WR 27%, TE 13%, DST 10% | R1: RB 100% · R2: RB 95%, WR 5% · R3: RB 100% |
| marginal_v2 | QB 12%, RB 30%, WR 36%, TE 9%, DST 12% | R1: WR 100% · R2: RB 45%, WR 55% · R3: RB 35%, WR 65% |

### Slot 5

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 34%, WR 37%, TE 11%, DST 6% | R1: RB 70%, WR 30% · R2: RB 40%, WR 60% · R3: QB 15%, RB 60%, WR 10%, TE 15% |
| marginal | QB 13%, RB 32%, WR 32%, TE 12%, DST 11% | R1: QB 100% · R2: RB 75%, WR 25% · R3: RB 5%, WR 95% |
| marginal_vor | QB 12%, RB 35%, WR 29%, TE 12%, DST 11% | R1: RB 80%, WR 20% · R2: RB 90%, WR 10% · R3: RB 100% |
| marginal_v2 | QB 13%, RB 28%, WR 36%, TE 11%, DST 11% | R1: RB 45%, WR 55% · R2: RB 75%, WR 25% · R3: RB 10%, WR 90% |

### Slot 10

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 28%, WR 39%, TE 14%, DST 7% | R1: RB 50%, WR 50% · R2: RB 35%, WR 65% · R3: QB 15%, RB 50%, WR 15%, TE 20% |
| marginal | QB 14%, RB 32%, WR 32%, TE 12%, DST 10% | R1: QB 100% · R2: RB 70%, WR 30% · R3: RB 15%, WR 85% |
| marginal_vor | QB 13%, RB 34%, WR 30%, TE 11%, DST 11% | R1: RB 100% · R2: RB 75%, WR 25% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 30%, WR 35%, TE 11%, DST 9% | R1: RB 70%, WR 30% · R2: RB 60%, WR 40% · R3: RB 35%, WR 65% |

