# V3-A calibration design (frozen contract)

**Status:** frozen design checkpoint — **no V3-A strategy / materialize / eval**
until this note is revised or the implementation gate below is checked off.

**Production UI:** remains raw **`marginal`**.

**Parents:** Phase-2 closeout
[`phase2_p22c_closeout.md`](phase2_p22c_closeout.md) ·
track [`PHASE2_P22C_ADP_STRUCTURAL.md`](PHASE2_P22C_ADP_STRUCTURAL.md) ·
curve freeze [`../src/draftopt/phase2/adp_value_curve.py`](../src/draftopt/phase2/adp_value_curve.py)

**Philosophical closer:**

> Improve the decision-time value signal while leaving roster construction
> completely unchanged. Calibration must be a pure transformation of
> decision-time information. It must not have access to outcomes.

---

## 1. Hypothesis

Phase-2 showed preliminary support for construction/valuation over
ADP-feasible drafting (C−B), with left-tail losses localized to mid-draft
forks. Closeout showed skill-over-QB forks are **symmetric** across best/worst
tails (not a positional rule), while fork prediction errors point at
**miscalibration** of the ADP→value curve relative to realized PPR.

**V3-A hypothesis:**

> The structural optimizer’s realized losses are partly caused by systematic
> miscalibration of its preseason player-value signal. A calibration layer that
> improves the relationship between decision-time value and realized fantasy
> points should improve C−B performance **without changing roster construction**.

Name: **calibration-adjusted valuation** — **not** “historical ESPN/FP
projections” (P2.2B closed; no dated 2024 proj source confirmed).

Do **not** design V3-A as “take fewer TEs,” “add QB scarcity,” V2 survival, or
CVaR. Those optimize symptoms or a different research branch.

---

## 2. Leakage boundary (hard rule)

```text
                    frozen snapshot
                          │
             ┌────────────┴────────────┐
             │                         │
          ADP/value                 outcomes
             │                         │
       calibration                   │
             │                         │
             ▼                         │
       calibrated value               │
             │                         │
             └──────► construction ◄──┘
                         │
                         ▼
                    actual PPR
```

- Calibration and `recommend()` **must not** read `eval_outcomes`,
  `eval_outcome_status`, or any actual-PPR table.
- Outcomes remain **downstream** of drafting — used only for scoring.
- Same leakage boundary as P2.1+.

**Allowed inputs** (must be demonstrably available at the frozen decision
timestamp):

- ADP
- position
- draftable-player pool
- team/player metadata available then
- any explicitly documented preseason signal available then
- **for fit only:** prior-season ADP + prior-season outcomes (train years ≠ eval year)

**Forbidden:**

- evaluation-season actual fantasy points (e.g. 2024 when scoring 2024)
- post-draft / in-season stats for the eval season
- hindsight-derived player tiers
- fitting calibration parameters on the evaluation season

---

## 3. Ablation ladder (evaluation)

Keep the Phase-2 environment fixed:

| Field | Value |
| --- | --- |
| Snapshot | `2024-preseason-2024-09-01-ffc12` |
| League | 12-team FFC PPR snake |
| Roster | `league_default` |
| Opponents | modeled `noisy_adp` |
| Seeds / slots | same as C−B ladder (slots 1–12 × 5 sims, seed0=42 unless re-registered) |
| Scoring | `ppr_eval_v1_2024` |
| Feasibility baseline | `adp_feasible` |

| Label | Strategy | Value signal | Construction |
| --- | --- | --- | --- |
| A | `adp_baseline` | ADP order | none |
| B | `adp_feasible` | ADP + starter feasibility | none |
| C | `adp_structural` | frozen `adp_linear_v1_2024_ffc12` | V1 marginal (unchanged) |
| D | `adp_v3a` | **calibrated signal only** | **same** V1 marginal |

**Load-bearing comparisons:**

- **D−B** — calibrated valuation vs feasibility baseline (parallel to C−B)
- **D−C** — does calibration improve the existing structural signal?

Also report: mean, median, win rate, SD, p10/p25/p75/p90, negative-draft rate,
position × round, draft slot. Do **not** optimize the mean alone.

Honesty bar: FFC ≠ ESPN · 12 ≠ 10 · calibrated ADP map ≠ ESPN `proj_ppr` ·
`evaluable` stays 0 until a separate gate says otherwise.

**Do not retune** `adp_linear_v1_2024_ffc12` in place. Curve C stays frozen forever.

---

## 4. Concrete first transform: V3-A.0

**V3-A.0 — positional empirical ADP→PPR map fit on pre-2024 seasons only.**

| Step | Spec |
| --- | --- |
| Train years | **2021–2023** (contiguous; freeze list before fit) |
| Pairing | decision-time ADP × that season’s actual PPR (nflverse / existing outcome pipeline) |
| Fit | per-position **monotone** map `ADP → E[PPR \| ADP, pos]` via **binned means + isotonic regression** (one method; freeze after first fit) |
| Apply | map **2024** FFC ADP → calibrated `season_points` |
| Identity | new immutable `curve_id`, e.g. `adp_emp_pos_v1_train_2021_2023` |

**Plumbing intent (implementation PR, not this note):**

- Materialize calibrated values analogous to
  [`adp_value_curve.py`](../src/draftopt/phase2/adp_value_curve.py) /
  [`materialize_p22c.py`](../src/draftopt/phase2/materialize_p22c.py)
- Strategy label `adp_v3a` reuses the same marginal construction as
  `adp_structural` (`MarginalValueStrategy` / structural wrapper) against the
  new projection rows — **no** change to `lineup_ev`, feasibility, or V2

**Prerequisite (blocks implementation):**

Dated pre-2024 ADP snapshots must exist (or be acquired) with documented
provenance and as-of dates. If unavailable, **implementation is blocked** —
do not invent ADP from outcomes.

**Forbidden transforms:**

- Fit any parameter using 2024 actuals
- QB/TE positional bans or “stop skill-over-QB” rules
- V2 / risk / λ / CVaR
- Changing feasibility or `lineup_ev`

---

## 5. Falsification

V3-A is **unsuccessful** if any of:

1. **D−B** does not improve over **C−B** in a pre-registered way (mean **and**
   distribution/tail — not mean alone).
2. Gains are confined to one arbitrary pocket (one slot / round / position).
3. It requires hindsight or evaluation-season outcomes.
4. It only works when retuned to the evaluation season.
5. It uses information unavailable at the frozen decision timestamp.

**Eventual standard:** multi-season validation
(2023 preseason → 2023 outcomes; 2024 → 2024; …), each snapshot frozen
independently. V3-A is not judged solely by “wins 2024.”

---

## 6. Explicit non-goals

- New V2-alpha / V2-beta / `robust_min` work
- λ / CVaR / neural projection models
- Changing production UI default away from `marginal`
- Claiming `evaluable=1` from a single 2024 labeled ablation
- Calling V3-A “ESPN projections” or undoing P2.2B honesty
- A giant “calibration framework” — **one transformation, one hypothesis,
  one comparison**

---

## 7. Implementation gate (later PR)

Do not start coding until:

1. [x] Train years frozen (default 2021–2023) and documented
2. [x] Pre-2024 ADP provenance + as-of dates recorded
   ([`phase2_v3a_gate1_adp_provenance.md`](phase2_v3a_gate1_adp_provenance.md))
3. [x] Fit method frozen (binned means + isotonic); `curve_id` assigned
   ([`phase2_v3a_gate3_calibration_freeze.md`](phase2_v3a_gate3_calibration_freeze.md))
4. [x] Train outcomes coverage green
   ([`phase2_v3a_gate2_train_outcomes.md`](phase2_v3a_gate2_train_outcomes.md))
5. [x] Leakage constraints audited (design)
   ([`phase2_v3a_gate4_leakage_audit.md`](phase2_v3a_gate4_leakage_audit.md))
6. [ ] Materialize D into draft DB without touching C’s curve constants
7. [ ] Register `adp_v3a` (construction identical to structural)
8. [ ] Same-board ladder: A/B/C/D; report D−B and D−C
9. [ ] Results artifact + falsification checklist filled

Gates **1–4 (design) are green.** Remaining items are the implementation PR.

Sequence: **design freeze → Gates 1–4 → smallest V3-A.0 implementation →
same-board actual-PPR evaluation.**

---

## Status line

> **Core thesis: 🟡 preliminary empirical support.**
> **V3-A: 🟢 hypothesis earned / 🔴 implementation pending (design frozen).**
> **External validity: 🔴.**
> **Production UI: `marginal`.**
> **`evaluable=0`.**
