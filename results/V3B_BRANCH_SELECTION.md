# V3-B branch selection (frozen decision)

**Status:** frozen **branch-selection** checkpoint — **no A strategy / ladder /
formula operationalization code** until a separate A operationalization contract
is opened. This document only chooses *which* hypothesis is next.

**Parents:**

- Branch freeze [`V3B_CONSTRUCTION_BRANCH_FREEZE.md`](V3B_CONSTRUCTION_BRANCH_FREEZE.md) (`cfc49b9`)
- B.1 inert result [`phase2_v3b1_ladder.md`](phase2_v3b1_ladder.md) (`6355ab9`)
- B.1 operationalization [`V3B_CROSS_POSITION_OPERATIONALIZATION.md`](V3B_CROSS_POSITION_OPERATIONALIZATION.md)
- B.0 falsified [`phase2_v3b_ladder.md`](phase2_v3b_ladder.md) / audit (`b668076`)
- V3-A map `adp_emp_pos_v1_train_2021_2023` (frozen)

**Production UI:** remains raw **`marginal`**.  
**`evaluable`:** **0**

---

## 1. Decision (locked)

> **Branch A selected:** test cross-position **marginal-vs-marginal** opportunity
> cost as the final low-complexity myopic construction hypothesis.
> **Branch B is deferred** until A is falsified (or shown policy-inert).

This is a **research decision**, not an intuition smuggled into code.

**Sequence from here:**

`cfc49b9` → **this doc (frozen)** → A operationalization contract → freeze →
A implementation → A−D test → **stop**.

**No A code before the A operationalization contract exists.**

---

## 2. Evidence map (research status)

| Experiment | Question | Result | Status |
| --- | --- | --- | --- |
| C−B | Does structural valuation beat feasible ADP? | +76.5 mean / 67% WR | Support |
| V3-A | Does calibration improve player valuation? | MAE 87.8 → 54.3 | Support |
| V3-A | Does calibration improve construction? | Mean ↑, left tail worse | Mixed / tradeoff |
| B.0 | Is same-pos \(M_D - r^*\) sufficient? | −24.3 / 42% WR / p10 −204 | ❌ Falsified |
| B.1 | Is \(M_D - v(a^*)\) sufficient? | 0 policy changes (Δ≡0) | ❌ Policy-inert |
| **A** | Cross-pos **marginal** OC \(M_D(p)-M_D(q^*)\)? | 0/60 pick changes; 900/900 top1 match | ❌ **Structurally near-inert** (not a strong OC kill) |
| **B** | One-step state-dependent construction? | 60/60 diverge; mean B−D −57.5; R1 QB→WR | ❌ **Active but falsified** (`6ad702b`); program closed [`PHASE2_V3B_CLOSEOUT.md`](PHASE2_V3B_CLOSEOUT.md) |

---

## 3. The two surviving hypotheses

### Branch A — cross-position marginal comparison (selected)

B.1 asked: *how valuable is the alternative player?*

\[
M_{B1}(p) = M_D(p) - v(q^*)
\]

Branch A asks: *how much lineup value would I gain by taking the alternative
instead?*

\[
M_A(p) = M_D(p) - M_D(q^*)
\]

where \(q^*\) is the best currently available player serving a **different**
open starter/FLEX need (precise \(q^*\) locked only in the A operationalization
contract — not invented here beyond the claim).

| Property | |
| --- | --- |
| Uses only current state? | ✅ |
| Conceptual complexity | Low |
| Distinguishes B.1's failure? | ✅ (different subtractand: \(M_D\) vs \(v\)) |
| Risk of recreating V2? | Low |
| Cheap to falsify? | Very |
| Explains late WR cascade? | Maybe |

**Still myopic.** Still decision-time only.

### Branch B — one-step state-dependent OC (deferred)

Opportunity cost depends on how today's pick changes **future** roster
possibilities — not merely currently open capacity.

**Explicit naming (hard):**

> **One-step state-dependent opportunity cost** — **not** “bring V2 back.”

| Property | |
| --- | --- |
| Uses only current state? | ❌ (uses a minimal future-state signal) |
| Conceptual complexity | Higher |
| Distinguishes B.1's failure? | ✅ |
| Risk of recreating V2? | High if undisciplined |
| Cheap to falsify? | Moderate |
| Explains late WR cascade? | More naturally |

Deferred until A's switch conditions fire. When opened, Branch B gets its own
hypothesis → information boundary → one operationalization → freeze → test →
stop. No survival/λ/CVaR resurrection by default.

---

## 4. Why A before B (decision rule)

B.1 falsified only \(M_D - v(a^*)\). That does **not** exhaust the myopic
construction hypothesis. Branch A is the last cheap, clearly distinct myopic
test. Preferring B now would convert two failed minimal proxies into “therefore
lookahead” without testing the remaining myopic signal.

**Information-value comparison (frozen):**

| Question | Branch A | Branch B |
| --- | --- | --- |
| Uses only current state? | ✅ | ❌ |
| New conceptual complexity | Low | High |
| Can distinguish B.1's failure? | ✅ | ✅ |
| Risks recreating V2? | Low | High |
| Cheap to falsify? | **Very** | Moderate |
| Explains late WR cascade? | Maybe | More naturally |
| Should be tested first? | **Yes — selected** | Later |

---

## 5. A experiment contract (locks for the next operationalization)

When A is operationalized and implemented, the following are **pre-frozen**:

| Lock | Value |
| --- | --- |
| Formula | One fixed \(M_A\); **no tuning** after seeing 2024 Δ |
| \(q^*\) | Precisely defined from **current** roster + remaining pool only |
| Information | Decision-time state only; **no** outcomes; **no** future boards |
| Baseline | **D** (`adp_v3a`); V3-A calibrated values **unchanged** |
| Boards | Same 60 `(slot, seed)` pairs; same opponents (`noisy_adp`) |
| Scoring | `ppr_eval_v1_2024` |
| Primary contrast | **A − D** |
| Metrics | mean, median, WR, **p10** |
| **New metric** | **Number of boards with ≥1 changed pick** (first-class after B.1) |
| Forbidden | B.1.1-style retunes; position weights; λ/CVaR; lookahead; outcome leakage |
| UI | `marginal` · `evaluable=0` |

Exact \(q^*\) / construction id / strategy name:
[`V3B_A_OPERATIONALIZATION.md`](V3B_A_OPERATIONALIZATION.md)
(`crosspos_empty_need_marginal_v1`, \(q^*=\arg\max M_D\)).

---

## 6. Switch conditions (after A ladder — no retune)

| Outcome | Reading | Next |
| --- | --- | --- |
| **0/60** boards with ≥1 pick change | A policy-inert (like B.1) | **Stop A**; open **Branch B design** |
| Pick changes exist but **A−D ≤ 0** (esp. mean/median/WR/p10 fail) | A falsified as useful construction | **Stop A**; open **Branch B design** |
| **A−D** positive (predeclared metrics) | Provisional support | **Mechanism audit first**; do **not** immediately iterate A |

**No B.1.1:** if A is inert or fails, do not multiply, soften, or second-best the
same proxy. Stop and follow the table.

---

## 7. Branch B placeholder (deferred only)

If switch conditions open B:

1. Name **one-step state-dependent opportunity cost** (not V2).
2. Freeze information boundary (what future signal is legal).
3. One operationalization → freeze → implement → **B−D** → stop.

Do not reopen V3-A. Do not compare against C as the construction baseline.

---

## 8. Roadmap (frozen view)

```text
CURRENT
  │
  ├── D: calibrated valuation ─────────────── frozen
  │
  └── Construction problem
          │
          ├── B.0 positional replacement ─── ❌
          │
          ├── B.1 cross-pos value OC ─────── ❌ inert
          │
          └── Branch selection (this doc)
                  │
                  ├── A: cross-pos marginal ── selected next
                  │       │
                  │       └── op contract → test → stop
                  │
                  └── B: one-step state-dep ── deferred
                          │
                          └── design → test → stop
```

Production V3 only after a convincing construction result — not before.

---

## 9. Status board

| Component | Status |
| --- | --- |
| Phase 2 core thesis | 🟡 Preliminary support |
| V3-A calibration | 🟡 Successful valuation / construction tradeoff — **frozen** |
| B.0 | ❌ Falsified |
| B.1 | ❌ Policy-inert |
| Branch A | ❌ **Structurally near-inert** — [`V3B_A_STRUCTURAL_POSTMORTEM.md`](V3B_A_STRUCTURAL_POSTMORTEM.md) |
| Branch B | ❌ **Active but falsified** — [`phase2_v3bb_ladder.md`](phase2_v3bb_ladder.md) (`6ad702b`) |
| V3-B program | 🔴 **Closed** — [`PHASE2_V3B_CLOSEOUT.md`](PHASE2_V3B_CLOSEOUT.md) |
| A / B implementation | A structurally near-inert; B implemented and falsified |
| UI | `marginal` |
| `evaluable` | **0** |

---

## 10. One-sentence freeze

> **Branch A is closed as structurally near-inert; Branch B design is frozen in
> `V3B_STATE_DEPENDENT_DESIGN.md` (one-step \(M_D+C(R')\), Gates P∧N, B−D);
> no B code until synthetic gates pass; no V2 resurrection.**
