# Risk / EV surface + Pareto frontier

## Purpose

Diagnostic only from three deterministic scenario EVs — not calibrated probabilities. No λ / CVaR / β3. UI stays marginal.

Success: articulate *why* a rational pick sits between Chase upside and Daniels insurance — not invent λ that happens to.

Futures: `adp_greedy, proj_greedy, vor`

## Verdict

- code: **A_frontier_exists**
- R1 Pareto size: **2** positions=`['QB', 'WR']`

- R1 Pareto spans skill (high mean/fragile) and elite QB (lower mean/high floor) — risk preference is a real decision variable.
- Chase: mean=688.2 floor=641.37 downside=46.83 max_regret=31.57 (proj_greedy).
- Daniels: mean=678.33 floor=672.94 downside=5.39 max_regret=38.67 (adp_greedy).
- Wait-0 board: scenario EVs coincide (no intervening picks) — risk surface collapses; confirms uncertainty is board-evolution, not player-value uncertainty.

- next: If frontier spans skill vs QB (A): risk-sensitive objective is justified. Also ask whether proj_greedy scenario is too extreme (B/C) before coding λ.

## R1_slot1_empty (overall #1, wait 18)

_Frozen long-wait failure board (18 picks)_

- scored: **58**
- α (max ADP EV): **Ja'Marr Chase**
- max mean EV: **Ja'Marr Chase**
- max floor: **Jayden Daniels**
- min max-regret: **Ja'Marr Chase**
- Pareto size: **2**

### Class summary

- `skill_RB_WR_TE` n=39: mean_of_means=615.07, mean_of_floors=568.52, mean_downside=46.55, mean_max_regret=104.42
- `QB` n=19: mean_of_means=617.42, mean_of_floors=612.03, mean_downside=5.39, mean_max_regret=99.58

### Pareto frontier

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 688.2 | 641.4 | 46.8 | 31.6 | proj_greedy | yes |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 678.3 | 672.9 | 5.4 | 38.7 | adp_greedy | yes |

### Top by mean EV

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 688.2 | 641.4 | 46.8 | 31.6 | proj_greedy | yes |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 687.5 | 640.7 | 46.8 | 32.2 | proj_greedy |  |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 678.3 | 672.9 | 5.4 | 38.7 | adp_greedy | yes |
| Josh Allen | QB | 669.2 | 669.2 | 685.4 | 674.6 | 669.2 | 5.4 | 42.4 | adp_greedy |  |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 674.2 | 627.3 | 46.8 | 45.6 | proj_greedy |  |
| Jalen Hurts | QB | 666.8 | 666.8 | 683.0 | 672.2 | 666.8 | 5.4 | 44.8 | adp_greedy |  |
| Lamar Jackson | QB | 665.1 | 665.1 | 681.3 | 670.5 | 665.1 | 5.4 | 46.5 | adp_greedy |  |
| Christian McCaffrey | RB | 690.0 | 619.8 | 690.0 | 666.6 | 619.8 | 46.8 | 53.2 | proj_greedy |  |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 665.7 | 618.9 | 46.8 | 54.1 | proj_greedy |  |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 665.5 | 618.6 | 46.8 | 54.3 | proj_greedy |  |
| Justin Jefferson | WR | 687.5 | 617.2 | 687.5 | 664.0 | 617.2 | 46.8 | 55.7 | proj_greedy |  |
| De'Von Achane | RB | 679.1 | 608.9 | 679.1 | 655.7 | 608.9 | 46.8 | 64.1 | proj_greedy |  |
| Ashton Jeanty | RB | 673.6 | 603.4 | 673.6 | 650.2 | 603.4 | 46.8 | 69.5 | proj_greedy |  |
| Malik Nabers | WR | 672.9 | 603.2 | 672.9 | 649.7 | 603.2 | 46.5 | 69.7 | proj_greedy |  |
| Puka Nacua | WR | 670.2 | 600.5 | 670.2 | 647.0 | 600.5 | 46.5 | 72.4 | proj_greedy |  |

### Top by floor

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 678.3 | 672.9 | 5.4 | 38.7 | adp_greedy | yes |
| Josh Allen | QB | 669.2 | 669.2 | 685.4 | 674.6 | 669.2 | 5.4 | 42.4 | adp_greedy |  |
| Jalen Hurts | QB | 666.8 | 666.8 | 683.0 | 672.2 | 666.8 | 5.4 | 44.8 | adp_greedy |  |
| Lamar Jackson | QB | 665.1 | 665.1 | 681.3 | 670.5 | 665.1 | 5.4 | 46.5 | adp_greedy |  |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 688.2 | 641.4 | 46.8 | 31.6 | proj_greedy | yes |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 687.5 | 640.7 | 46.8 | 32.2 | proj_greedy |  |
| Joe Burrow | QB | 631.8 | 631.8 | 648.0 | 637.2 | 631.8 | 5.4 | 79.8 | adp_greedy |  |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 674.2 | 627.3 | 46.8 | 45.6 | proj_greedy |  |
| Patrick Mahomes | QB | 626.3 | 626.3 | 642.5 | 631.7 | 626.3 | 5.4 | 85.3 | adp_greedy |  |
| Christian McCaffrey | RB | 690.0 | 619.8 | 690.0 | 666.6 | 619.8 | 46.8 | 53.2 | proj_greedy |  |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 665.7 | 618.9 | 46.8 | 54.1 | proj_greedy |  |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 665.5 | 618.6 | 46.8 | 54.3 | proj_greedy |  |
| Justin Jefferson | WR | 687.5 | 617.2 | 687.5 | 664.0 | 617.2 | 46.8 | 55.7 | proj_greedy |  |
| Baker Mayfield | QB | 612.3 | 612.3 | 628.5 | 617.7 | 612.3 | 5.4 | 99.3 | adp_greedy |  |
| De'Von Achane | RB | 679.1 | 608.9 | 679.1 | 655.7 | 608.9 | 46.8 | 64.1 | proj_greedy |  |

### Lowest max regret

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 688.2 | 641.4 | 46.8 | 31.6 | proj_greedy | yes |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 687.5 | 640.7 | 46.8 | 32.2 | proj_greedy |  |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 678.3 | 672.9 | 5.4 | 38.7 | adp_greedy | yes |
| Josh Allen | QB | 669.2 | 669.2 | 685.4 | 674.6 | 669.2 | 5.4 | 42.4 | adp_greedy |  |
| Jalen Hurts | QB | 666.8 | 666.8 | 683.0 | 672.2 | 666.8 | 5.4 | 44.8 | adp_greedy |  |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 674.2 | 627.3 | 46.8 | 45.6 | proj_greedy |  |
| Lamar Jackson | QB | 665.1 | 665.1 | 681.3 | 670.5 | 665.1 | 5.4 | 46.5 | adp_greedy |  |
| Christian McCaffrey | RB | 690.0 | 619.8 | 690.0 | 666.6 | 619.8 | 46.8 | 53.2 | proj_greedy |  |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 665.7 | 618.9 | 46.8 | 54.1 | proj_greedy |  |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 665.5 | 618.6 | 46.8 | 54.3 | proj_greedy |  |
| Justin Jefferson | WR | 687.5 | 617.2 | 687.5 | 664.0 | 617.2 | 46.8 | 55.7 | proj_greedy |  |
| De'Von Achane | RB | 679.1 | 608.9 | 679.1 | 655.7 | 608.9 | 46.8 | 64.1 | proj_greedy |  |
| Ashton Jeanty | RB | 673.6 | 603.4 | 673.6 | 650.2 | 603.4 | 46.8 | 69.5 | proj_greedy |  |
| Malik Nabers | WR | 672.9 | 603.2 | 672.9 | 649.7 | 603.2 | 46.5 | 69.7 | proj_greedy |  |
| Puka Nacua | WR | 670.2 | 600.5 | 670.2 | 647.0 | 600.5 | 46.5 | 72.4 | proj_greedy |  |

### Spotlight

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 665.5 | 618.6 | 46.8 | 54.3 | proj_greedy |  |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 687.5 | 640.7 | 46.8 | 32.2 | proj_greedy |  |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 688.2 | 641.4 | 46.8 | 31.6 | proj_greedy | yes |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 665.7 | 618.9 | 46.8 | 54.1 | proj_greedy |  |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 674.2 | 627.3 | 46.8 | 45.6 | proj_greedy |  |
| Josh Allen | QB | 669.2 | 669.2 | 685.4 | 674.6 | 669.2 | 5.4 | 42.4 | adp_greedy |  |
| Malik Nabers | WR | 672.9 | 603.2 | 672.9 | 649.7 | 603.2 | 46.5 | 69.7 | proj_greedy |  |
| Lamar Jackson | QB | 665.1 | 665.1 | 681.3 | 670.5 | 665.1 | 5.4 | 46.5 | adp_greedy |  |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 678.3 | 672.9 | 5.4 | 38.7 | adp_greedy | yes |
| Jalen Hurts | QB | 666.8 | 666.8 | 683.0 | 672.2 | 666.8 | 5.4 | 44.8 | adp_greedy |  |

## O20_after_Chase_proj18 (overall #20, wait 0)

_Wait-0 neighbor contrast (futures collapse when n_cpu=0)_

- scored: **60**
- α (max ADP EV): **Malik Nabers**
- max mean EV: **Justin Fields**
- max floor: **Justin Fields**
- min max-regret: **Justin Fields**
- Pareto size: **2**

### Class summary

- `skill_RB_WR_TE` n=44: mean_of_means=882.86, mean_of_floors=882.86, mean_downside=0.0, mean_max_regret=57.83
- `QB` n=16: mean_of_means=915.71, mean_of_floors=915.71, mean_downside=0.0, mean_max_regret=24.98

### Pareto frontier

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |

### Top by mean EV

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Puka Nacua | WR | 940.0 | 940.0 | 940.0 | 940.0 | 940.0 | 0.0 | 0.7 | adp_greedy |  |
| Amon-Ra St. Brown | WR | 932.0 | 932.0 | 932.0 | 932.0 | 932.0 | 0.0 | 8.7 | adp_greedy |  |
| Nico Collins | WR | 930.5 | 930.5 | 930.5 | 930.5 | 930.5 | 0.0 | 10.2 | adp_greedy |  |
| Jonathan Taylor | RB | 930.1 | 930.1 | 930.1 | 930.1 | 930.1 | 0.0 | 10.6 | adp_greedy |  |
| Dak Prescott | QB | 927.2 | 927.2 | 927.2 | 927.2 | 927.2 | 0.0 | 13.5 | adp_greedy |  |
| Drake Maye | QB | 926.6 | 926.6 | 926.6 | 926.6 | 926.6 | 0.0 | 14.1 | adp_greedy |  |
| Justin Herbert | QB | 925.9 | 925.9 | 925.9 | 925.9 | 925.9 | 0.0 | 14.8 | adp_greedy |  |
| Kyren Williams | RB | 925.4 | 925.4 | 925.4 | 925.4 | 925.4 | 0.0 | 15.3 | adp_greedy |  |
| Bucky Irving | RB | 924.8 | 924.8 | 924.8 | 924.8 | 924.8 | 0.0 | 15.8 | adp_greedy |  |
| Josh Jacobs | RB | 924.2 | 924.2 | 924.2 | 924.2 | 924.2 | 0.0 | 16.4 | adp_greedy |  |
| J.J. McCarthy | QB | 923.9 | 923.9 | 923.9 | 923.9 | 923.9 | 0.0 | 16.8 | adp_greedy |  |
| Derrick Henry | RB | 923.1 | 923.1 | 923.1 | 923.1 | 923.1 | 0.0 | 17.6 | adp_greedy |  |
| Chase Brown | RB | 922.6 | 922.6 | 922.6 | 922.6 | 922.6 | 0.0 | 18.1 | adp_greedy |  |

### Top by floor

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Puka Nacua | WR | 940.0 | 940.0 | 940.0 | 940.0 | 940.0 | 0.0 | 0.7 | adp_greedy |  |
| Amon-Ra St. Brown | WR | 932.0 | 932.0 | 932.0 | 932.0 | 932.0 | 0.0 | 8.7 | adp_greedy |  |
| Nico Collins | WR | 930.5 | 930.5 | 930.5 | 930.5 | 930.5 | 0.0 | 10.2 | adp_greedy |  |
| Jonathan Taylor | RB | 930.1 | 930.1 | 930.1 | 930.1 | 930.1 | 0.0 | 10.6 | adp_greedy |  |
| Dak Prescott | QB | 927.2 | 927.2 | 927.2 | 927.2 | 927.2 | 0.0 | 13.5 | adp_greedy |  |
| Drake Maye | QB | 926.6 | 926.6 | 926.6 | 926.6 | 926.6 | 0.0 | 14.1 | adp_greedy |  |
| Justin Herbert | QB | 925.9 | 925.9 | 925.9 | 925.9 | 925.9 | 0.0 | 14.8 | adp_greedy |  |
| Kyren Williams | RB | 925.4 | 925.4 | 925.4 | 925.4 | 925.4 | 0.0 | 15.3 | adp_greedy |  |
| Bucky Irving | RB | 924.8 | 924.8 | 924.8 | 924.8 | 924.8 | 0.0 | 15.8 | adp_greedy |  |
| Josh Jacobs | RB | 924.2 | 924.2 | 924.2 | 924.2 | 924.2 | 0.0 | 16.4 | adp_greedy |  |
| J.J. McCarthy | QB | 923.9 | 923.9 | 923.9 | 923.9 | 923.9 | 0.0 | 16.8 | adp_greedy |  |
| Derrick Henry | RB | 923.1 | 923.1 | 923.1 | 923.1 | 923.1 | 0.0 | 17.6 | adp_greedy |  |
| Chase Brown | RB | 922.6 | 922.6 | 922.6 | 922.6 | 922.6 | 0.0 | 18.1 | adp_greedy |  |

### Lowest max regret

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy | yes |
| Puka Nacua | WR | 940.0 | 940.0 | 940.0 | 940.0 | 940.0 | 0.0 | 0.7 | adp_greedy |  |
| Amon-Ra St. Brown | WR | 932.0 | 932.0 | 932.0 | 932.0 | 932.0 | 0.0 | 8.7 | adp_greedy |  |
| Nico Collins | WR | 930.5 | 930.5 | 930.5 | 930.5 | 930.5 | 0.0 | 10.2 | adp_greedy |  |
| Jonathan Taylor | RB | 930.1 | 930.1 | 930.1 | 930.1 | 930.1 | 0.0 | 10.6 | adp_greedy |  |
| Dak Prescott | QB | 927.2 | 927.2 | 927.2 | 927.2 | 927.2 | 0.0 | 13.5 | adp_greedy |  |
| Drake Maye | QB | 926.6 | 926.6 | 926.6 | 926.6 | 926.6 | 0.0 | 14.1 | adp_greedy |  |
| Justin Herbert | QB | 925.9 | 925.9 | 925.9 | 925.9 | 925.9 | 0.0 | 14.8 | adp_greedy |  |
| Kyren Williams | RB | 925.4 | 925.4 | 925.4 | 925.4 | 925.4 | 0.0 | 15.3 | adp_greedy |  |
| Bucky Irving | RB | 924.8 | 924.8 | 924.8 | 924.8 | 924.8 | 0.0 | 15.8 | adp_greedy |  |
| Josh Jacobs | RB | 924.2 | 924.2 | 924.2 | 924.2 | 924.2 | 0.0 | 16.4 | adp_greedy |  |
| J.J. McCarthy | QB | 923.9 | 923.9 | 923.9 | 923.9 | 923.9 | 0.0 | 16.8 | adp_greedy |  |
| Derrick Henry | RB | 923.1 | 923.1 | 923.1 | 923.1 | 923.1 | 0.0 | 17.6 | adp_greedy |  |
| Chase Brown | RB | 922.6 | 922.6 | 922.6 | 922.6 | 922.6 | 0.0 | 18.1 | adp_greedy |  |

### Spotlight

| player | pos | ADP | proj | VOR | mean | floor | downside | max regret | worst regret f | Pareto? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | 940.7 | 0.0 | 0.0 | adp_greedy |  |

## Reading

- **A (objective):** frontier has both high-mean skill and high-floor QB → risk preference is the missing dial (not another ranking hack).
- **B (scenario set):** if only proj creates the skill cliff, ask whether proj_greedy is too extreme before coding λ.
- **C (both):** most likely — need risk-sensitive objective *and* realistic board-evolution uncertainty.
- Wait-0 boards collapsing scenarios confirms the uncertainty is **state transition** (who survives), not player valuation.
- Do **not** implement Score = E[EV] − λR yet; freeze this surface first.
