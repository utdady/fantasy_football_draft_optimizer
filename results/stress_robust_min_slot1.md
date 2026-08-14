# β2-robust-min opponent-policy lean

## Setup

- n_sims per cell: **20**
- slots: `[1]`
- seed: `0`
- strategies: `marginal, marginal_vor, marginal_v2, robust_min` (paired seeds)
- V2-alpha lookahead: **adp_greedy (frozen)**
- robust_min lookahead: **min_f over adp_greedy+proj_greedy+vor**
- planner vs evaluator: Recommend() may use scenario futures; actual CPU picks use --policies only.
- opponent policies: `noisy_adp, adp_greedy, proj_greedy, vor`

- note: Diagnostic lean — not a validation/promotion of robust_min.
- note: For deterministic opponent policies (adp_greedy, proj_greedy, vor), repeated sims with different seeds reprint the same trajectory; win rates are not independent-trial estimates.
- note: noisy_adp has real sample variance across seeds.
- note: UI default remains marginal.

## R1 decision snapshot (empty board)

_R1 planner snapshot on empty board; independent of opponent policy at overall #1._

- α vs robust agree: **False**

| strategy | pick | pos | wait | ev / min | spread | worst | q |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| marginal_v2 | Ja'Marr Chase | WR | 18 | 711.61 | None | None | Jayden Daniels |
| robust_min | Jayden Daniels | QB | 18 | 672.94 | 16.18 | adp_greedy | Malik Nabers |
|  | ev_by_future=`{'adp_greedy': 672.94, 'proj_greedy': 672.94, 'vor': 689.12}` |  |  |  |  |  |  |
| marginal | Jayden Daniels | QB | None | None | None | None | None |
| marginal_vor | Bijan Robinson | RB | None | None | None | None | None |

## Matrix (headline deltas)

| opponent | slot | det? | raw | vor | α | robust | α−raw | rob−raw | rob−α |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| noisy_adp | 1 | no | 2428.9 | 2438.2 | 2500.2 | 2428.0 | +71.3 | -0.9 | -72.3 |
| adp_greedy | 1 | yes | 2406.4 | 2439.3 | 2482.7 | 2406.4 | +76.3 | +0.0 | -76.3 |
| proj_greedy | 1 | yes | 2330.7 | 2254.5 | 2313.7 | 2330.7 | -17.0 | +0.0 | +17.0 |
| vor | 1 | yes | 2030.6 | 2445.4 | 2072.0 | 2055.4 | +41.4 | +24.8 | -16.6 |

## R1 pick behavior (actual sims)

### noisy_adp · slot 1

- `marginal`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}
- `marginal_vor`: top=Bijan Robinson (RB) (100%); counts={'Bijan Robinson (RB)': 20}
- `marginal_v2`: top=Ja'Marr Chase (WR) (100%); counts={"Ja'Marr Chase (WR)": 20}
- `robust_min`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}

### adp_greedy · slot 1

- `marginal`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}
- `marginal_vor`: top=Bijan Robinson (RB) (100%); counts={'Bijan Robinson (RB)': 20}
- `marginal_v2`: top=Ja'Marr Chase (WR) (100%); counts={"Ja'Marr Chase (WR)": 20}
- `robust_min`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}

### proj_greedy · slot 1

- `marginal`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}
- `marginal_vor`: top=Bijan Robinson (RB) (100%); counts={'Bijan Robinson (RB)': 20}
- `marginal_v2`: top=Ja'Marr Chase (WR) (100%); counts={"Ja'Marr Chase (WR)": 20}
- `robust_min`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}

### vor · slot 1

- `marginal`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}
- `marginal_vor`: top=Bijan Robinson (RB) (100%); counts={'Bijan Robinson (RB)': 20}
- `marginal_v2`: top=Ja'Marr Chase (WR) (100%); counts={"Ja'Marr Chase (WR)": 20}
- `robust_min`: top=Jayden Daniels (QB) (100%); counts={'Jayden Daniels (QB)': 20}


## Loss diagnostics (focus vs raw)

### noisy_adp · slot 1 (3 losses; stochastic)

- sim 8 seed=8072: Δ=-8.2 (raw 2364.9 vs robust_min 2356.8)
  - R1 raw=Jayden Daniels (QB); focus=Jayden Daniels (QB)
  - no early q-survival failures recorded
- sim 14 seed=14126: Δ=-8.2 (raw 2406.2 vs robust_min 2398.1)
  - R1 raw=Jayden Daniels (QB); focus=Jayden Daniels (QB)
  - no early q-survival failures recorded
- sim 17 seed=17153: Δ=-2.5 (raw 2463.6 vs robust_min 2461.1)
  - R1 raw=Jayden Daniels (QB); focus=Jayden Daniels (QB)
  - no early q-survival failures recorded

## Reading

- 🟢 Best: robust slightly worse vs ADP-like, much better vs proj_greedy.
- 🟡 Interesting: fixes proj but crushes ADP-like → minimax too sharp.
- 🔴 Bad: still fails proj_greedy → need richer future-board model.
- Deterministic CPUs: treat mean Δ as a single-trajectory gap, not a win-rate claim.
- Do not promote robust_min to UI from this lean alone.
