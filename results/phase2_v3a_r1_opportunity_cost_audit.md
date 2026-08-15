# V3-A R1 fork opportunity-cost audit

- stage: `V3A_R1_FORK_OPPORTUNITY_COST_AUDIT`
- curve: `adp_emp_pos_v1_train_2021_2023` (frozen)
- evaluable: **0**
- pairs: 60 (ladder pick match: 60/60)
- source: `results\phase2_v3a_ladder.json`

Decision-time opportunity-cost audit at the R1 C/D fork on frozen V3-A boards. Targeted replay of adp_v3a only; map unchanged. Findings classify construction failure — not permission to retune calibration or resurrect V2.

**D and future E share frozen V3-A values; only construction may change. E−D is the causal V3-B test. Implementation of E remains blocked until this audit informs the V3-B contract.**

## Primary classification

**`D_combination`** — Combination: R1 empty-slot / zero-replacement drives the pick (marginal ≈ full calibrated value); multi-round opportunity cost drives roster translation failure (won fork pick, RB/portfolio hole).

Tag coverage: `{'n_with_A_tags': 60, 'n_with_B_tags': 60, 'n_with_C_tags': 39, 'n_combination_A_and_C': 39}`

Tag counts: `{'A_zero_replacement': 60, 'A_marginal_equals_full_value': 60, 'B_replacement_gap_large_but_unused': 60, 'C_rb_portfolio_hole': 35, 'D_combination_A_and_C': 39, 'C_won_pick_lost_roster': 26, 'C_large_negative_roster_delta': 22}`

## Decision-time (model belief)

lineup_before≈0 and marginal≈value ⇒ empty-slot / zero-replacement. model_marginal_adv = D.marginal − C_alt.marginal on D's board.

- lineup_before: mean=0.00, max=0.00
- marginal − calibrated value: mean=-0.00
- model marginal adv (D − C_alt): mean=+90.61, median=+103.25

## Realized opportunity cost

- fork pick actual D−C: mean=+212.95, WR(D)=95%
- starter total D−C: mean=+22.09, p10=-268.43
- RB starter D−C: mean=-161.67
- won pick / lost roster: 26/60

## Per-board rows

| Slot | Seed | D pick | C alt | D marg | C marg | before | act D | act C | Δfork | Δroster | ΔRB | tags |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +59.12 | -256.40 | A,B,C,D |
| 1 | 43 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -48.90 | +136.50 | A,B,C,D |
| 1 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +35.04 | -6.10 | A,B |
| 1 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -109.38 | -314.90 | A,B,C,D |
| 1 | 46 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +346.46 | +77.60 | A,B |
| 2 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +1.64 | -521.90 | A,B,C,D |
| 2 | 43 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -26.90 | +0.00 | A,B,C,D |
| 2 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +152.98 | +70.50 | A,B |
| 2 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +33.72 | -243.80 | A,B,C,D |
| 2 | 46 | Josh Allen (QB) | Breece Hall (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 240.90 | +138.14 | +115.22 | -144.30 | A,B,C,D |
| 3 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +259.18 | -83.70 | A,B,C,D |
| 3 | 43 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -149.34 | -102.10 | A,B,C,D |
| 3 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +212.26 | +214.50 | A,B |
| 3 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +257.82 | +116.00 | A,B |
| 3 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | -50.14 | -141.50 | A,B,C,D |
| 4 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +228.90 | +11.00 | A,B |
| 4 | 43 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +197.28 | +0.00 | A,B |
| 4 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +124.78 | +111.40 | A,B |
| 4 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +114.02 | +56.10 | A,B |
| 4 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | +212.20 | -37.00 | A,B |
| 5 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +13.78 | +0.00 | A,B |
| 5 | 43 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | -129.24 | -117.90 | A,B,C,D |
| 5 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +335.48 | +76.30 | A,B |
| 5 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -189.38 | -441.70 | A,B,C,D |
| 5 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | +88.50 | -8.00 | A,B |
| 6 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +261.48 | +0.00 | A,B |
| 6 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -465.04 | -520.30 | A,B,C,D |
| 6 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +223.24 | +128.50 | A,B |
| 6 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -85.10 | -259.20 | A,B,C,D |
| 6 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | -104.98 | -83.70 | A,B,C,D |
| 7 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -58.90 | -269.20 | A,B,C,D |
| 7 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -212.20 | -226.70 | A,B,C,D |
| 7 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +236.82 | +60.80 | A,B |
| 7 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +221.12 | +0.00 | A,B |
| 7 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | -0.12 | +0.00 | A,B,C,D |
| 8 | 42 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +269.50 | +76.00 | A,B |
| 8 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -282.52 | -644.12 | A,B,C,D |
| 8 | 44 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +508.32 | +66.60 | A,B |
| 8 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | -180.00 | -492.00 | A,B,C,D |
| 8 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | +319.30 | +24.80 | A,B |
| 9 | 42 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | +26.20 | -287.50 | A,B,C,D |
| 9 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -293.72 | -413.72 | A,B,C,D |
| 9 | 44 | Josh Allen (QB) | Justin Jefferson (WR) | 350.29 | 280.88 | 0.00 | 379.04 | 317.48 | +61.56 | -15.46 | +0.00 | A,B,C,D |
| 9 | 45 | Josh Allen (QB) | Christian McCaffrey (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 47.80 | +331.24 | +41.12 | -66.00 | A,B |
| 9 | 46 | Josh Allen (QB) | Tyreek Hill (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 218.20 | +160.84 | -322.68 | -216.30 | A,B,C,D |
| 10 | 42 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | -250.76 | -368.20 | A,B,C,D |
| 10 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -267.64 | -410.10 | A,B,C,D |
| 10 | 44 | Josh Allen (QB) | Justin Jefferson (WR) | 350.29 | 280.88 | 0.00 | 379.04 | 317.48 | +61.56 | +136.28 | -181.40 | A,B,C,D |
| 10 | 45 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | -183.48 | -661.30 | A,B,C,D |
| 10 | 46 | Josh Allen (QB) | Ja'Marr Chase (WR) | 350.29 | 283.13 | 0.00 | 379.04 | 403.00 | -23.96 | -82.10 | -183.40 | A,B,C,D |
| 11 | 42 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | -107.26 | -291.60 | A,B,C,D |
| 11 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | +195.50 | -403.62 | A,B,C,D |
| 11 | 44 | Josh Allen (QB) | Jonathan Taylor (RB) | 350.29 | 236.06 | 0.00 | 379.04 | 244.70 | +134.34 | +50.32 | -120.60 | A,B,C,D |
| 11 | 45 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | -96.20 | -578.80 | A,B,C,D |
| 11 | 46 | Josh Allen (QB) | Ja'Marr Chase (WR) | 350.29 | 283.13 | 0.00 | 379.04 | 403.00 | -23.96 | +153.12 | -108.30 | A,B,C,D |
| 12 | 42 | Josh Allen (QB) | Bijan Robinson (RB) | 350.29 | 247.04 | 0.00 | 379.04 | 341.70 | +37.34 | -345.58 | -492.60 | A,B,C,D |
| 12 | 43 | Josh Allen (QB) | CeeDee Lamb (WR) | 350.29 | 285.09 | 0.00 | 379.04 | 263.40 | +115.64 | -275.56 | -360.62 | A,B,C,D |
| 12 | 44 | Josh Allen (QB) | Jonathan Taylor (RB) | 350.29 | 236.06 | 0.00 | 379.04 | 244.70 | +134.34 | +38.08 | -320.20 | A,B,C,D |
| 12 | 45 | Josh Allen (QB) | Justin Jefferson (WR) | 350.29 | 280.88 | 0.00 | 379.04 | 317.48 | +61.56 | -8.20 | -237.10 | A,B,C,D |
| 12 | 46 | Josh Allen (QB) | Ja'Marr Chase (WR) | 350.29 | 283.13 | 0.00 | 379.04 | 403.00 | -23.96 | +197.18 | -310.70 | A,B,C,D |

## Mechanism key

| Code | Meaning |
| --- | --- |
| A | Zero-replacement / empty-slot fill (lineup_before≈0, marg≈value) |
| B | Replacement gap large but unused by model |
| C | Multi-round / portfolio opportunity cost |
| D | Combination of A and C |

## V3-B gate

- design justified: **True**
- implementation blocked: **True**
- next: Freeze V3-B contract: one construction change; identical V3-A values; evaluate E−D. Do not retune map; no λ/CVaR/V2.

- UI: `marginal`
- map: frozen
