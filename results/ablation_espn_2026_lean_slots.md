# Ablation backtest — lean slots (real ESPN ingest)

Reviewable artifact for the first real-data ablation run. **Not synthetic.**

## Setup

- n_sims per slot: **50**
- teams: **10**
- preset: `league_default` (no K, 2 FLEX, 16 rounds)
- seed: `0`
- slots: `1, 5, 10`
- strategies: `adp, greedy, marginal`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- data: local ingested `draftopt.db` (~859 players / ~774 ESPN projections at run time)
- CPU: noisy ADP policy (**not** human ESPN managers)
- commit context: harness after paired RNG + greedy ablation (`5ee0526` era)

## Notes

- `win_rate` below means **paired starter-points win rate**, not wide-receiver share.
- Huge greedy collapse is expected under 1-QB / multi-FLEX constraints when ESPN QB projections outrank RB/WR in raw points.
- Position/round mix was **not** collected in this run; see later `slots_1-10` results for that.

## Slot matrix

| slot | adp | greedy | marginal | marginal−adp | win_rate | marginal−greedy | win_vs_greedy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2173.0 | 792.0 | 2423.0 | +250.0 | 100.0% | +1630.9 | 100.0% |
| 5 | 2162.6 | 774.9 | 2444.3 | +281.7 | 100.0% | +1669.3 | 100.0% |
| 10 | 2157.2 | 695.2 | 2446.5 | +289.3 | 100.0% | +1751.3 | 100.0% |

## Raw stdout

```text
Matrix n=50 teams=10 preset=league_default seed=0 slots=[1, 5, 10]
slot        adp     greedy   marginal    m-adp   m>adp  m-greed  m>greed
   1     2173.0      792.0     2423.0   +250.0  100.0%  +1630.9   100.0%
   5     2162.6      774.9     2444.3   +281.7  100.0%  +1669.3   100.0%
  10     2157.2      695.2     2446.5   +289.3  100.0%  +1751.3   100.0%
```

## Interpretation (tentative)

1. Marginal beats ADP by ~250–290 starter pts across early/mid/late slots under this CPU.
2. Greedy (highest ESPN projection, no roster awareness) collapses — supports “projection ≠ draft value.”
3. Next: full slots 1–10 at n=50 with position/round histograms + candidate-window sensitivity.
