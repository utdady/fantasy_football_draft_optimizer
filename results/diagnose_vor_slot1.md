# VOR decision-trace diagnostic

## Setup

- n_sims: **10** (early rounds only)
- slot: **1**
- rounds traced: **1–3**
- seed: `0`
- preset: `league_default`
- strategy picks: `marginal_vor`
- CPU: noisy ADP (paired pick RNG)

## Headline: RB#N vs WR#N at pick 1 (sim 0)

- RB#29 = **207.8296567** (`Austin Ekeler`)
- WR#29 = **221.36233553** (`George Pickens`)
- RB#N − WR#N = **-13.5**
- Best RB VOR − best WR VOR at pick 1 = **+12.9**

Interpretation: RB replacement is **lower** than WR at the same N → elite RB VOR is inflated by a steeper ESPN RB cliff (real scarcity signal and/or projection artifact), not by unequal FLEX_SHARE ranks.

## Aggregate best-pos VOR by round

| round | mean best RB VOR | mean best WR VOR | mean best QB VOR | mean RB−WR VOR gap |
| --- | ---: | ---: | ---: | ---: |
| 1 | 131.5 | 118.7 | 69.7 | +12.9 |
| 2 | 141.4 | 93.9 | 70.2 | +47.5 |
| 3 | 139.1 | 93.9 | 70.2 | +45.2 |

## Per-sim traces (R1–R3)

### Sim 0 (seed=0)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=159.8 (Kaleb Johnson); WR#29=203.3 (Matthew Golden); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 203.32310366 (diff -43.5); best RB−WR VOR gap +26.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 159.8 | Kaleb Johnson | 124.2 | 284.1 | 124.2 |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Jeremiyah Love | RB | 278.8 | 29 | 159.8 | Kaleb Johnson | 119.0 | 278.8 | 119.0 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Omarion Hampton | RB | 259.4 | 29 | 159.8 | Kaleb Johnson | 99.6 | 259.4 | 99.6 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=139.3 (Cam Skattebo); WR#29=203.3 (Matthew Golden); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 203.32310366 (diff -64.0); best RB−WR VOR gap +46.1

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Josh Jacobs | RB | 282.9 | 29 | 139.3 | Cam Skattebo | 143.5 | 282.9 | 143.5 |
| Jeremiyah Love | RB | 278.8 | 29 | 139.3 | Cam Skattebo | 139.5 | 278.8 | 139.5 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Omarion Hampton | RB | 259.4 | 29 | 139.3 | Cam Skattebo | 120.1 | 259.4 | 120.1 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

### Sim 1 (seed=1009)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=299.3 (Justin Fields); RB#29=159.8 (Kaleb Johnson); WR#29=203.3 (Matthew Golden); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 203.32310366 (diff -43.5); best RB−WR VOR gap +26.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 159.8 | Kaleb Johnson | 124.2 | 284.1 | 124.2 |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Chase Brown | RB | 281.2 | 29 | 159.8 | Kaleb Johnson | 121.4 | 281.2 | 121.4 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Omarion Hampton | RB | 259.4 | 29 | 159.8 | Kaleb Johnson | 99.6 | 259.4 | 99.6 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=299.3 (Justin Fields); RB#29=139.3 (Cam Skattebo); WR#29=203.3 (Matthew Golden); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 203.32310366 (diff -64.0); best RB−WR VOR gap +46.1

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Josh Jacobs | RB | 282.9 | 29 | 139.3 | Cam Skattebo | 143.5 | 282.9 | 143.5 |
| Chase Brown | RB | 281.2 | 29 | 139.3 | Cam Skattebo | 141.9 | 281.2 | 141.9 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Omarion Hampton | RB | 259.4 | 29 | 139.3 | Cam Skattebo | 120.1 | 259.4 | 120.1 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

### Sim 2 (seed=2018)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Saquon Barkley** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=163.8 (Jacory Croskey-Merritt); WR#29=203.1 (Deebo Samuel); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 163.7683341 vs 203.13788145 (diff -39.4); best RB−WR VOR gap +89.7

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Saquon Barkley | RB | 326.0 | 29 | 163.8 | Jacory Croskey-Merritt | 162.2 | 326.0 | 162.2 |
| Kyren Williams | RB | 284.1 | 29 | 163.8 | Jacory Croskey-Merritt | 120.3 | 284.1 | 120.3 |
| Bucky Irving | RB | 283.5 | 29 | 163.8 | Jacory Croskey-Merritt | 119.7 | 283.5 | 119.7 |
| Josh Jacobs | RB | 282.9 | 29 | 163.8 | Jacory Croskey-Merritt | 119.1 | 282.9 | 119.1 |
| Chase Brown | RB | 281.2 | 29 | 163.8 | Jacory Croskey-Merritt | 117.5 | 281.2 | 117.5 |
| Alvin Kamara | RB | 266.7 | 29 | 163.8 | Jacory Croskey-Merritt | 102.9 | 266.7 | 102.9 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 21 / Round 3** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=159.8 (Kaleb Johnson); WR#29=203.1 (Deebo Samuel); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 203.13788145 (diff -43.3); best RB−WR VOR gap +51.7

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 159.8 | Kaleb Johnson | 124.2 | 284.1 | 124.2 |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Chase Brown | RB | 281.2 | 29 | 159.8 | Kaleb Johnson | 121.4 | 281.2 | 121.4 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Omarion Hampton | RB | 259.4 | 29 | 159.8 | Kaleb Johnson | 99.6 | 259.4 | 99.6 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

### Sim 3 (seed=3027)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=299.3 (Justin Fields); RB#29=139.3 (Cam Skattebo); WR#29=209.8 (Chris Olave); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 209.82328203 (diff -70.5); best RB−WR VOR gap +53.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 139.3 | Cam Skattebo | 144.7 | 284.1 | 144.7 |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Chase Brown | RB | 281.2 | 29 | 139.3 | Cam Skattebo | 141.9 | 281.2 | 141.9 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Omarion Hampton | RB | 259.4 | 29 | 139.3 | Cam Skattebo | 120.1 | 259.4 | 120.1 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=299.3 (Justin Fields); RB#29=137.0 (Zach Charbonnet); WR#29=209.8 (Chris Olave); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 137.02487636 vs 209.82328203 (diff -72.8); best RB−WR VOR gap +54.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 137.0 | Zach Charbonnet | 146.4 | 283.5 | 146.4 |
| Chase Brown | RB | 281.2 | 29 | 137.0 | Zach Charbonnet | 144.2 | 281.2 | 144.2 |
| Alvin Kamara | RB | 266.7 | 29 | 137.0 | Zach Charbonnet | 129.7 | 266.7 | 129.7 |
| Omarion Hampton | RB | 259.4 | 29 | 137.0 | Zach Charbonnet | 122.4 | 259.4 | 122.4 |
| Chuba Hubbard | RB | 258.6 | 29 | 137.0 | Zach Charbonnet | 121.5 | 258.6 | 121.5 |
| Jaylen Warren | RB | 250.2 | 29 | 137.0 | Zach Charbonnet | 113.2 | 250.2 | 113.2 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| Kenneth Walker | RB | 238.8 | 29 | 137.0 | Zach Charbonnet | 101.8 | 238.8 | 101.8 |

### Sim 4 (seed=4036)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=139.3 (Cam Skattebo); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 209.82328203 (diff -70.5); best RB−WR VOR gap +53.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 139.3 | Cam Skattebo | 144.7 | 284.1 | 144.7 |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Derrick Henry | RB | 281.7 | 29 | 139.3 | Cam Skattebo | 142.4 | 281.7 | 142.4 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Omarion Hampton | RB | 259.4 | 29 | 139.3 | Cam Skattebo | 120.1 | 259.4 | 120.1 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=137.0 (Zach Charbonnet); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 137.02487636 vs 209.82328203 (diff -72.8); best RB−WR VOR gap +54.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 137.0 | Zach Charbonnet | 146.4 | 283.5 | 146.4 |
| Derrick Henry | RB | 281.7 | 29 | 137.0 | Zach Charbonnet | 144.7 | 281.7 | 144.7 |
| Alvin Kamara | RB | 266.7 | 29 | 137.0 | Zach Charbonnet | 129.7 | 266.7 | 129.7 |
| Omarion Hampton | RB | 259.4 | 29 | 137.0 | Zach Charbonnet | 122.4 | 259.4 | 122.4 |
| Chuba Hubbard | RB | 258.6 | 29 | 137.0 | Zach Charbonnet | 121.5 | 258.6 | 121.5 |
| Jaylen Warren | RB | 250.2 | 29 | 137.0 | Zach Charbonnet | 113.2 | 250.2 | 113.2 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Kenneth Walker | RB | 238.8 | 29 | 137.0 | Zach Charbonnet | 101.8 | 238.8 | 101.8 |

### Sim 5 (seed=5045)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Ashton Jeanty** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=163.8 (Jacory Croskey-Merritt); WR#29=203.1 (Deebo Samuel); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 163.7683341 vs 203.13788145 (diff -39.4); best RB−WR VOR gap +40.1

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Ashton Jeanty | RB | 302.1 | 29 | 163.8 | Jacory Croskey-Merritt | 138.3 | 302.1 | 138.3 |
| Kyren Williams | RB | 284.1 | 29 | 163.8 | Jacory Croskey-Merritt | 120.3 | 284.1 | 120.3 |
| Bucky Irving | RB | 283.5 | 29 | 163.8 | Jacory Croskey-Merritt | 119.7 | 283.5 | 119.7 |
| Josh Jacobs | RB | 282.9 | 29 | 163.8 | Jacory Croskey-Merritt | 119.1 | 282.9 | 119.1 |
| Derrick Henry | RB | 281.7 | 29 | 163.8 | Jacory Croskey-Merritt | 118.0 | 281.7 | 118.0 |
| Chase Brown | RB | 281.2 | 29 | 163.8 | Jacory Croskey-Merritt | 117.5 | 281.2 | 117.5 |
| Alvin Kamara | RB | 266.7 | 29 | 163.8 | Jacory Croskey-Merritt | 102.9 | 266.7 | 102.9 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |

**Pick 21 / Round 3** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=159.8 (Kaleb Johnson); WR#29=203.1 (Deebo Samuel); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 203.13788145 (diff -43.3); best RB−WR VOR gap +26.0

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 159.8 | Kaleb Johnson | 124.2 | 284.1 | 124.2 |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Derrick Henry | RB | 281.7 | 29 | 159.8 | Kaleb Johnson | 121.9 | 281.7 | 121.9 |
| Chase Brown | RB | 281.2 | 29 | 159.8 | Kaleb Johnson | 121.4 | 281.2 | 121.4 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |
| Chuba Hubbard | RB | 258.6 | 29 | 159.8 | Kaleb Johnson | 98.7 | 258.6 | 98.7 |

### Sim 6 (seed=6054)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Saquon Barkley** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=159.8 (Kaleb Johnson); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 209.82328203 (diff -50.0); best RB−WR VOR gap +74.7

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Saquon Barkley | RB | 326.0 | 29 | 159.8 | Kaleb Johnson | 166.2 | 326.0 | 166.2 |
| Kyren Williams | RB | 284.1 | 29 | 159.8 | Kaleb Johnson | 124.2 | 284.1 | 124.2 |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Chase Brown | RB | 281.2 | 29 | 159.8 | Kaleb Johnson | 121.4 | 281.2 | 121.4 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Chuba Hubbard | RB | 258.6 | 29 | 159.8 | Kaleb Johnson | 98.7 | 258.6 | 98.7 |

**Pick 21 / Round 3** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=139.3 (Cam Skattebo); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 209.82328203 (diff -70.5); best RB−WR VOR gap +53.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 139.3 | Cam Skattebo | 144.7 | 284.1 | 144.7 |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Josh Jacobs | RB | 282.9 | 29 | 139.3 | Cam Skattebo | 143.5 | 282.9 | 143.5 |
| Chase Brown | RB | 281.2 | 29 | 139.3 | Cam Skattebo | 141.9 | 281.2 | 141.9 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

### Sim 7 (seed=7063)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=163.8 (Jacory Croskey-Merritt); WR#29=203.1 (Deebo Samuel); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 163.7683341 vs 203.13788145 (diff -39.4); best RB−WR VOR gap +22.1

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 163.8 | Jacory Croskey-Merritt | 120.3 | 284.1 | 120.3 |
| Bucky Irving | RB | 283.5 | 29 | 163.8 | Jacory Croskey-Merritt | 119.7 | 283.5 | 119.7 |
| Josh Jacobs | RB | 282.9 | 29 | 163.8 | Jacory Croskey-Merritt | 119.1 | 282.9 | 119.1 |
| Derrick Henry | RB | 281.7 | 29 | 163.8 | Jacory Croskey-Merritt | 118.0 | 281.7 | 118.0 |
| Chase Brown | RB | 281.2 | 29 | 163.8 | Jacory Croskey-Merritt | 117.5 | 281.2 | 117.5 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Alvin Kamara | RB | 266.7 | 29 | 163.8 | Jacory Croskey-Merritt | 102.9 | 266.7 | 102.9 |
| Malik Nabers | WR | 301.4 | 29 | 203.1 | Deebo Samuel | 98.2 | 301.4 | 98.2 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=159.8 (Kaleb Johnson); WR#29=203.1 (Deebo Samuel); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 159.80919525 vs 203.13788145 (diff -43.3); best RB−WR VOR gap +25.4

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 159.8 | Kaleb Johnson | 123.7 | 283.5 | 123.7 |
| Josh Jacobs | RB | 282.9 | 29 | 159.8 | Kaleb Johnson | 123.1 | 282.9 | 123.1 |
| Derrick Henry | RB | 281.7 | 29 | 159.8 | Kaleb Johnson | 121.9 | 281.7 | 121.9 |
| Chase Brown | RB | 281.2 | 29 | 159.8 | Kaleb Johnson | 121.4 | 281.2 | 121.4 |
| Alvin Kamara | RB | 266.7 | 29 | 159.8 | Kaleb Johnson | 106.9 | 266.7 | 106.9 |
| Brock Bowers | TE | 262.2 | 12 | 156.9 | Dallas Goedert | 105.3 | 262.2 | 105.3 |
| Omarion Hampton | RB | 259.4 | 29 | 159.8 | Kaleb Johnson | 99.6 | 259.4 | 99.6 |
| Chuba Hubbard | RB | 258.6 | 29 | 159.8 | Kaleb Johnson | 98.7 | 258.6 | 98.7 |

### Sim 8 (seed=8072)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=139.3 (Cam Skattebo); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 209.82328203 (diff -70.5); best RB−WR VOR gap +53.2

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 139.3 | Cam Skattebo | 144.7 | 284.1 | 144.7 |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Derrick Henry | RB | 281.7 | 29 | 139.3 | Cam Skattebo | 142.4 | 281.7 | 142.4 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Omarion Hampton | RB | 259.4 | 29 | 139.3 | Cam Skattebo | 120.1 | 259.4 | 120.1 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |
| Kenneth Walker | RB | 238.8 | 29 | 139.3 | Cam Skattebo | 99.4 | 238.8 | 99.4 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=137.0 (Zach Charbonnet); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 137.02487636 vs 209.82328203 (diff -72.8); best RB−WR VOR gap +54.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 137.0 | Zach Charbonnet | 146.4 | 283.5 | 146.4 |
| Derrick Henry | RB | 281.7 | 29 | 137.0 | Zach Charbonnet | 144.7 | 281.7 | 144.7 |
| Alvin Kamara | RB | 266.7 | 29 | 137.0 | Zach Charbonnet | 129.7 | 266.7 | 129.7 |
| Omarion Hampton | RB | 259.4 | 29 | 137.0 | Zach Charbonnet | 122.4 | 259.4 | 122.4 |
| Chuba Hubbard | RB | 258.6 | 29 | 137.0 | Zach Charbonnet | 121.5 | 258.6 | 121.5 |
| Jaylen Warren | RB | 250.2 | 29 | 137.0 | Zach Charbonnet | 113.2 | 250.2 | 113.2 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |
| Kenneth Walker | RB | 238.8 | 29 | 137.0 | Zach Charbonnet | 101.8 | 238.8 | 101.8 |

### Sim 9 (seed=9081)

**Pick 1 / Round 1** → would take **Bijan Robinson** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=207.8 (Austin Ekeler); WR#29=221.4 (George Pickens); TE#12=160.0 (Tucker Kraft); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 207.8296567 vs 221.36233553 (diff -13.5); best RB−WR VOR gap +12.9

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bijan Robinson | RB | 339.4 | 29 | 207.8 | Austin Ekeler | 131.5 | 339.4 | 131.5 |
| Ja'Marr Chase | WR | 340.0 | 29 | 221.4 | George Pickens | 118.7 | 340.0 | 118.7 |
| Saquon Barkley | RB | 326.0 | 29 | 207.8 | Austin Ekeler | 118.2 | 326.0 | 118.2 |
| Christian McCaffrey | RB | 318.4 | 29 | 207.8 | Austin Ekeler | 110.6 | 318.4 | 110.6 |
| Jahmyr Gibbs | RB | 317.3 | 29 | 207.8 | Austin Ekeler | 109.5 | 317.3 | 109.5 |
| Brock Bowers | TE | 262.2 | 12 | 160.0 | Tucker Kraft | 102.2 | 262.2 | 102.2 |
| De'Von Achane | RB | 307.5 | 29 | 207.8 | Austin Ekeler | 99.7 | 307.5 | 99.7 |
| Trey McBride | TE | 259.2 | 12 | 160.0 | Tucker Kraft | 99.2 | 259.2 | 99.2 |

**Pick 20 / Round 2** → would take **Kyren Williams** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=139.3 (Cam Skattebo); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 139.3476305 vs 209.82328203 (diff -70.5); best RB−WR VOR gap +37.0

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Kyren Williams | RB | 284.1 | 29 | 139.3 | Cam Skattebo | 144.7 | 284.1 | 144.7 |
| Bucky Irving | RB | 283.5 | 29 | 139.3 | Cam Skattebo | 144.1 | 283.5 | 144.1 |
| Chase Brown | RB | 281.2 | 29 | 139.3 | Cam Skattebo | 141.9 | 281.2 | 141.9 |
| James Cook | RB | 269.9 | 29 | 139.3 | Cam Skattebo | 130.6 | 269.9 | 130.6 |
| Alvin Kamara | RB | 266.7 | 29 | 139.3 | Cam Skattebo | 127.3 | 266.7 | 127.3 |
| Chuba Hubbard | RB | 258.6 | 29 | 139.3 | Cam Skattebo | 119.2 | 258.6 | 119.2 |
| CeeDee Lamb | WR | 317.5 | 29 | 209.8 | Chris Olave | 107.7 | 317.5 | 107.7 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |

**Pick 21 / Round 3** → would take **Bucky Irving** (RB)

Baselines: `QB#10=301.9 (Bo Nix); RB#29=137.0 (Zach Charbonnet); WR#29=209.8 (Chris Olave); TE#12=156.9 (Dallas Goedert); DST#10=104.4 (Giants D/ST)`
RB#N vs WR#N: 137.02487636 vs 209.82328203 (diff -72.8); best RB−WR VOR gap +38.7

| candidate | pos | proj | repl_N | repl_pts | repl_name | VOR | gain_raw | gain_vor |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Bucky Irving | RB | 283.5 | 29 | 137.0 | Zach Charbonnet | 146.4 | 283.5 | 146.4 |
| Chase Brown | RB | 281.2 | 29 | 137.0 | Zach Charbonnet | 144.2 | 281.2 | 144.2 |
| James Cook | RB | 269.9 | 29 | 137.0 | Zach Charbonnet | 132.9 | 269.9 | 132.9 |
| Alvin Kamara | RB | 266.7 | 29 | 137.0 | Zach Charbonnet | 129.7 | 266.7 | 129.7 |
| Chuba Hubbard | RB | 258.6 | 29 | 137.0 | Zach Charbonnet | 121.5 | 258.6 | 121.5 |
| Jaylen Warren | RB | 250.2 | 29 | 137.0 | Zach Charbonnet | 113.2 | 250.2 | 113.2 |
| CeeDee Lamb | WR | 317.5 | 29 | 209.8 | Chris Olave | 107.7 | 317.5 | 107.7 |
| Trey McBride | TE | 259.2 | 12 | 156.9 | Dallas Goedert | 102.3 | 259.2 | 102.3 |

