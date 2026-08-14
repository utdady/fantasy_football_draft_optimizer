# Real-DB recommendation latency

- players in DB: **859**
- slot: **1**
- warm repeats: **20**
- seed: `0`

| strategy | user pick # | overall | remaining | candidates | wait | cold ms | p50 | p95 | p99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| marginal | 1 | 1 | 793 | 58 | None | 25.7 | 19.6 | 42.4 | 48.0 |
| marginal | 2 | 20 | 774 | 63 | None | 19.0 | 27.1 | 40.2 | 43.4 |
| marginal | 3 | 21 | 773 | 64 | None | 111.2 | 166.6 | 375.3 | 391.7 |
| marginal_vor | 1 | 1 | 793 | 58 | None | 146.8 | 106.5 | 131.2 | 145.5 |
| marginal_vor | 2 | 20 | 774 | 63 | None | 105.7 | 66.2 | 126.8 | 140.3 |
| marginal_vor | 3 | 21 | 773 | 64 | None | 15.8 | 42.7 | 81.6 | 90.3 |
| marginal_v2 | 1 | 1 | 793 | 58 | 18 | 714.1 | 699.8 | 906.5 | 965.7 |
| marginal_v2 | 2 | 20 | 774 | 63 | 0 | 444.3 | 753.5 | 901.5 | 1060.6 |
| marginal_v2 | 3 | 21 | 773 | 64 | 18 | 842.1 | 807.4 | 844.0 | 866.4 |

Threshold: should feel near-instant on a ~90s draft clock (comfortable if warm p95 ≪ 1–2s).
