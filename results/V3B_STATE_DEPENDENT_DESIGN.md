# V3-B Branch B — one-step state-dependent design (frozen)

**Status:** frozen **design / operationalization contract**.  
Gates P∧N **passed**; 60-board B−D **ran** → **active but falsified** (mean B−D −57.5).  
See `phase2_v3bb_ladder.md` + `phase2_v3bb_mechanism_audit.md`. No B.1.1 / horizon↑ / λ.

**Not V2.** Not multi-round lookahead. Not opponent simulation.

**Parents:**

- Branch A structural postmortem [`V3B_A_STRUCTURAL_POSTMORTEM.md`](V3B_A_STRUCTURAL_POSTMORTEM.md) (`0924d17`)
- Branch selection [`V3B_BRANCH_SELECTION.md`](V3B_BRANCH_SELECTION.md) (`3465c06`)
- Branch freeze [`V3B_CONSTRUCTION_BRANCH_FREEZE.md`](V3B_CONSTRUCTION_BRANCH_FREEZE.md) (`cfc49b9`)
- Control D / map `adp_v3a` · `adp_emp_pos_v1_train_2021_2023` (frozen)

**Production UI:** remains raw **`marginal`**.  
**`evaluable`:** **0**

---

## 1. Exact claim

> **Branch B hypothesis:** Candidate-induced **next roster state** carries
> construction information that **current-state** marginal valuation cannot
> express. A minimal **one-step** continuation after \(R'=T(R,p)\) can change
> relative rankings vs D for that reason — not because lookahead is “clever.”

We are **not** testing whether multi-horizon / survival / V2 machinery helps.

---

## 2. Why B is licensed (after A)

| Experiment | Result | Lesson |
| --- | --- | --- |
| B.0 | Harmful | Static same-pos replacement insufficient |
| B.1 | Policy-inert | Current-state \(v(q^*)\) subtraction inert |
| Branch A | **Structurally near-inert** (900/900 A=D) | Current-state \(M_D(q^*)\) / trivial-shift shapes do not re-rank |
| **Branch B** | **Not tested** | First hypothesis that **requires** \(OC\) to depend on **state induced by choosing \(p\)** |

A did **not** falsify opportunity cost as a concept. B must correct A’s defect.

---

## 3. Hard capability requirement

> **B must permit two candidates at different positions to change relative
> ranking because of the roster state induced by choosing each.**

Insufficient by itself:

\[
M(p) = M_D(p) - OC(p \mid R_{\mathrm{current}})
\]

when \(OC\) is attached only to \(p\)’s current position / current pool in a way
that is constant, position-local, or incumbent-protecting (A’s failure mode).

Required shape:

\[
R' = T(R, p), \qquad OC_B(p) = OC_B(R')
\]

with \(OC_B(p) \neq OC_B(q)\) when \(T(R,p)\) and \(T(R,q)\) differ enough that
continuations differ.

---

## 4. One-step state transition

For each candidate \(p\) at decision time:

1. **Current state** \(R\): user roster counts / drafted set; remaining pool \(S\).
2. **Transition** \(R' = T(R,p) := R \cup \{p\}\), \(S' = S \setminus \{p\}\).
3. **One subsequent decision state only:** evaluate a scalar continuation on
   \((R', S')\) — **not** a multi-round tree, **not** opponent picks, **not**
   simulated future boards.

Horizon hard stop: **one** continuation evaluation after \(T\). If one-step
fails, **stop and reassess** — do not automatically increase horizon.

---

## 5. One formula (frozen operationalization)

**Construction id:** `onestep_continuation_marginal_v1`  
**Suggested strategy name:** `adp_v3bb` (Branch B)

**Base (unchanged from D):**

\[
M_D(x \mid R) = L(R \cup \{x\}) - L(R)
\]

same `MarginalValueStrategy` / `adp_v3a` path (frozen V3-A values).

**Continuation in the induced state:**

\[
C(R') = \max_{q \in S'} M_D(q \mid R')
\]

i.e. the best next-pick marginal under D’s scorer given roster \(R'\) and
remaining pool \(S'\) (same ranking inputs/tie-breaks as D). If \(S'=\emptyset\)
or no candidate has a defined marginal, \(C(R')=0\) and flag
`continuation_missing=true`.

**Branch B score:**

\[
M_B(p) = M_D(p \mid R) + C(R \cup \{p\})
\]

Rank by \(M_B\) descending; tie-breaks identical to D.

### What this can say

> Taking \(p\) yields immediate marginal \(M_D(p\mid R)\) **plus** the best
> immediate next marginal available **after** the roster slot/capacity change
> that \(p\) induces.

### What this must not say

- Current-state cross-pos \(v(q^*)\) or \(M_D(q^*)\) subtraction (B.1 / A).
- Multi-step “value of waiting N rounds.”
- Survival / opponent ADP trajectories / V2 mix.

### Why this escapes A’s affine trap

\(C(R\cup\{p\})\) generally **depends on which position/slot \(p\) filled**.
Two candidates with similar \(M_D(\cdot\mid R)\) can get different continuations,
so relative order **can** reverse. That is the structural requirement A failed.

---

## 6. Explicit forbids (A / B.1 failure modes + scope)

**Forbidden score shapes / machinery:**

| Forbid | Why |
| --- | --- |
| \(M_D(p) - c(\mathrm{position})\) | Position constant = hidden trivial shift |
| \(M_D(p) - v(q^*)\) with \(q^*\) in **current** state | B.1 |
| \(M_D(p) - M_D(q^*)\) with \(q^*\) in **current** state | Branch A |
| Any **candidate-independent** subtraction/addition | Pure affine → inert |
| Rules that **protect the incumbent** merely for having max current \(M_D\) | A’s mechanism |
| 2024 **actual** PPR / outcomes in recommend | Leakage |
| Multi-round lookahead / recursive \(C\) beyond one step | Scope creep → V2 family |
| Opponent simulation / noisy future boards inside \(C\) | V2 / survival family |
| λ / CVaR / map retune / positional penalties | Out of contract |

**Allowed:** current \(R\), \(S\), frozen V3-A values, \(M_D(\cdot\mid R)\) and
\(M_D(\cdot\mid R')\) via the same EV path as D, deterministic \(T(R,p)\).

---

## 7. Information boundary

| Admissible | Forbidden |
| --- | --- |
| Current roster / remaining pool | Future opponent picks |
| Frozen calibrated projections | Actual PPR / eval outcomes |
| One-step \(R'=T(R,p)\) | Multi-round simulated boards |
| \(M_D\) under \(R\) and under \(R'\) | Hindsight / post-draft info |

Baseline for contrasts: **D** only (not C).

---

## 8. Synthetic policy-sensitivity gates (required before any 60-board run)

Both gates are **non-negotiable** after Branch A. Fail either → reject this
operationalization; **do not** run the real ladder; **do not** invent B.1.1
by tweaking weights.

### Gate P — positive control (capability)

Construct a tiny synthetic state where:

- Under D: candidate \(A \succ B\) (different positions).
- \(T(R,A)\) and \(T(R,B)\) yield different next-state continuations \(C\).
- The continuation gap is large enough that \(M_B\) **can** reverse to \(B \succ A\).

**Pass:** implementation’s \(M_B\) ranks \(B\) above \(A\) on that fixture.  
**Fail:** cannot reverse → still structurally inert / wrong formula → stop.

### Gate N — negative control (not noise)

Construct a synthetic state where top candidates induce **no meaningful**
next-state OC difference (continuations equal or gap too small to justify a
flip under the frozen formula), and D’s order should be preserved.

**Pass:** \(M_B\) does **not** spuriously reverse D’s order.  
**Fail:** noisy / unstable reordering → reject before real boards.

| Gate | Proves |
| --- | --- |
| P | B **can** differ from D when state-induced OC says it should |
| N | That capability is **not** just arbitrary flip noise |

---

## 9. Real evaluation (only after Gates P & N)

**Primary contrast:** **B − D**

| Lock | Value |
| --- | --- |
| Boards | Same 60 `(slot, seed)` (slots 1–12 × 5, seed0=42) |
| Opponents | `noisy_adp` |
| DB / values | Frozen V3-A decision DB |
| Scoring | `ppr_eval_v1_2024` |
| `evaluable` | **0** |
| Metrics | mean, median, WR, **p10**, **boards with ≥1 changed pick**, total changed picks |
| Retune | **None** after seeing 2024 Δ |

### Stop / classify

| Outcome | Reading | Next |
| --- | --- | --- |
| 0/60 pick changes | Still policy-inert | Stop; reassess hypothesis (do **not** auto-lengthen horizon) |
| Pick changes + B−D ≤ 0 | Falsified as useful construction | Freeze; no tune; optional light pick-trace only |
| Pick changes + B−D positive (predeclared) | **Provisional only** | **Mandatory mechanism audit** before any claim that state-dependent OC “worked”; no B.1.1; no horizon expansion |

### Mandatory mechanism audit (even when B−D looks good)

**Mechanism audit is not a consolation prize for a disappointing ladder.**  
A flattering mean/WR/p10 does **not** skip this step.

After any B−D with ≥1 pick-change board (and **especially** when B−D > 0), before
interpreting the result as evidence for candidate-induced state-dependent OC,
document at least:

1. **Where** B diverges from D — round-band histogram; first-divergence round.
2. **What** flips — position pairs at first fork (D→B); roster-count Δ if useful.
3. **Concentration** — whether positive Δ mass is mega-concentrated in a few boards
   (same discipline as V3-A / Branch A postmortems).
4. **Sanity vs Gates** — divergences should be plausibly tied to different
   continuations \(C(R')\), not unexplained noise (Gate N’s spirit on real boards).

If the audit shows divergences cluster in a mechanistically uninteresting way
(e.g. almost only R1–R2 with no state-induced story, or a single position pair
dominating), **do not** promote B to “OC validated” — record the finding and stop.

**Still forbidden after a positive B−D:** weighting \(C\), lengthening horizon,
λ/CVaR, map retune, resurrecting V2.

---

## 10. Implementation gate checklist

- [x] Branch A read as structurally near-inert (`0924d17`)
- [x] Claim: candidate-induced one-step state vs current-state marginal
- [x] \(R'=T(R,p)\); one-step only
- [x] Formula \(M_B = M_D(p\mid R) + C(R\cup\{p\})\) named
- [x] Forbids (A/B.1 shapes, outcomes, multi-round, V2) listed
- [x] Gates P + N specified
- [x] B−D metrics + stop rules frozen
- [x] **Mandatory mechanism audit on positive B−D** (where/why; not optional)
- [x] Unit tests for \(T\), \(C\), formula, forbids
- [x] Synthetic Gate P pass
- [x] Synthetic Gate N pass
- [x] Strategy `adp_v3bb` (only if P∧N)
- [x] Smoke vs D
- [x] 60-board B−D; report; **stop**
- [x] Mechanism audit if any pick changes (required if B−D > 0)
  - Done as **light** where/why: B−D ≤ 0 → falsified; see `phase2_v3bb_mechanism_audit.md`

---

## 11. Status board

| Layer | Status |
| --- | --- |
| Branch B design | 🟢 **frozen here** |
| Branch B implementation | ❌ **active + falsified** (60/60 diverge; mean B−D −57.5; R1 QB→WR) |
| Branch A | ❌ structurally near-inert |
| V2 / multi-round | 🔴 frozen (not this experiment) |
| UI | `marginal` · `evaluable=0` |

---

## 12. One-sentence contract

> **Branch B ranks by immediate \(M_D(p\mid R)\) plus the best next-pick \(M_D\)
> in the roster state after taking \(p\) (one step only); it must pass synthetic
> reversal and negative-control gates before any B−D ladder; forbids current-state
> \(q^*\) subtraction and V2 machinery; judge B−D with pick-change metrics; a
> positive B−D still requires a mandatory where/why mechanism audit before any
> OC claim; no retune / no horizon expansion.**
