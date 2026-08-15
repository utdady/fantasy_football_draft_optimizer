# P2.2C decision-space coverage

- snapshot: `2024-preseason-2024-09-01-ffc12`
- evaluable: **0** (locked)
- decision_space_gate: **pass**
- reasons: none

Board coverage ≠ outcome coverage. Unmapped ffc:* players remain draftable but are silent losses for actual-PPR scoring. No nflverse attach in this report. Not production marginal.

## Overall mapping

| Metric | Value |
| --- | ---: |
| Players | 205 |
| Mapped | 205 (100.0%) |
| Unmapped | 0 |
| Mapped with gsis | 193 (94.1%) |
| Outcome-ready (gsis or dst:TEAM) | 205 (100.0%) |

_Prior failed report preserved at `phase2_p22c_decision_space_coverage.md` (v1)._

## Top-N ADP coverage (lowest ADP)

| Band | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| Top 50 | 50 | 50 | 0 | 100.0% |
| Top 100 | 100 | 100 | 0 | 100.0% |
| Top 150 | 150 | 150 | 0 | 100.0% |

## Unmapped by ADP band

| Band | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| 1-50 | 50 | 50 | 0 | 100.0% |
| 51-100 | 50 | 50 | 0 | 100.0% |
| 101-150 | 50 | 50 | 0 | 100.0% |
| 151+ | 55 | 55 | 0 | 100.0% |

## Unmapped by position

| Pos | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| DST | 12 | 12 | 0 | 100.0% |
| K | 15 | 15 | 0 | 100.0% |
| QB | 26 | 26 | 0 | 100.0% |
| RB | 60 | 60 | 0 | 100.0% |
| TE | 20 | 20 | 0 | 100.0% |
| WR | 72 | 72 | 0 | 100.0% |

## All unmapped (ADP-ranked)

| ADP rank | ADP | Pos | Name | Team | reason |
| ---: | ---: | --- | --- | --- | --- |

## Strategy selections of unmapped / no-gsis

- slots: [1, 5, 10] · n_sims: 3 · seed0: 42
- user picks scanned: 270
- gate_strategy_unmapped_zero: **True**

### `adp_baseline` — 0 pick-events, 0 unique players

_none_

### `adp_structural` — 0 pick-events, 0 unique players

_none_

## Board-wide unmapped picks (secondary)

- board pick-events with unmapped/no-gsis: 0
- unique players: 0

**Next:** decision_space_gate=pass � safe to attach nflverse 2024 PPR next. DST outcomes still need team-level scoring (dst:TEAM), not GSIS player weeks. Keep evaluable=0 until outcome coverage gates pass. Do not retune ADP curve.
