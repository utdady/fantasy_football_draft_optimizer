# P2.2C — ADP-structural evaluation (labeled ablation)

**Status:** methodology frozen; snapshot + labeled strategies + smoke runner
landed. **Not** production `marginal`. Actual-PPR scoring still gated.

**Parents:** [`PHASE2_P22_SOURCES.md`](PHASE2_P22_SOURCES.md) · P2.2A
[`phase2_p22_feasibility_2024_12tm.md`](phase2_p22_feasibility_2024_12tm.md) ·
P2.2B closed [`phase2_p22b_fp_probe.md`](phase2_p22b_fp_probe.md)

---

## Why this exists

P2.2B could not confirm dated historical **projections** for 2024 via FantasyPros
free API. Rather than invent ECR→points or pay for unknown provenance, we run an
honest ablation:

> Does **roster construction / scarcity reasoning** improve realized PPR when the
> only decision-time value signal is historical ADP?

This is **not** “does production `marginal` beat ADP.”

---

## Frozen labels (do not blur)

| Field | Value |
| --- | --- |
| `decision_market` | FFC |
| `league_size` | **12** (not 10 — FFC 2024 meta) |
| `scoring` | PPR |
| `value_signal` | ADP-derived structural curve |
| `outcomes` | nflverse 2024 actual PPR (`nflverse_computed`) |
| `snapshot_date` / ADP `as_of` | FFC window end `2024-09-01` |

**Honesty bar:** FFC ≠ ESPN · 12 ≠ 10 · ADP-curve ≠ ESPN `proj_ppr` · ECR ≠ proj.

### Strategy names (required)

| Name | Meaning |
| --- | --- |
| `adp_baseline` | Always pick best remaining ADP (lowest ADP) |
| `adp_structural` | Same marginal **roster-construction** machinery as V1, but `proj_ppr` replaced by an **ADP-derived** value curve |
| `adp_structural_vor` | Optional later: VOR-lite on the same ADP-derived curve |

Do **not** register these as UI default. Do **not** rename them to `marginal`.

---

## Optimizer vs evaluator

| Data | Optimizer? | Evaluator? |
| --- | ---: | ---: |
| FFC 2024 ADP (dated window) | ✅ | — |
| ADP-derived value curve | ✅ | — |
| Draft slot / 12-team snake / roster rules | ✅ | — |
| Actual 2024 PPR (nflverse) | ❌ | ✅ |
| ESPN / FP projections | ❌ | ❌ |
| In-season injuries | ❌ | ❌ |

---

## ADP → value curve (FROZEN — do not retune after outcomes)

**Curve ID:** `adp_linear_v1_2024_ffc12`  
**Code:** `src/draftopt/phase2/adp_value_curve.py`

\[
v = \mathrm{clamp}\big(V_{\mathrm{floor}},\;
V_{\max}\cdot\frac{\mathrm{ADP}_{\mathrm{ref}}-\mathrm{ADP}}{\mathrm{ADP}_{\mathrm{ref}}-1},\;
V_{\max}\big)
\]

| Constant | Value |
| --- | ---: |
| `V_MAX` | 350 |
| `ADP_REF` | 180 |
| `V_FLOOR` | 1 |

Chosen **before** any actual-PPR comparison. Changing these after seeing Δ is a methodology leak.

---

## Decision-space coverage gate (before PPR)

Board coverage ≠ outcome coverage. Unmapped `ffc:*` players remain draftable but
are silent losses for actual-PPR scoring.

| Check | Required for later `evaluable` claim |
| --- | --- |
| Overall / top-50 / 100 / 150 ADP coverage | Explicit in report |
| Unmapped by position + ADP band | Explicit |
| Strategy selections of unmapped / no outcome key | **Must be zero** |
| Offense/K | mapped + **gsis** |
| DST | mapped to **`dst:{TEAM}`** (team entity; not fake GSIS) |
| Outcome (nflverse) coverage | After attach — not this step |

**Audit trail:** failed v1
[`phase2_p22c_decision_space_coverage.md`](phase2_p22c_decision_space_coverage.md)
→ mapping repair → pass v2
[`phase2_p22c_decision_space_coverage_v2.md`](phase2_p22c_decision_space_coverage_v2.md)
(205/205 mapped; 0 strategy unmapped selections; `evaluable` still 0).

```bash
python -m draftopt.phase2.coverage_p22c --slots 1,5,10 --n-sims 3 \
  --out results/phase2_p22c_decision_space_coverage_v2.md
```

---

## Experiment steps (order)

1. Freeze decision snapshot from FFC 2024 **12-team** cut (`evaluable=0`,
   `validation_status=source_validation`, reason notes ADP-structural track).
2. **Decision-space coverage** → fix high-value unmapped → rematerialize until gate passes.
3. Leakage validate (`*_as_of ≤ snapshot_date`).
4. Replay: `adp_baseline` vs `adp_structural` (same slots/seeds; **12 teams × 15 rounds**
   matching FFC meta; `league_default` roster, K not drafted).
5. Score rosters with **actual** starter PPR (same slots as league).
6. Report \(\Delta = \mathrm{PPR}_{structural} - \mathrm{PPR}_{baseline}\) by slot
   (+ stratified / mapping-sensitivity).
7. Only then consider `evaluable=1` for this **labeled** experiment (still not
   Stage B “marginal vs ADP on ESPN proj”).

Smoke (`smoke_p22c`) reports ADP-**curve** starter Δ only — not empirical validity.
Coverage (`coverage_p22c`) is the gate before step 5.

---

## Possible outcomes (all scientifically useful)

| Result | Interpretation |
| --- | --- |
| **A** structural ≫ baseline | Roster construction has real-world value even on ADP-only signal → justifies later projection hunt / V3 interest |
| **B** structural ≈ baseline | Phase 1 sim edge may be projection-environment artifact |
| **C** structural ≪ baseline | Strong warning against VOR sophistication before fixing value signal |

---

## Explicit non-goals

- Calling this production `marginal` validation
- Using 12-team results to claim 10-team ESPN-league wins
- V2 / β / robust_min / V3
- Tuning ADP curve after seeing outcomes
- ECR→points

---

## Progress

```text
P2.2B  ██████████ CLOSED (FP free API)
P2.2C  ██████░░░░ mapping green + outcomes attach/gate (evaluable=0; Δ next)
```

### Commands

```bash
# Freeze FFC12 decision world (evaluable=0)
python -m draftopt.phase2.materialize_p22c

# Decision-space coverage (v2 after mapping repair)
python -m draftopt.phase2.coverage_p22c --slots 1,5,10 --n-sims 3 \
  --out results/phase2_p22c_decision_space_coverage_v2.md

# Attach 2024 nflverse outcomes under ppr_eval_v1_2024 (no Δ)
python -m draftopt.phase2.attach_outcomes_p22c

# Outcome coverage gate
python -m draftopt.phase2.outcome_coverage_p22c
```

Scoring contract: [`PHASE2_P22C_SCORING_CONTRACT_ppr_eval_v1_2024.md`](PHASE2_P22C_SCORING_CONTRACT_ppr_eval_v1_2024.md)
