# VOR-lite ablation — slot 1 n=50 (real ESPN)

## Setup

- n_sims per slot: **50**
- teams: **10**
- preset: `league_default`
- seed: `0`
- slots: `[1]`
- strategies: `adp, marginal, marginal_no_qb_r1, marginal_vor`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- CPU: noisy ADP (not human ESPN managers)

## Notes

- Scored on ESPN preseason projections (not actual season outcomes).
- Opponents use noisy-ADP CPU policy — not human ESPN managers.

## Slot matrix

| slot | adp | marginal | marginal_no_qb_r1 | marginal_vor | marginal−adp | win_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2173.0 | 2423.0 | 2460.1 | 2439.0 | +250.0 | 100.0% |

`win_rate` = paired starter-points win rate (not wide-receiver share).

## Position mix (user picks)

### Slot 1

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 17%, RB 33%, WR 34%, TE 8%, DST 8% | R1: RB 100% · R2: RB 52%, WR 36%, TE 12% · R3: QB 10%, RB 60%, WR 10%, TE 20% |
| marginal | QB 12%, RB 29%, WR 36%, TE 12%, DST 11% | R1: QB 100% · R2: RB 36%, WR 64% · R3: RB 18%, WR 82% |
| marginal_no_qb_r1 | QB 12%, RB 29%, WR 36%, TE 13%, DST 11% | R1: WR 100% · R2: QB 100% · R3: RB 44%, WR 56% |
| marginal_vor | QB 12%, RB 37%, WR 28%, TE 12%, DST 10% | R1: RB 100% · R2: RB 98%, WR 2% · R3: RB 100% |

## Pairwise vs ADP (starter pts)

| strategy | mean | median | mean d vs ADP | win vs ADP |
| --- | ---: | ---: | ---: | ---: |
| adp | 2173.0 | 2180.0 | — | — |
| marginal (raw) | 2423.0 | 2425.6 | +250.0 | 100% |
| marginal_vor | 2439.0 | 2432.5 | +266.0 | 100% |
| marginal_no_qb_r1 | 2460.1 | 2459.1 | +287.1 | 100% |

`marginal_vor` vs raw `marginal`: mean d **+16.0**, win **66%**.

## Takeaways

1. **R1 QB was an artifact of the objective**, not good judgment: raw marginal R1 = 100% QB; VOR-lite R1 = 100% RB; no-QB control R1 = 100% WR.
2. **Banning R1 QB improves** starter EV vs raw marginal (+287 vs +250 over ADP) — so the previous edge was *not* helped by R1 QB under this CPU/scoring; it was partly held back by it.
3. **VOR-lite also beats ADP** (+266) and slightly beats raw marginal, with R1–R3 heavily RB — mechanism check passed, but early-round RB concentration may be the next thing to scrutinize (FLEX/replacement calibration).
4. Default product strategy is still raw `marginal` in the UI; treat `marginal_vor` as the V1 candidate pending more slots / candidate-window checks.
5. Caveat unchanged: noisy-ADP CPU + preseason ESPN projections, not humans or actual season outcomes.

