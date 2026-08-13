# V2-alpha baseline (frozen)

**Status:** frozen for validation — do not change the V2-alpha formula while running the confirmation suite.

## Freeze point

| Field | Value |
| --- | --- |
| Git commit | `dcc2e05` (`feat: V2-alpha deterministic ADP lookahead`) |
| Tag | `v2-alpha-baseline` |
| Strategy name | `marginal_v2` (aliases: `v2`, `v2_alpha`, `lookahead_adp`) |
| UI default | still raw `marginal` (unchanged) |

## Frozen objective

For candidate \(p\) at overall \(t\), next user pick \(t'\):

1. Take \(p\)
2. Advance opponents with **ADP-greedy** for \(t'-t-1\) picks (deterministic; in-memory)
3. At \(t'\), take \(q\) = best remaining by **raw** lineup_ev lift
4. \(\mathrm{EV}(p) = L(R \cup \{p, q\})\) using raw ESPN starter points

## Lean evidence (pre-validation)

See [`ablation_v2alpha_slots_1_5_10.md`](ablation_v2alpha_slots_1_5_10.md) (n=20, slots 1/5/10) and
[`case_study_v2alpha_long_wait.md`](case_study_v2alpha_long_wait.md).

## Caveat

**V2-alpha is not yet validated as a real-world drafting advantage.** It currently
demonstrates an advantage over V1 baselines under an ADP-greedy *lookahead* model
while draft opponents in backtests use the noisy-ADP CPU. Treat lean +Δ as
directional until the full validation suite completes.

## Validation protocol (locked)

1. Freeze (this document + tag)  
2. Small RAW / VOR / V2 divergence trace  
3. Full slots 1–10 × n=50 paired matrix  
4. Opponent-policy stress (lean seats)  
5. Only then consider V2-β — shape dictated by failure modes  

No runtime optimization of `marginal_v2` until this baseline’s confirmation artifacts exist.
