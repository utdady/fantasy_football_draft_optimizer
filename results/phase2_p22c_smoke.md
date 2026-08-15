# P2.2C smoke (decision world)

- snapshot: `2024-preseason-2024-09-01-ffc12`
- evaluable: **0**
- leakage: **pass**
- decision_market: FFC · league_size: 12
- value_signal: `adp_linear_v1_2024_ffc12`

**curve_starter_pts use ADP-derived values aliased as ESPN projections in draft_db. NOT actual 2024 PPR. NOT production marginal.**

## Runs

| strategy | slot | seed | curve starter | rank | first pick |
| --- | ---: | ---: | ---: | ---: | --- |
| `adp_baseline` | 1 | 42 | 2075.8 | 6 | Christian McCaffrey |
| `adp_structural` | 1 | 42 | 2213.6 | 1 | Christian McCaffrey |
| `adp_baseline` | 5 | 42 | 2154.0 | 2 | Christian McCaffrey |
| `adp_structural` | 5 | 42 | 2268.4 | 1 | Christian McCaffrey |
| `adp_baseline` | 10 | 42 | 2137.3 | 2 | Bijan Robinson |
| `adp_structural` | 10 | 42 | 2227.3 | 1 | Bijan Robinson |

## Δ curve starter (structural − baseline)

| slot | seed | Δ | baseline | structural |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 42 | +137.8 | 2075.8 | 2213.6 |
| 5 | 42 | +114.4 | 2154.0 | 2268.4 |
| 10 | 42 | +89.9 | 2137.3 | 2227.3 |

Next: Attach nflverse 2024 PPR outcomes and score Δ on actual points; keep evaluable=0 until coverage gates pass.
