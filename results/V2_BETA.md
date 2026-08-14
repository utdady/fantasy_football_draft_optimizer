# V2-beta (policy mixture) — REJECTED

**Status:** rejected (negative result — keep artifacts).

## Formulation

Equal-weight average of complete two-pick futures:

\[
EV_\beta(p)=\tfrac13\bigl(EV_{ADP}(p)+EV_{proj}(p)+EV_{VOR}(p)\bigr)
\]

Strategy: `marginal_v2_beta` (aliases: `v2_beta`, `v2b`). UI default stayed `marginal`.

## Pilot (slot 1, n=10)

See [`stress_v2beta_pilot_slot1.md`](stress_v2beta_pilot_slot1.md).

| opponent | α−raw | β−raw | β−α |
| --- | ---: | ---: | ---: |
| noisy_adp | +83.7 | +57.1 | **−26.6** |
| adp_greedy | +76.3 | +50.9 | **−25.4** |
| proj_greedy | −17.0 | **−28.8** | **−11.8** |
| vor | +41.4 | +66.2 | +24.8 |

## Rejection reason

Equal-weight averaging of finished future policies sacrifices ~25–27 points of
α’s ADP-like advantage and does **not** eliminate the projection-greedy failure
(Chase → deferred QB sniped). Averaging worlds is the wrong representation of
survival uncertainty — not a weight-tuning problem.

**Do not** hand-tune mixture weights against this stress grid. **Do not** run a
full β matrix.

## Next

Exact failure-state survival diagnostic: [`case_study_survival_chase_daniels.md`](case_study_survival_chase_daniels.md).

**Verdict: Outcome A** — under the proj death branch, taking Daniels now beats
Chase + replacement QB (~+33.6). Explicit survival risk would flip the R1
decision; policy-mixture failed because it diluted that branch instead of
representing it.

## β2-robust diagnostic (not a strategy)

[`case_study_robust_min.md`](case_study_robust_min.md) — `min_f` over scenario
two-pick EVs (ADP/proj/VOR).

**Result:** R1 flips Chase→Daniels without hardcoding; **agrees with α on all
three neighbor boards** (wait-0 / healthy paths). Do not promote minimax to
UI yet — still a diagnostic — but it clears the tiny pass bar for a slot-1 ×
4-policy lean test if desired.
