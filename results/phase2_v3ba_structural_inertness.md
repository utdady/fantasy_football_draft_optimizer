# V3-B Branch A structural inertness diagnostic

- created: `2026-08-15T14:36:50Z`
- boards: 60
- user decisions: 900

Branch A q* excludes the candidate's whole position, so the unique global M_D argmax with pos in N(R) is structurally protected vs cross-position challengers; within-position M_A is an affine shift of M_D.

**Same-pos gap cannot create A≠D (order preserved within position). 0/60 ladder identity is expected when structural_protected holds almost always. This is not a strong empirical falsification of opportunity cost as a concept.**

## Headline

- A top1 == D top1: **900/900** (100.0%)
- unique global M_D max: 401/900 (44.6%)
- pos(p*) in N(R): 540/900 (60.0%)
- **structural_protected** (unique max AND pos in N(R) AND q* present): **285/900** (31.7%)
- protected but A≠D: **0** (expect 0)
- unprotected decisions: 615; among them A≠D: 0
- cross_alt_missing (M_A falls back to M_D): 534/900 (59.3%)
- unprotected breakdown: `{'cross_alt_missing_fallback_to_md': 534, 'not_unique_global_max': 81, 'unique_but_pos_not_in_N_R': 0}`

Early rounds are almost entirely **incumbent-protected**. Later rounds are mostly **missing-alt fallback** (N(R) empty / no cross need) where M_A = M_D by definition — still not an empirical OC test.

## Same-position gap (cannot flip A vs D)

- n with same-pos runner-up: 883
- mean / median / p10 / min gap: 4.4938 / 0.0 / 0.0 / 0.0

Within a position, M_A subtracts the same outside q*, so order matches M_D. Narrow same-pos gaps do **not** create policy divergence.

## Protected rate by round

| Round | n | protected | frac |
| ---: | ---: | ---: | ---: |
| 1 | 60 | 60 | 100% |
| 2 | 60 | 60 | 100% |
| 3 | 60 | 48 | 80% |
| 4 | 60 | 16 | 27% |
| 5 | 60 | 59 | 98% |
| 6 | 60 | 41 | 68% |
| 7 | 60 | 1 | 2% |
| 8 | 60 | 0 | 0% |
| 9 | 60 | 0 | 0% |
| 10 | 60 | 0 | 0% |
| 11 | 60 | 0 | 0% |
| 12 | 60 | 0 | 0% |
| 13 | 60 | 0 | 0% |
| 14 | 60 | 0 | 0% |
| 15 | 60 | 0 | 0% |

## Reading for Branch B

| Wrong sentence | Better sentence |
| --- | --- |
| OC failed empirically; only lookahead remains | This single-reference, position-excluded subtraction was **structurally near-inert** |
| Same-pos near-ties might have saved A | Same-pos margins cannot produce A≠D under this formula |

Branch B design (when opened) must **forbid** scores of the form M_D(p)-c(p) where c is constant across candidates or systematically smaller for the current M_D-argmax than for cross-position rivals.

- UI: `marginal`
- map: frozen
