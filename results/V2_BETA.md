# V2-beta research record

## Equal-weight policy mixture — REJECTED

**Status:** rejected (negative result — keep artifacts).

Formulation: \(EV_\beta=\frac13(EV_{ADP}+EV_{proj}+EV_{VOR})\).

Pilot: [`stress_v2beta_pilot_slot1.md`](stress_v2beta_pilot_slot1.md).

Averaging finished futures dilutes the dangerous scenario without encoding
player-specific survival risk. **Do not** tune mixture weights.

## Survival diagnostic — Outcome A

[`case_study_survival_chase_daniels.md`](case_study_survival_chase_daniels.md):
under proj death, Daniels-now beats Chase+replacement QB (~+33.6).

## β2 robust-min — REJECTED as final strategy

Diagnostic pass: [`case_study_robust_min.md`](case_study_robust_min.md)  
Lean: [`stress_robust_min_slot1.md`](stress_robust_min_slot1.md)

| opponent | α−raw | rob−raw | rob−α |
| --- | ---: | ---: | ---: |
| noisy_adp | +71.3 | −0.9 | **−72.3** |
| adp_greedy | +76.3 | +0.0 | **−76.3** |
| proj_greedy | −17.0 | **0.0** | **+17.0** |
| vor | +41.4 | +24.8 | −16.6 |

Fixes projection-greedy failure but over-insures (always Daniels at R1).
**Do not** tweak `min_f` weights. UI stays `marginal`.

## Next

Risk/EV surface + Pareto frontier (no new overnight sims):
[`case_study_risk_ev_surface.md`](case_study_risk_ev_surface.md) via
`python -m draftopt.case_study_risk_surface`.

Decide A (objective) / B (scenario set) / C (both) before designing the next
strategy.
