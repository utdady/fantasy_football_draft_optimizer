# Survival diagnostic: Chase / Daniels @ slot-1 #1

## Question

Is the proj-greedy V2 failure caused by missing **explicit survival risk** for the deferred player (Outcome A), or does the **downstream roster** still prefer Chase even when Daniels is known dead (Outcome B)?

## Frozen state

- slot `1`, overall `#1`, next `#20`, wait **18**
- source: proj_greedy V2 stress / β pilot R1
- roster: empty
- take-now candidate: **Ja'Marr Chase**; deferred q: **Jayden Daniels**
- policy disagreement only (no invented P=2/3)

## What α / β actually pick

- `marginal_v2`: **Ja'Marr Chase** (WR) q=Jayden Daniels EV=711.61
- `marginal_v2_beta`: **Ja'Marr Chase** (WR) q=Jayden Daniels EV=688.2
  - ev_by_future: `{'adp_greedy': 711.61, 'proj_greedy': 641.37, 'vor': 711.61}`

## Player ranks (among remaining @ #1)

| player | pos | proj | ADP rank | proj rank | VOR rank | VOR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Ja'Marr Chase | WR | 340.0 | 4 | 5 | 2 | 118.7 |
| Jayden Daniels | QB | 371.6 | 46 | 1 | 21 | 69.7 |
| Justin Fields | QB | 299.3 | 258 | 21 | 87 | 0.0 |
| Matthew Stafford | QB | 274.1 | 67 | 41 | 96 | 0.0 |

## Primary: Chase now vs Daniels now

- one-pick: take-now=340.0, deferred=371.6 (Δ deferred−take = +31.6)
- policy disagreement: `{'adp_greedy': 'survives', 'proj_greedy': 'dies', 'vor': 'survives'}`

| future | q survives? | take-now + best q | take-now + best QB | deferred-now two-pick | Δ (deferred−take) | Δ (deferred − take+QB) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| adp_greedy | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 672.9 | -38.7 | -38.7 |
| proj_greedy | ✗ | 641.4 (Malik Nabers) | 639.3 (Justin Fields) | 672.9 | +31.6 | +33.6 |
| vor | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 689.1 | -22.5 | -22.5 |

**Outcome hint:** Outcome A (survival explains it): under proj death, taking deferred q now beats take-now + replacement QB


## Secondary (same R1 board): Chase now vs Fields deferred

- one-pick: take-now=340.0, deferred=299.3 (Δ deferred−take = -40.7)
- policy disagreement: `{'adp_greedy': 'survives', 'proj_greedy': 'survives', 'vor': 'survives'}`

| future | q survives? | take-now + best q | take-now + best QB | deferred-now two-pick | Δ (deferred−take) | Δ (deferred − take+QB) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| adp_greedy | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 600.7 | -111.0 | -111.0 |
| proj_greedy | ✓ | 641.4 (Malik Nabers) | 639.3 (Justin Fields) | 600.7 | -40.7 | -38.7 |
| vor | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 616.9 | -94.8 | -94.8 |

**Outcome hint:** inconclusive (proj does not kill q)


## Secondary (same R1 board): Chase now vs Stafford deferred

- one-pick: take-now=340.0, deferred=274.1 (Δ deferred−take = -65.9)
- policy disagreement: `{'adp_greedy': 'survives', 'proj_greedy': 'survives', 'vor': 'survives'}`

| future | q survives? | take-now + best q | take-now + best QB | deferred-now two-pick | Δ (deferred−take) | Δ (deferred − take+QB) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| adp_greedy | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 575.4 | -136.2 | -136.2 |
| proj_greedy | ✓ | 641.4 (Malik Nabers) | 639.3 (Justin Fields) | 575.4 | -65.9 | -63.9 |
| vor | ✓ | 711.6 (Jayden Daniels) | 711.6 (Jayden Daniels) | 591.6 | -120.0 | -120.0 |

**Outcome hint:** inconclusive (proj does not kill q)

## After Chase + 18 proj-greedy CPUs (authentic #20 board)

- overall: `#20`
- Daniels still available: **False**
- Fields still available: **True**
- Stafford still available: **True**

V2-alpha top-3:

- Malik Nabers (WR) q=Justin Fields EV=940.69
- Justin Fields (QB) q=Malik Nabers EV=940.69
- Puka Nacua (WR) q=Malik Nabers EV=940.0

## Diagnostic at #20 (α take-now vs its deferred q)

- one-pick: take-now=641.4, deferred=639.3 (Δ deferred−take = -2.0)
- policy disagreement: `{'adp_greedy': 'survives', 'proj_greedy': 'survives', 'vor': 'survives'}`

| future | q survives? | take-now + best q | take-now + best QB | deferred-now two-pick | Δ (deferred−take) | Δ (deferred − take+QB) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| adp_greedy | ✓ | 940.7 (Justin Fields) | 940.7 (Justin Fields) | 940.7 | +0.0 | +0.0 |
| proj_greedy | ✓ | 940.7 (Justin Fields) | 940.7 (Justin Fields) | 940.7 | +0.0 | +0.0 |
| vor | ✓ | 940.7 (Justin Fields) | 940.7 (Justin Fields) | 940.7 | +0.0 | +0.0 |

**Outcome hint:** inconclusive (proj does not kill q)

## Verdict (primary R1)

- proj kills Daniels: **True**
- under that death, Daniels-now beats Chase+replacement QB: **True**
- Outcome A (survival explains it): under proj death, taking deferred q now beats take-now + replacement QB

### Architecture implication

- **Outcome A** → build β2 around survival-aware EV (with a principled survival model — not 2/3 policy votes).
- **Outcome B** → survival alone is not enough; need a richer distribution over future roster states before coding β2.
