# Phase 2 / V3-B closeout

**Status:** terminal documentation checkpoint — **no further V3-B experiments**.  
**Construction-branch falsification checkpoint:** `6ad702b`  
**Production UI:** raw **`marginal`**. · **`evaluable`:** **0**

This closes the **entire licensed V3-B program** (B.0 → B.1 → A → B), not only Branch B.

---

## 1. What was tested

| Experiment | Construction | Result vs D (`adp_v3a`) | Reading |
| --- | --- | --- | --- |
| **B.0** | Same-pos replacement `M_D − r*` | E−D **−24.3**, 42% WR | Harmful |
| **B.1** | Current-state cross-pos value `M_D − v(a*)` | **0/60** pick changes; Δ≡0 | Policy-inert |
| **A** | Cross-pos marginal `M_D(p) − M_D(q*)` | **0/60**; 900/900 top1 = D | Structurally near-inert |
| **B** | One-step state-dep. `M_D(p\|R) + C(R∪{p})` | **60/60** diverge; mean B−D **−57.5**, WR **37%** | Policy-active but harmful |

Primary artifacts:

- B.0: `phase2_v3b_ladder.md` / `phase2_v3b0_failure_audit.md` (`b668076`)
- B.1: `phase2_v3b1_ladder.md` (`6355ab9`)
- A: `phase2_v3ba_ladder.md` / `V3B_A_STRUCTURAL_POSTMORTEM.md` (`0924d17`)
- B: `phase2_v3bb_ladder.md` / `phase2_v3bb_mechanism_audit.md` (`6ad702b`)

Design spine: `V3B_CONSTRUCTION_BRANCH_FREEZE.md` → `V3B_BRANCH_SELECTION.md` → A/B contracts.

**There was no Branch C.** The frozen menu ended at B.

---

## 2. What this establishes

**Not established:** “Construction doesn’t matter.”

**Established:**

> **None of the licensed construction hypotheses provided evidence that modifying
> frozen V3-A construction improves 2024 starter PPR relative to D.**

Each failure was **mechanism-diagnosed**, not a shrug at a bad mean:

| Branch | Mechanism |
| --- | --- |
| B.0 | Same-pos replacement reallocates poorly (WR cascade) |
| B.1 | Subtractand never moves argmax |
| A | Affine / incumbent-protecting shape → structurally near-inert |
| B | Empty-roster R1: \(M_B \approx M_D(p)+M_D(\text{best other})\) near-ties QB/WR; **QB→WR on 60/60**; ADP tie-break prefers WR; outcomes worse |

Gates P∧N passed for B — the hypothesis **was expressed**; the policy changed on every board and lost. That is a clean falsification of this operationalization, not an implementation miss.

---

## 3. V3-A is a separate axis (do not conflate)

Closing V3-B does **not** falsify V3-A calibration, and does **not** leave “better values + existing construction” untested.

| Axis | Status | Evidence |
| --- | --- | --- |
| **Player calibration** | 🟡 Supported / frozen | Train MAE ~87.8→54.3; gates + leakage audit (`cd1b03c`) |
| **Calibrated values under frozen structural construction** | 🟡 Tradeoff / frozen | **D−C already run:** mean **+22.1**, WR **55%**, p10 **−268** (`phase2_v3a_ladder.md`, mechanism audit) |
| **Construction modifications on top of D** | 🔴 Closed with this doc | B.0 / B.1 / A / B |

**D** = `adp_v3a` = V3-A map as `season_points` + **same** marginal construction as C (`adp_structural`).  
Re-running “calibrated input vs structural” under a new name is **not** unfinished business.

V3-A remains a **frozen instrument and control baseline (D)**. It is **not** a production ship decision and **not** permission to retune the map from construction failures.

---

## 4. What remains unresolved (questions, not authorized runs)

- Whether some **other** construction hypothesis (outside this menu) could beat D.
- Whether the V3-A calibration relationship **generalizes** beyond the 2024 eval environment.
- Whether player-level calibration gains survive further out-of-sample checks.
- Whether the original construction thesis is worth a **new** research program at all.

These are open scientific questions. **None** are licensed experiments under V3-B.

---

## 5. Explicitly closed escape hatches (not V3-B follow-ups)

Forbidden as “next tries” within this program:

- Scaling / weighting \(C\) (e.g. \(C/2\))
- Tuning replacement or OC magnitude
- λ / CVaR
- Horizon expansion / multi-round lookahead
- Resurrecting V2
- QB/WR-specific penalties or position special cases
- Retuning the V3-A map from 2024 Δ
- Selecting a favorable subset of the 60 boards
- Optimizing against 2024 outcomes / cherry-picking contracts

Failure → tweak → rerun is **out of scope**. Checkpoint `6ad702b` is terminal for licensed construction work.

---

## 6. Status board (authoritative after this closeout)

| Layer | Status |
| --- | --- |
| Phase 2 thesis (C−B after feasibility + DST) | 🟡 preliminary empirical support |
| V3-A calibration (player-level) | 🟡 supported / frozen |
| V3-A under frozen construction (D−C) | 🟡 tradeoff / frozen |
| **V3-B construction program** | 🔴 **closed** (`6ad702b`) |
| External validity | 🔴 untested |
| V3 implementation beyond frozen D | 🔴 not justified |
| UI | `marginal` |
| `evaluable` | **0** |

---

## 7. Two legitimate paths from here

1. **Freeze V3 and stop** — reproducible Phase-2 chain; frozen calibration instrument; documented failed construction menu; UI stays `marginal`. **Preferred default after this closeout.**
2. **Open a new research family later** — requires a **new hypothesis**, information boundary, and independent design contract. Not a lettered continuation of V3-B. Not “B lost, try something else.”

Do **not** immediately open another algorithm experiment. The next useful question is what was learned, not what to try next.

---

## 8. One-sentence closeout

> **V3-B is closed:** licensed myopic and one-step construction corrections were inert or harmful against frozen V3-A valuation (D); V3-A calibration remains a separate supported/frozen tradeoff (D−C); no construction retune is authorized; any future construction work needs a new hypothesis family.
