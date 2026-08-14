# V2-beta opponent-policy stress

## Setup

- n_sims per cell: **10**
- slots: `[1]`
- seed: `0`
- strategies: `marginal, marginal_vor, marginal_v2, marginal_v2_beta` (paired seeds)
- V2-alpha lookahead: **adp_greedy (frozen)**
- V2-beta lookahead: **equal mix adp_greedy+proj_greedy+vor**
- opponent policies: `noisy_adp, adp_greedy, proj_greedy, vor`

- note: For deterministic opponent policies (adp_greedy, proj_greedy, vor), repeated sims with different seeds reprint the same trajectory; win rates are not independent-trial estimates.
- note: noisy_adp has real sample variance across seeds.

## Matrix (headline deltas)

| opponent | slot | det? | raw | vor | α | β | α−raw | β−raw | β−α |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| noisy_adp | 1 | no | 2409.1 | 2417.3 | 2492.8 | 2466.2 | +83.7 | +57.1 | -26.6 |
| adp_greedy | 1 | yes | 2406.4 | 2439.3 | 2482.7 | 2457.3 | +76.3 | +50.9 | -25.4 |
| proj_greedy | 1 | yes | 2330.7 | 2254.5 | 2313.7 | 2301.8 | -17.0 | -28.8 | -11.8 |
| vor | 1 | yes | 2030.6 | 2445.4 | 2072.0 | 2096.8 | +41.4 | +66.2 | +24.8 |

## Loss diagnostics (sample vs raw)

### noisy_adp · slot 1 (1 losses; stochastic)

- sim 3 seed=3027: Δ=-18.5 (raw 2424.4 vs marginal_v2_beta 2405.9)
  - R1 raw=Jayden Daniels (QB); focus=Ja'Marr Chase (WR)
  - no early q-survival failures recorded

### proj_greedy · slot 1 (10 losses; deterministic)

- sim 0 seed=0: Δ=-28.8 (raw 2330.7 vs marginal_v2_beta 2301.8)
  - R1 raw=Jayden Daniels (QB); focus=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18
- sim 1 seed=1009: Δ=-28.8 (raw 2330.7 vs marginal_v2_beta 2301.8)
  - R1 raw=Jayden Daniels (QB); focus=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18
- sim 2 seed=2018: Δ=-28.8 (raw 2330.7 vs marginal_v2_beta 2301.8)
  - R1 raw=Jayden Daniels (QB); focus=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18

## Reading

- Success for β: shrink proj_greedy catastrophe vs α while keeping most of α’s noisy_adp edge (β−raw close to α−raw).
- If β becomes too QB-afraid, inspect `ev_by_future` on recommend / loss traces before tuning weights.
- Deterministic CPUs: treat mean Δ as a single-trajectory gap, not a win-rate claim.
