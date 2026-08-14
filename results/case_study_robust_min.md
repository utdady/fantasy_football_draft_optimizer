# β2-robust diagnostic (α vs min_f)

## Purpose

β2-robust diagnostic only — not an expected-value strategy. min_f over ADP/proj/VOR scenario two-pick EVs; no hardcoded player/position rules; no P(f) weights.

Pass bar: (1) R1 Chase→Daniels flip without hardcoding; (2) robust ≈ α on neighbor boards (not a paranoia cascade).

Futures: `adp_greedy, proj_greedy, vor`

## Verdict

- PASS: robust flips Chase→Daniels at R1 and agrees with α on all neighbor boards
- R1 flip pass: **True**
- neighbor agree: `['O20_after_Chase_proj18', 'O20_after_Daniels_adp18', 'O20_alpha_noisy_path']`
- neighbor disagree: `[]`
- paranoia_flag (≥2 neighbor disagreements): **False**

## R1_slot1_empty (overall #1, wait 18)

_Frozen proj-greedy failure: long wait, empty roster_

- candidates scored: **58**
- α pick: **Ja'Marr Chase** (WR) ev_adp=711.61 ev_min=641.37 worst=proj_greedy
- robust min pick: **Jayden Daniels** (QB) ev_adp=672.94 ev_min=672.94 worst=adp_greedy
- agree: **False**
- regret_α: `{'adp_greedy': 0.0, 'proj_greedy': 31.57, 'vor': 0.0}`
- regret_robust: `{'adp_greedy': 38.67, 'proj_greedy': 0.0, 'vor': 22.49}`

### Top by α (ADP future EV)

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 641.4 | proj_greedy |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 640.7 | proj_greedy |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 627.3 | proj_greedy |
| Christian McCaffrey | RB | 690.0 | 619.8 | 690.0 | 619.8 | proj_greedy |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 618.9 | proj_greedy |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 618.6 | proj_greedy |
| Justin Jefferson | WR | 687.5 | 617.2 | 687.5 | 617.2 | proj_greedy |
| De'Von Achane | RB | 679.1 | 608.9 | 679.1 | 608.9 | proj_greedy |

### Top by robust min

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 672.9 | adp_greedy |
| Josh Allen | QB | 669.2 | 669.2 | 685.4 | 669.2 | adp_greedy |
| Jalen Hurts | QB | 666.8 | 666.8 | 683.0 | 666.8 | adp_greedy |
| Lamar Jackson | QB | 665.1 | 665.1 | 681.3 | 665.1 | adp_greedy |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 641.4 | proj_greedy |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 640.7 | proj_greedy |
| Joe Burrow | QB | 631.8 | 631.8 | 648.0 | 631.8 | adp_greedy |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 627.3 | proj_greedy |

### Spotlight

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Jahmyr Gibbs | RB | 688.9 | 618.6 | 688.9 | 618.6 | proj_greedy |
| Bijan Robinson | RB | 711.0 | 640.7 | 711.0 | 640.7 | proj_greedy |
| Ja'Marr Chase | WR | 711.6 | 641.4 | 711.6 | 641.4 | proj_greedy |
| CeeDee Lamb | WR | 689.1 | 618.9 | 689.1 | 618.9 | proj_greedy |
| Saquon Barkley | RB | 697.6 | 627.3 | 697.6 | 627.3 | proj_greedy |
| Malik Nabers | WR | 672.9 | 603.2 | 672.9 | 603.2 | proj_greedy |
| Jayden Daniels | QB | 672.9 | 672.9 | 689.1 | 672.9 | adp_greedy |
| Justin Fields | QB | 600.7 | 600.7 | 616.9 | 600.7 | adp_greedy |

## O20_after_Chase_proj18 (overall #20, wait 0)

_Neighbor: after fragile R1 deferral realized; Fields still up_

- candidates scored: **60**
- α pick: **Malik Nabers** (WR) ev_adp=940.69 ev_min=940.69 worst=adp_greedy
- robust min pick: **Malik Nabers** (WR) ev_adp=940.69 ev_min=940.69 worst=adp_greedy
- agree: **True**
- regret_α: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`
- regret_robust: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`

### Top by α (ADP future EV)

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |
| Puka Nacua | WR | 940.0 | 940.0 | 940.0 | 940.0 | adp_greedy |
| Amon-Ra St. Brown | WR | 932.0 | 932.0 | 932.0 | 932.0 | adp_greedy |
| Nico Collins | WR | 930.5 | 930.5 | 930.5 | 930.5 | adp_greedy |
| Jonathan Taylor | RB | 930.1 | 930.1 | 930.1 | 930.1 | adp_greedy |
| Dak Prescott | QB | 927.2 | 927.2 | 927.2 | 927.2 | adp_greedy |
| Drake Maye | QB | 926.6 | 926.6 | 926.6 | 926.6 | adp_greedy |

### Top by robust min

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |
| Puka Nacua | WR | 940.0 | 940.0 | 940.0 | 940.0 | adp_greedy |
| Amon-Ra St. Brown | WR | 932.0 | 932.0 | 932.0 | 932.0 | adp_greedy |
| Nico Collins | WR | 930.5 | 930.5 | 930.5 | 930.5 | adp_greedy |
| Jonathan Taylor | RB | 930.1 | 930.1 | 930.1 | 930.1 | adp_greedy |
| Dak Prescott | QB | 927.2 | 927.2 | 927.2 | 927.2 | adp_greedy |
| Drake Maye | QB | 926.6 | 926.6 | 926.6 | 926.6 | adp_greedy |

### Spotlight

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Malik Nabers | WR | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |

## O20_after_Daniels_adp18 (overall #20, wait 0)

_Neighbor: secure-QB path under ADP-like CPUs (healthy deferrals?)_

- candidates scored: **64**
- α pick: **Nico Collins** (WR) ev_adp=962.07 ev_min=962.07 worst=adp_greedy
- robust min pick: **Nico Collins** (WR) ev_adp=962.07 ev_min=962.07 worst=adp_greedy
- agree: **True**
- regret_α: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`
- regret_robust: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`

### Top by α (ADP future EV)

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Malik Nabers | WR | 962.1 | 962.1 | 962.1 | 962.1 | adp_greedy |
| Nico Collins | WR | 962.1 | 962.1 | 962.1 | 962.1 | adp_greedy |
| Kyren Williams | RB | 957.0 | 957.0 | 957.0 | 957.0 | adp_greedy |
| Bucky Irving | RB | 956.4 | 956.4 | 956.4 | 956.4 | adp_greedy |
| Josh Jacobs | RB | 955.8 | 955.8 | 955.8 | 955.8 | adp_greedy |
| Chase Brown | RB | 954.2 | 954.2 | 954.2 | 954.2 | adp_greedy |
| A.J. Brown | WR | 948.6 | 948.6 | 948.6 | 948.6 | adp_greedy |
| Brian Thomas | WR | 943.0 | 943.0 | 943.0 | 943.0 | adp_greedy |

### Top by robust min

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Malik Nabers | WR | 962.1 | 962.1 | 962.1 | 962.1 | adp_greedy |
| Nico Collins | WR | 962.1 | 962.1 | 962.1 | 962.1 | adp_greedy |
| Kyren Williams | RB | 957.0 | 957.0 | 957.0 | 957.0 | adp_greedy |
| Bucky Irving | RB | 956.4 | 956.4 | 956.4 | 956.4 | adp_greedy |
| Josh Jacobs | RB | 955.8 | 955.8 | 955.8 | 955.8 | adp_greedy |
| Chase Brown | RB | 954.2 | 954.2 | 954.2 | 954.2 | adp_greedy |
| A.J. Brown | WR | 948.6 | 948.6 | 948.6 | 948.6 | adp_greedy |
| Brian Thomas | WR | 943.0 | 943.0 | 943.0 | 943.0 | adp_greedy |

### Spotlight

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Malik Nabers | WR | 962.1 | 962.1 | 962.1 | 962.1 | adp_greedy |
| Justin Fields | QB | 672.9 | 672.9 | 672.9 | 672.9 | adp_greedy |

## O20_alpha_noisy_path (overall #20, wait 0)

_Neighbor: α-driven board at R2 with wait 0 (back-to-back picks)_

- candidates scored: **63**
- α pick: **Malik Nabers** (WR) ev_adp=1012.96 ev_min=1012.96 worst=adp_greedy
- robust min pick: **Malik Nabers** (WR) ev_adp=1012.96 ev_min=1012.96 worst=adp_greedy
- agree: **True**
- regret_α: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`
- regret_robust: `{'adp_greedy': 0.0, 'proj_greedy': 0.0, 'vor': 0.0}`

### Top by α (ADP future EV)

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Jayden Daniels | QB | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Malik Nabers | WR | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Josh Allen | QB | 1009.2 | 1009.2 | 1009.2 | 1009.2 | adp_greedy |
| Jalen Hurts | QB | 1006.9 | 1006.9 | 1006.9 | 1006.9 | adp_greedy |
| Lamar Jackson | QB | 1005.2 | 1005.2 | 1005.2 | 1005.2 | adp_greedy |
| Nico Collins | WR | 1000.7 | 1000.7 | 1000.7 | 1000.7 | adp_greedy |
| Kyren Williams | RB | 995.7 | 995.7 | 995.7 | 995.7 | adp_greedy |
| Bucky Irving | RB | 995.1 | 995.1 | 995.1 | 995.1 | adp_greedy |

### Top by robust min

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Jayden Daniels | QB | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Malik Nabers | WR | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Josh Allen | QB | 1009.2 | 1009.2 | 1009.2 | 1009.2 | adp_greedy |
| Jalen Hurts | QB | 1006.9 | 1006.9 | 1006.9 | 1006.9 | adp_greedy |
| Lamar Jackson | QB | 1005.2 | 1005.2 | 1005.2 | 1005.2 | adp_greedy |
| Nico Collins | WR | 1000.7 | 1000.7 | 1000.7 | 1000.7 | adp_greedy |
| Kyren Williams | RB | 995.7 | 995.7 | 995.7 | 995.7 | adp_greedy |
| Bucky Irving | RB | 995.1 | 995.1 | 995.1 | 995.1 | adp_greedy |

### Spotlight

| player | pos | ADP | proj | VOR | min | worst |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Malik Nabers | WR | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Jayden Daniels | QB | 1013.0 | 1013.0 | 1013.0 | 1013.0 | adp_greedy |
| Justin Fields | QB | 940.7 | 940.7 | 940.7 | 940.7 | adp_greedy |

## Reading

- R1 flip + neighbor agreement → `min_f` behaves as a **targeted** correction for fragile long-wait deferrals, not a paranoia cascade on wait-0 boards.
- Note: an exploratory evaluation at overall #21 (wait 18 again) also preferred Daniels over α's WR — same long-wait fragility pattern, not a short-wait case.
- Clears the tiny pass bar for a slot-1 × 4-policy lean test; still **not** UI / not a `marginal_v2` replacement until that stress is reviewed.
- If later stress shows over-conservatism, diagnose before inventing P(f).
