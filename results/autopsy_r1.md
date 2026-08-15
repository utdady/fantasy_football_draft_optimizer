# Autopsy · draft `eb8374278e41` · pick 1

**Gate 1: CLOSED** (pass / inconclusive). Do not rerun empty-board Allen/Gibbs. Next: live_sim Gate 2.

- board_hash: `e3b0c44298fc1c14`
- control: **marginal**
- next user overall: 24
- picks until next: 22
- ranking flipped vs M (stub): **True**

Lookahead / survival columns are diagnostic stubs only. They do not change TAKE. Do not ship without Gate 1–3 in AUTOPSY_GATE.md.

| Player | Pos | M | P(survive) | E[next M] | EV stub | Δ(EV−M) | next q |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Josh Allen | QB | 369.21 | 0.4673 | 273.08 | 642.29 | 273.08 | Breece Hall |
| Jahmyr Gibbs | RB | 365.27 | 0.1152 | 322.5 | 687.77 | 322.5 | Lamar Jackson |
| Puka Nacua | WR | 356.57 | 0.1395 | 322.5 | 679.06 | 322.49 | Lamar Jackson |

Control best: **Josh Allen** · Stub best: **Jahmyr Gibbs**

## Reading (Gate 1 — empty 1.01, slot 1)

Inspect separately. Stubs only. TAKE unchanged.

| | Allen | Gibbs | Puka |
| --- | ---: | ---: | ---: |
| **M** | 369.21 | 365.27 | 356.57 |
| **P(survive to 2.12)** | 0.47 | 0.12 | 0.14 |
| **d(EV-M)** (ADP-greedy 22 CPU) | +273 (q=Breece) | +322 (q=Lamar) | +322 (q=Lamar) |

- **M:** Allen wins by ~4 over Gibbs. That is the frozen control. Human disagreement is not a 50-point M gap.
- **P(survive):** Gibbs/Puka are unlikely to last 22 picks; Allen (ADP ~23) is a coin flip at pick 24. This *directionally* matches “elite RB will not survive.” It is a crude sigmoid, not a model.
- **d(EV-M):** The ADP-greedy future **does** flip the ranking (Gibbs 687.8 vs Allen 642.3) because taking Allen lets the next 22 ADP names eat the skill pool and leaves Breece; taking Gibbs leaves a QB (Lamar). That is the same long-wait V2-alpha mechanism we already tested — **not** evidence to ship lookahead.

**Does the future-board term explain the disagreement?** Plausibly, as a story. **Does this earn V2?** No — same V2-alpha long-wait mechanism; need messy live boards (Gate 2), not more empty 1.01s.


Draft: `eb8374278e41`. Case: `results/autopsy_cases/eb8374278e41_pick1_e3b0c44298fc1c14.json`.
