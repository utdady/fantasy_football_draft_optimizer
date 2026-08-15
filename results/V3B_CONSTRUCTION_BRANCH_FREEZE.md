# V3-B construction branch freeze (post B.1)

**Status:** frozen **research pause** — no B.1.1, no new construction code, no
ladder, until a *separate* design revision explicitly chooses one remaining
hypothesis and names one operationalization.

**Checkpoint:** `6355ab9` (B.1 implementation + inert 60-board result)

**Production UI:** remains raw **`marginal`**.  
**`evaluable`:** **0**

**Parents:**

- B.1 ladder [`phase2_v3b1_ladder.md`](phase2_v3b1_ladder.md) (`6355ab9`)
- B.1 operationalization [`V3B_CROSS_POSITION_OPERATIONALIZATION.md`](V3B_CROSS_POSITION_OPERATIONALIZATION.md) (`bfa9840`)
- Cross-pos hypothesis [`V3B_CROSS_POSITION_HYPOTHESIS.md`](V3B_CROSS_POSITION_HYPOTHESIS.md) (`e96ba69`)
- B.0 failure audit [`phase2_v3b0_failure_audit.md`](phase2_v3b0_failure_audit.md) (`b668076`)
- V3-A map `adp_emp_pos_v1_train_2021_2023` (frozen)

---

## 1. Narrow finding (do not over-read)

**B.1 did not fail by producing worse drafts. It failed by producing the exact
same drafts as D.**

Proxy:

\[
M_{B1}(p) = M_D(p) - v(a^*(p))
\]

(`crosspos_empty_need_nextbest_v1`)

- Numerical scores changed.
- **Argmax never changed** on any of the 60 boards.
- B.1−D ≡ 0 (mean / median / p10); WR = 0% as 60 ties; pick sequences identical.

So the claim that is **not supported** is only:

> A current-state cross-position opportunity cost **in this minimal form**
> (\(M_D - v(a^*)\)) is enough to translate calibrated values into
> different/better construction decisions.

**Not established by B.1:** “myopic construction is impossible” or “cross-position
opportunity cost as a whole is false.”

Because policy ≡ D, do **not** audit B.1 tails / positions / rounds as evidence
about the proxy — those would be artifacts of D.

---

## 2. Established progression

| Experiment | Result | What it tells us |
| --- | --- | --- |
| V3-A | Mean ↑, left tail worsened | Calibration improved player valuation; construction translated it poorly |
| V3-B.0 | E−D −24.3, 42% WR, p10 −204 | Simple same-position \(M_D - r^*\) falsified |
| V3-B.0 audit | WR allocation / cascade | Cross-position / state interaction suspected |
| **V3-B.1** | **Identical to D** | Minimal current-state \(M_D - v(a^*)\) is **policy-inert** |

Two intuitive construction fixes eliminated **without** iterative magnitude /
second-best / weight / λ tuning.

---

## 3. Remaining design space (named, not licensed)

At least two conceptually distinct branches remain. **Neither is validated.
Neither may be implemented opportunistically.**

### Branch A — another myopic construction signal

Compare decision-time marginals of the candidate and the best cross-need
alternative (same current remaining pool / \(N(R)\) spirit), e.g.:

\[
M_D(p) - M_D(q^*)
\]

rather than subtracting calibrated player value \(v(q^*)\).

Still myopic. Still current-state. Different signal than B.1.

### Branch B — state-dependent / lookahead construction

Opportunity cost depends on how today’s pick changes **future** roster states
(not merely currently open capacity).

Scientifically justified for *design consideration* because simpler myopic
proxies (B.0 same-pos; B.1 \(v(a^*)\)) have been tested — **not** because a
smarter optimizer is desired, and **not** as automatic V2 resurrection.

---

## 4. Explicitly not established

- Cross-position opportunity cost as a whole
- Marginal-vs-marginal cross-position comparison (Branch A)
- Lookahead / state-dependent construction (Branch B)
- Any particular V3-B formula beyond the two falsified/inert proxies

---

## 5. Hard freeze (this branch)

**Forbidden until a new gated design revision:**

- B.1.1 / retuning \(a^*\) magnitude
- Multiplying \(a^*\)
- Second-best / third-best alternatives as “the next try”
- Position weights / Allen–WR special cases
- λ / CVaR
- Reopening V3-A map or values
- Assuming the answer is “V2” without choosing Branch A vs B in writing

**Baseline for any future construction experiment:** **D** (`adp_v3a`), not C.
Do not reintroduce feasibility contamination from C−A / C−B comparisons into the
construction contrast.

---

## 6. Resume gate (when deliberately opened)

Next artifact must:

1. **Choose** Branch A or Branch B (or name a third, equally explicit claim).
2. Freeze **information boundary** (what is legal at pick time).
3. Name **one** operationalization (construction id + formula).
4. Freeze falsification: primary contrast **new − D**; mean / median / WR / **p10**.
5. Implement → smoke → 60-board → **stop** (no retune after 2024 Δ).

Same treatment as B.0 and B.1. No opportunistic search.

---

## 7. Status board (frozen here)

| Layer | Status |
| --- | --- |
| Core thesis | 🟡 preliminary support |
| V3-A | 🟡 calibration success / construction tradeoff — **map frozen** |
| V3-B.0 | ❌ simple positional replacement falsified |
| V3-B.1 | ❌ inert; no policy change (`6355ab9`) |
| Construction | Mechanism narrowed, **not solved** |
| Branch A (myopic \(M_D - M_D(q^*)\)) | 🟡 named only — not opened |
| Branch B (lookahead / state-dependent) | 🟡 newly justified for design consideration — not opened |
| UI | `marginal` |
| `evaluable` | **0** |

---

## 8. One-sentence freeze

> **B.1 established only that \(M_D - v(a^*)\) was policy-inert vs D; freeze
> construction work here with two named remaining hypotheses (marginal-vs-marginal
> myopic vs state-dependent/lookahead); any resume must pick one, contract it,
> and judge new−D without retuning.**
