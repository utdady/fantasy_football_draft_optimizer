# V2-alpha validation — slots 1-10 n=50

## Setup

- n_sims per slot: **50**
- teams: **10**
- preset: `league_default`
- seed: `0`
- slots: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`
- strategies: `adp, marginal, marginal_vor, marginal_v2`
- pairing: shared sim seed + CPU RNG keyed by overall pick #
- scoring: ESPN season projections only (starter EV)
- CPU: noisy ADP (not human ESPN managers)

## Notes

- Scored on ESPN preseason projections (not actual season outcomes).
- Opponents use noisy-ADP CPU policy — not human ESPN managers.

## Slot matrix

| slot | adp | marginal | marginal_vor | marginal_v2 | vor−adp | vor>adp | vor−raw | vor>raw | v2−raw | v2>raw | v2−vor | v2>vor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2173.0 | 2423.0 | 2439.0 | 2494.9 | +266.0 | 100.0% | +16.0 | 66.0% | +72.0 | 98.0% | +56.0 | 100.0% |
| 2 | 2173.2 | 2427.2 | 2445.1 | 2497.5 | +271.9 | 100.0% | +17.9 | 72.0% | +70.3 | 100.0% | +52.4 | 98.0% |
| 3 | 2160.9 | 2432.8 | 2447.4 | 2499.9 | +286.5 | 100.0% | +14.6 | 66.0% | +67.1 | 98.0% | +52.5 | 98.0% |
| 4 | 2187.7 | 2439.8 | 2447.3 | 2501.2 | +259.6 | 100.0% | +7.5 | 56.0% | +61.4 | 100.0% | +53.9 | 98.0% |
| 5 | 2162.6 | 2444.3 | 2443.4 | 2500.2 | +280.8 | 100.0% | -0.8 | 38.0% | +55.9 | 98.0% | +56.8 | 98.0% |
| 6 | 2147.4 | 2449.7 | 2441.1 | 2502.3 | +293.7 | 100.0% | -8.6 | 38.0% | +52.6 | 96.0% | +61.2 | 96.0% |
| 7 | 2181.0 | 2451.5 | 2438.9 | 2502.4 | +257.9 | 98.0% | -12.6 | 32.0% | +51.0 | 96.0% | +63.6 | 98.0% |
| 8 | 2104.6 | 2449.5 | 2433.4 | 2490.3 | +328.8 | 100.0% | -16.1 | 24.0% | +40.8 | 98.0% | +57.0 | 98.0% |
| 9 | 2144.8 | 2447.3 | 2429.0 | 2485.5 | +284.2 | 100.0% | -18.3 | 18.0% | +38.2 | 92.0% | +56.5 | 98.0% |
| 10 | 2157.2 | 2446.5 | 2433.6 | 2484.1 | +276.4 | 98.0% | -12.9 | 30.0% | +37.6 | 92.0% | +50.5 | 98.0% |

`win%` / `vor>adp` / `vor>raw` / `v2>raw` / `v2>vor` = paired starter-points win rate (not wide-receiver share).

## Starter-EV dispersion (population stdev)

| slot | adp std | marginal std | marginal_vor std | marginal_v2 std |
| --- | ---: | ---: | ---: | ---: |
| 1 | 95.5 | 29.9 | 34.6 | 21.8 |
| 2 | 113.0 | 28.1 | 31.9 | 21.0 |
| 3 | 106.5 | 30.1 | 34.0 | 22.4 |
| 4 | 122.2 | 24.1 | 37.7 | 24.5 |
| 5 | 111.7 | 22.3 | 28.7 | 24.1 |
| 6 | 139.9 | 22.1 | 29.6 | 19.2 |
| 7 | 112.6 | 23.8 | 30.7 | 16.6 |
| 8 | 168.0 | 22.2 | 26.0 | 26.0 |
| 9 | 166.3 | 24.7 | 25.1 | 26.4 |
| 10 | 132.1 | 23.2 | 25.7 | 25.4 |

### Paired Δ dispersion (V2)

| slot | v2−raw mean | v2−raw std | v2−vor mean | v2−vor std | v2−adp mean | v2−adp std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | +72.0 | 27.4 | +56.0 | 29.5 | +322.0 | 96.4 |
| 2 | +70.3 | 30.3 | +52.4 | 31.3 | +324.3 | 108.0 |
| 3 | +67.1 | 31.3 | +52.5 | 34.6 | +339.0 | 109.2 |
| 4 | +61.4 | 30.8 | +53.9 | 31.6 | +313.5 | 123.0 |
| 5 | +55.9 | 31.9 | +56.8 | 29.4 | +337.6 | 113.7 |
| 6 | +52.6 | 29.4 | +61.2 | 27.9 | +354.9 | 140.2 |
| 7 | +51.0 | 28.5 | +63.6 | 31.1 | +321.5 | 113.6 |
| 8 | +40.8 | 24.0 | +57.0 | 28.9 | +385.7 | 166.2 |
| 9 | +38.2 | 29.5 | +56.5 | 30.2 | +340.7 | 167.6 |
| 10 | +37.6 | 29.6 | +50.5 | 24.9 | +326.9 | 132.4 |

## Position mix (user picks)

### Slot 1

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 17%, RB 33%, WR 34%, TE 8%, DST 8% | R1: RB 100% · R2: RB 52%, WR 36%, TE 12% · R3: QB 10%, RB 60%, WR 10%, TE 20% |
| marginal | QB 12%, RB 29%, WR 36%, TE 12%, DST 11% | R1: QB 100% · R2: RB 36%, WR 64% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 37%, WR 28%, TE 12%, DST 10% | R1: RB 100% · R2: RB 98%, WR 2% · R3: RB 100% |
| marginal_v2 | QB 12%, RB 28%, WR 37%, TE 10%, DST 12% | R1: WR 100% · R2: RB 44%, WR 56% · R3: QB 2%, RB 28%, WR 70% |

### Slot 2

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 31%, WR 35%, TE 8%, DST 10% | R1: RB 100% · R2: RB 56%, WR 34%, TE 10% · R3: QB 18%, RB 50%, WR 16%, TE 16% |
| marginal | QB 13%, RB 29%, WR 35%, TE 14%, DST 10% | R1: QB 100% · R2: RB 46%, WR 54% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 35%, WR 30%, TE 12%, DST 10% | R1: RB 100% · R2: RB 100% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 27%, WR 37%, TE 10%, DST 12% | R1: RB 8%, WR 92% · R2: RB 52%, WR 48% · R3: RB 18%, WR 82% |

### Slot 3

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 34%, WR 36%, TE 8%, DST 8% | R1: RB 92%, WR 8% · R2: RB 52%, WR 44%, TE 4% · R3: QB 14%, RB 60%, WR 16%, TE 10% |
| marginal | QB 13%, RB 30%, WR 34%, TE 12%, DST 12% | R1: QB 100% · R2: RB 58%, WR 42% · R3: RB 10%, WR 90% |
| marginal_vor | QB 14%, RB 35%, WR 30%, TE 11%, DST 11% | R1: RB 84%, WR 16% · R2: RB 98%, WR 2% · R3: RB 100% |
| marginal_v2 | QB 15%, RB 26%, WR 36%, TE 11%, DST 12% | R1: RB 20%, WR 80% · R2: RB 58%, WR 42% · R3: RB 12%, WR 88% |

### Slot 4

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 16%, RB 32%, WR 37%, TE 8%, DST 8% | R1: RB 82%, WR 18% · R2: RB 50%, WR 46%, TE 4% · R3: QB 18%, RB 48%, WR 20%, TE 14% |
| marginal | QB 12%, RB 30%, WR 35%, TE 12%, DST 10% | R1: QB 100% · R2: RB 66%, WR 34% · R3: RB 8%, WR 92% |
| marginal_vor | QB 13%, RB 34%, WR 30%, TE 12%, DST 11% | R1: RB 74%, WR 26% · R2: RB 100% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 27%, WR 37%, TE 10%, DST 12% | R1: RB 26%, WR 74% · R2: RB 62%, WR 38% · R3: RB 12%, WR 88% |

### Slot 5

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 13%, RB 34%, WR 36%, TE 10%, DST 6% | R1: RB 68%, WR 32% · R2: RB 44%, WR 56% · R3: QB 14%, RB 50%, WR 12%, TE 24% |
| marginal | QB 13%, RB 30%, WR 32%, TE 13%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 12%, WR 88% |
| marginal_vor | QB 13%, RB 36%, WR 30%, TE 12%, DST 10% | R1: RB 76%, WR 24% · R2: RB 92%, WR 8% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 28%, WR 38%, TE 11%, DST 10% | R1: RB 38%, WR 62% · R2: RB 68%, WR 32% · R3: RB 16%, WR 84% |

### Slot 6

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 39%, TE 11%, DST 6% | R1: RB 56%, WR 44% · R2: RB 40%, WR 60% · R3: QB 6%, RB 56%, WR 14%, TE 24% |
| marginal | QB 14%, RB 30%, WR 36%, TE 11%, DST 10% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 14%, WR 86% |
| marginal_vor | QB 14%, RB 34%, WR 30%, TE 11%, DST 12% | R1: RB 82%, WR 18% · R2: RB 96%, WR 2%, TE 2% · R3: RB 100% |
| marginal_v2 | QB 15%, RB 28%, WR 35%, TE 11%, DST 11% | R1: RB 48%, WR 52% · R2: RB 64%, WR 36% · R3: RB 22%, WR 78% |

### Slot 7

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 30%, WR 38%, TE 12%, DST 6% | R1: RB 46%, WR 54% · R2: RB 50%, WR 50% · R3: QB 10%, RB 58%, WR 12%, TE 20% |
| marginal | QB 14%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 68%, WR 32% · R3: RB 18%, WR 82% |
| marginal_vor | QB 12%, RB 35%, WR 29%, TE 12%, DST 12% | R1: RB 96%, WR 4% · R2: RB 94%, WR 6% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 30%, WR 33%, TE 11%, DST 12% | R1: RB 56%, WR 44% · R2: RB 66%, WR 34% · R3: RB 22%, WR 78% |

### Slot 8

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 43%, TE 10%, DST 6% | R1: RB 42%, WR 58% · R2: RB 36%, WR 64% · R3: QB 10%, RB 60%, WR 12%, TE 18% |
| marginal | QB 13%, RB 30%, WR 33%, TE 13%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 10%, WR 90% |
| marginal_vor | QB 13%, RB 36%, WR 28%, TE 13%, DST 11% | R1: RB 90%, WR 10% · R2: RB 96%, WR 4% · R3: RB 100% |
| marginal_v2 | QB 14%, RB 29%, WR 35%, TE 11%, DST 12% | R1: RB 60%, WR 40% · R2: RB 68%, WR 32% · R3: RB 28%, WR 72% |

### Slot 9

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 12%, RB 29%, WR 41%, TE 12%, DST 7% | R1: RB 44%, WR 56% · R2: RB 44%, WR 56% · R3: QB 8%, RB 44%, WR 24%, TE 24% |
| marginal | QB 13%, RB 31%, WR 33%, TE 11%, DST 11% | R1: QB 100% · R2: RB 76%, WR 24% · R3: RB 30%, WR 70% |
| marginal_vor | QB 13%, RB 36%, WR 28%, TE 12%, DST 11% | R1: RB 96%, WR 4% · R2: RB 92%, WR 8% · R3: RB 100% |
| marginal_v2 | QB 15%, RB 28%, WR 35%, TE 12%, DST 10% | R1: RB 68%, WR 32% · R2: RB 54%, WR 46% · R3: RB 32%, WR 68% |

### Slot 10

| strategy | position share | early rounds (1–3) |
| --- | --- | --- |
| adp | QB 14%, RB 26%, WR 40%, TE 13%, DST 7% | R1: RB 44%, WR 56% · R2: RB 34%, WR 66% · R3: QB 8%, RB 50%, WR 22%, TE 20% |
| marginal | QB 14%, RB 32%, WR 32%, TE 12%, DST 11% | R1: QB 100% · R2: RB 74%, WR 26% · R3: RB 32%, WR 68% |
| marginal_vor | QB 13%, RB 35%, WR 29%, TE 11%, DST 10% | R1: RB 96%, WR 4% · R2: RB 86%, WR 14% · R3: RB 100% |
| marginal_v2 | QB 13%, RB 28%, WR 37%, TE 11%, DST 11% | R1: RB 74%, WR 26% · R2: RB 56%, WR 44% · R3: RB 34%, WR 66% |

