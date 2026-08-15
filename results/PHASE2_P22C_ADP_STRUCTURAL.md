# P2.2C — ADP-structural evaluation (labeled ablation)

**Status:** Phase-2 closeout complete. **V3-A Gates 1–4 green**
([`V3A_CALIBRATION_DESIGN.md`](V3A_CALIBRATION_DESIGN.md);
[`gate1`](phase2_v3a_gate1_adp_provenance.md) ·
[`gate2`](phase2_v3a_gate2_train_outcomes.md) ·
[`gate3`](phase2_v3a_gate3_calibration_freeze.md) ·
[`gate4`](phase2_v3a_gate4_leakage_audit.md)).
Next: V3-A.0 **implementation** (fit + materialize + D−B/D−C) — still no UI change.
**Not** production `marginal`. `evaluable` still 0.

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
| `adp_baseline` | Always pick best remaining ADP (lowest ADP); **no** roster-need logic |
| `adp_feasible` | Lowest ADP among picks that preserve starter feasibility (QB/RB/WR/TE/FLEX/DST/K) |
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
P2.2C  ██████████ feasible ladder + C−B mechanism (evaluable=0; V3 still blocked)
```

### ADP-feasible ladder (load-bearing)

Artifact: [`phase2_p22c_adp_feasible_ladder.md`](phase2_p22c_adp_feasible_ladder.md)

Same 60 pairs (slots 1–12 × 5 sims, seed0=42), `ppr_eval_v1_2024`.

| Split | Feasibility (B−A) | **Valuation (C−B)** |
| --- | ---: | ---: |
| Full | +53.7 mean / 60% WR | **+76.5 mean / +54.1 med / 67% WR** |
| Ex-DST | −13.8 / 20% | **+67.8 / +42.2 / 65%** |
| Ex-DST+TE | −34.3 / 0% | **+41.3 / +28.3 / 57%** |

DST fill: baseline 35% · feasible 100% · structural 100%.

**Read:** C−A (+130) was contaminated by feasibility. After controlling with `adp_feasible`, structural still beats feasible on full and ex-DST — first evidence of a valuation/construction edge beyond “fill required slots.” Still n=1 season, modeled opponents; not V3 greenlight; UI stays `marginal`.

### C−B mechanism (position / round / slot / left tail)

Artifact: [`phase2_p22c_valuation_cb_mechanism.md`](phase2_p22c_valuation_cb_mechanism.md)

Offline attribution from the ladder JSON (no re-sim):

| Lens | Finding |
| --- | --- |
| Position | Mean C−B driven by **WR (+44)** and **TE (+26)**; QB ≈ 0; RB mean slightly negative |
| Round band | Gains in all bands; mid **r6-10** and late still matter; R6 large +, R10/R12/R14 large − |
| Slot | Highly uneven (n=5/slot); slot 7 outlier-strong; slot 1 contains the −282 min |
| Left tail | Worst 10 mean **−128**; losses concentrated in **RB/TE/QB** and **r11-15**; often miss late RB/TE breakouts after early DST |

Research question for V3 design remains: **are left-tail failures systematic valuation errors?** Do not chase mean until that is answered.

### Left-tail loss-case inspection

Artifact: [`phase2_p22c_loss_case_inspection.md`](phase2_p22c_loss_case_inspection.md)

Worst 10 C−B pairs replayed with decision-time alternatives:

| Finding | Detail |
| --- | --- |
| Fork timing | Almost all first forks in **R5–R8** |
| Fork positions | C: TE/WR/RB · B: often **QB** or RB |
| Fork pick actual | C wins **1**, loses **9** on the fork pick itself |
| Post-fork | **10/10** have ≥80 PPR hindsight regret among shown alts later |
| DST-at-fork | **Not** the dominant first-split pattern in this set |

Provisional: losses look like **mid-draft valuation forks (often TE vs QB)** plus **downstream cascade**, not “forgot DST at the split.” Still hypotheses — V3 blocked.

### Phase-2 closeout (symmetry + fork prediction error)

Artifact: [`phase2_p22c_closeout.md`](phase2_p22c_closeout.md) · best-10: [`phase2_p22c_gain_case_inspection.md`](phase2_p22c_gain_case_inspection.md)

| Check | Result |
| --- | --- |
| skill-over-QB worst vs best | **6 vs 5** → symmetric / high-variance (do **not** V3 as “stop TE-over-QB”) |
| Fork win rate | worst 1/10 C wins fork; best 6/10 |
| Mean pred_error (actual−curve) | C picks **−94**; B picks **−7** (B QBs often under-projected) |
| Empty-slot fills (C) | 4/10 — marginal-construction still secondary candidate |

**Provisional V3 pointer:** projection/calibration (V3-A), not a one-sided positional rule.

**Design freeze:** [`V3A_CALIBRATION_DESIGN.md`](V3A_CALIBRATION_DESIGN.md) — no V3 code until the implementation gate in that note.
### Commands

```bash
# Attach outcomes + coverage gate (already green on 61888bd)
python -m draftopt.phase2.attach_outcomes_p22c
python -m draftopt.phase2.outcome_coverage_p22c

# Actual-PPR Δ (baseline vs structural) — modeled opponents; n=1 season
python -m draftopt.phase2.delta_p22c --slots 1-12 --n-sims 5

# Mechanism audit + ADP-feasible ladder
python -m draftopt.phase2.diagnose_delta_p22c --slots 1-12 --n-sims 5
python -m draftopt.phase2.feasible_ladder_p22c --slots 1-12 --n-sims 5

# C−B valuation mechanism (offline from ladder JSON; no re-sim)
python -m draftopt.phase2.diagnose_valuation_p22c

# Left-tail loss-case inspection (replays worst C−B pairs only)
python -m draftopt.phase2.inspect_loss_cases_p22c

# Best-10 + closeout (symmetry + fork prediction-error table)
python -m draftopt.phase2.closeout_p22c
```

Scoring contract: [`PHASE2_P22C_SCORING_CONTRACT_ppr_eval_v1_2024.md`](PHASE2_P22C_SCORING_CONTRACT_ppr_eval_v1_2024.md)
