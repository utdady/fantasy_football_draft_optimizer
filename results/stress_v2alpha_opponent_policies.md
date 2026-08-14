# V2-alpha opponent-policy stress

## Setup

- n_sims per cell: **20**
- slots: `[1, 5, 10]`
- seed: `0`
- strategies: `marginal` vs `marginal_v2` (paired)
- V2 lookahead: **adp_greedy (frozen)** (frozen)
- opponent policies: `noisy_adp, adp_greedy, proj_greedy, vor`

## Matrix (V2 − raw)

| opponent | slot | raw mean | v2 mean | v2−raw | v2>raw | n_losses |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| noisy_adp | 1 | 2428.9 | 2500.2 | +71.3 | 100% | 0 |
| noisy_adp | 5 | 2443.5 | 2506.4 | +62.9 | 95% | 1 |
| noisy_adp | 10 | 2447.9 | 2484.2 | +36.3 | 85% | 3 |
| adp_greedy | 1 | 2406.4 | 2482.7 | +76.3 | 100% | 0 |
| adp_greedy | 5 | 2426.7 | 2469.2 | +42.5 | 100% | 0 |
| adp_greedy | 10 | 2463.6 | 2495.4 | +31.8 | 100% | 0 |
| proj_greedy | 1 | 2330.7 | 2313.7 | -17.0 | 0% | 20 |
| proj_greedy | 5 | 2340.3 | 2307.5 | -32.8 | 0% | 20 |
| proj_greedy | 10 | 2328.7 | 2324.4 | -4.2 | 0% | 20 |
| vor | 1 | 2030.6 | 2072.0 | +41.4 | 100% | 0 |
| vor | 5 | 2030.6 | 2055.4 | +24.8 | 100% | 0 |
| vor | 10 | 2022.6 | 2030.6 | +8.0 | 100% | 0 |

## Loss diagnostics (sample)

### noisy_adp · slot 5 (1 losses)

- sim 11 seed=11099: Δ=-10.2 (raw 2463.6 vs v2 2453.4)
  - R1 raw=Jayden Daniels (QB); v2=Bijan Robinson (RB)
  - q FAILED: took Kyren Williams expecting Jayden Daniels (QB) after wait 8

### noisy_adp · slot 10 (3 losses)

- sim 1 seed=1009: Δ=-16.4 (raw 2442.9 vs v2 2426.5)
  - R1 raw=Jayden Daniels (QB); v2=CeeDee Lamb (WR)
  - no early q-survival failures recorded
- sim 5 seed=5045: Δ=-6.7 (raw 2443.2 vs v2 2436.6)
  - R1 raw=Jayden Daniels (QB); v2=Saquon Barkley (RB)
  - no early q-survival failures recorded
- sim 6 seed=6054: Δ=-11.4 (raw 2463.6 vs v2 2452.2)
  - R1 raw=Jayden Daniels (QB); v2=Saquon Barkley (RB)
  - no early q-survival failures recorded

### proj_greedy · slot 1 (20 losses)

- sim 0 seed=0: Δ=-17.0 (raw 2330.7 vs v2 2313.7)
  - R1 raw=Jayden Daniels (QB); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18
- sim 1 seed=1009: Δ=-17.0 (raw 2330.7 vs v2 2313.7)
  - R1 raw=Jayden Daniels (QB); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18
- sim 2 seed=2018: Δ=-17.0 (raw 2330.7 vs v2 2313.7)
  - R1 raw=Jayden Daniels (QB); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Jayden Daniels (QB) after wait 18
  - q FAILED: took Puka Nacua expecting Justin Fields (QB) after wait 18
  - q FAILED: took James Cook expecting Matthew Stafford (QB) after wait 18

### proj_greedy · slot 5 (20 losses)

- sim 0 seed=0: Δ=-32.8 (raw 2340.3 vs v2 2307.5)
  - R1 raw=Ja'Marr Chase (WR); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Joe Burrow (QB) after wait 10
  - q FAILED: took Ashton Jeanty expecting Kyler Murray (QB) after wait 8
  - q FAILED: took Jonathan Taylor expecting Dak Prescott (QB) after wait 10
  - q FAILED: took Jeremiyah Love expecting Caleb Williams (QB) after wait 8
- sim 1 seed=1009: Δ=-32.8 (raw 2340.3 vs v2 2307.5)
  - R1 raw=Ja'Marr Chase (WR); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Joe Burrow (QB) after wait 10
  - q FAILED: took Ashton Jeanty expecting Kyler Murray (QB) after wait 8
  - q FAILED: took Jonathan Taylor expecting Dak Prescott (QB) after wait 10
  - q FAILED: took Jeremiyah Love expecting Caleb Williams (QB) after wait 8
- sim 2 seed=2018: Δ=-32.8 (raw 2340.3 vs v2 2307.5)
  - R1 raw=Ja'Marr Chase (WR); v2=Ja'Marr Chase (WR)
  - q FAILED: took Ja'Marr Chase expecting Joe Burrow (QB) after wait 10
  - q FAILED: took Ashton Jeanty expecting Kyler Murray (QB) after wait 8
  - q FAILED: took Jonathan Taylor expecting Dak Prescott (QB) after wait 10
  - q FAILED: took Jeremiyah Love expecting Caleb Williams (QB) after wait 8

### proj_greedy · slot 10 (20 losses)

- sim 0 seed=0: Δ=-4.2 (raw 2328.7 vs v2 2324.4)
  - R1 raw=Christian McCaffrey (RB); v2=Christian McCaffrey (RB)
  - q FAILED: took CeeDee Lamb expecting Baker Mayfield (QB) after wait 18
  - q FAILED: took Bucky Irving expecting J.J. McCarthy (QB) after wait 18
  - q FAILED: took Omarion Hampton expecting Geno Smith (QB) after wait 18
- sim 1 seed=1009: Δ=-4.2 (raw 2328.7 vs v2 2324.4)
  - R1 raw=Christian McCaffrey (RB); v2=Christian McCaffrey (RB)
  - q FAILED: took CeeDee Lamb expecting Baker Mayfield (QB) after wait 18
  - q FAILED: took Bucky Irving expecting J.J. McCarthy (QB) after wait 18
  - q FAILED: took Omarion Hampton expecting Geno Smith (QB) after wait 18
- sim 2 seed=2018: Δ=-4.2 (raw 2328.7 vs v2 2324.4)
  - R1 raw=Christian McCaffrey (RB); v2=Christian McCaffrey (RB)
  - q FAILED: took CeeDee Lamb expecting Baker Mayfield (QB) after wait 18
  - q FAILED: took Bucky Irving expecting J.J. McCarthy (QB) after wait 18
  - q FAILED: took Omarion Hampton expecting Geno Smith (QB) after wait 18

## Reading

- If V2 stays ahead under proj_greedy / vor opponents, the opportunity idea generalizes beyond ADP-like CPUs.
- If the edge collapses only for some policies, V2-β should mix futures rather than only sample more ADP paths.
