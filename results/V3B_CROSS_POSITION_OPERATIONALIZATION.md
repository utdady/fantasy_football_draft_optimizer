# V3-B.1 cross-position operationalization (frozen contract)

**Status:** frozen **operationalization** — one myopic proxy named below.
**No B.1 strategy / ladder / eval code** until the implementation checklist is
checked open. Do not retune after seeing 2024 Δ.

**Production UI:** remains raw **`marginal`**.

**Parents:**

- Hypothesis [`V3B_CROSS_POSITION_HYPOTHESIS.md`](V3B_CROSS_POSITION_HYPOTHESIS.md) (`e96ba69`)
- B.0 failure audit [`phase2_v3b0_failure_audit.md`](phase2_v3b0_failure_audit.md) (`b668076`)
- B.0 construction [`V3B_CONSTRUCTION_DESIGN.md`](V3B_CONSTRUCTION_DESIGN.md) (`cb7a325`)
- Frozen map `adp_emp_pos_v1_train_2021_2023`

**Philosophical closer:**

> The alternative must exist in the **current** draft state. If valuing it
> requires future availability, opponent simulation, or multi-round plans, the
> experiment has left this contract and entered the V2 / lookahead family.

---

## 1. Frozen inputs

| Field | Value |
| --- | --- |
| Values | Identical frozen V3-A calibrated `season_points` (same DB as D / `adp_v3a`) |
| Control D | `adp_v3a` + current empty-slot marginal \(M_D\) |
| Roster | `league_default` (QB/RB/WR/TE/FLEX/DST/K as in production preset) |
| Boards | Same **60** `(slot, seed)` pairs (slots 1–12 × 5, seed0=42) |
| Opponents | modeled `noisy_adp` |
| Scoring | `ppr_eval_v1_2024` |
| `evaluable` | **0** |

**Admissible at pick time:** current user roster counts, current remaining pool,
frozen V3-A values, roster slot template, pick/round index for bookkeeping only.

**Forbidden:** actual PPR, future picks, simulated future boards, survival /
lookahead, λ/CVaR, WR/QB penalties, map retune.

---

## 2. Meaningful alternative allocation (current state only)

### 2.1 Empty starter capacity \(N(R)\)

From the user’s current drafted counts and `league_default` slots, compute
**fixed-slot deficits** (same spirit as `min_starter_picks_needed` / feasibility):

\[
\begin{aligned}
\mathrm{def}(\mathrm{QB}) &= \max(0,\ \mathrm{slots.QB} - \mathrm{count.QB}) \\
\mathrm{def}(\mathrm{RB}) &= \max(0,\ \mathrm{slots.RB} - \mathrm{count.RB}) \\
&\ldots \quad (\mathrm{WR},\mathrm{TE},\mathrm{DST},\mathrm{K})
\end{aligned}
\]

**FLEX capacity remaining:** after assigning extras of RB/WR/TE beyond their
fixed slots toward FLEX (same accounting as `adp_feasible`),

\[
\mathrm{def}(\mathrm{FLEX}) = \max(0,\ \mathrm{slots.FLEX} - \mathrm{flex\_filled}).
\]

Define the **empty-capacity position set** \(N(R)\):

1. Include every fixed position \(x \in \{\mathrm{QB},\mathrm{RB},\mathrm{WR},\mathrm{TE},\mathrm{DST},\mathrm{K}\}\) with \(\mathrm{def}(x) > 0\).
2. If \(\mathrm{def}(\mathrm{FLEX}) > 0\), also include \(\{\mathrm{RB},\mathrm{WR},\mathrm{TE}\}\) as FLEX-eligible capacity (they may fill the open FLEX).

If \(N(R) = \emptyset\) (all starter capacity filled), the cross-position
alternative is defined as missing (§2.3) — ranking falls back to \(M_D\) alone
for that decision (bench phase). Record `cross_alt_missing=true`.

### 2.2 Eligible alternatives for candidate \(p\)

Let \(\mathrm{pos}(p)\) be \(p\)'s position (uppercased).

The **cross-position alternative set** \(\mathcal{A}(p)\) is the set of remaining
draftable players \(q\) such that:

- \(q \neq p\)
- \(q\) has a frozen V3-A calibrated value \(v(q)\)
- \(\mathrm{pos}(q) \in N(R)\)
- \(\mathrm{pos}(q) \neq \mathrm{pos}(p)\)

No hypothetical future roster construction. No “who will be left in three
rounds.” Only players **currently** in the remaining pool.

### 2.3 Scalar alternative \(a^*(p)\)

\[
a^*(p) =
\begin{cases}
\max\{ v(q) : q \in \mathcal{A}(p) \}
& \text{if }\mathcal{A}(p) \neq \emptyset \\
0
& \text{otherwise}
\end{cases}
\]

When \(\mathcal{A}(p)=\emptyset\), set `cross_alt_missing=true` and record it on
the recommend artifact (do not silently treat missing as a “normal” zero without
a flag).

---

## 3. One proxy (B.1.0)

**Construction id:** `crosspos_empty_need_nextbest_v1`

**Base marginal (unchanged from D):**

\[
M_D(p) = L(R \cup \{p\}) - L(R)
\]

(same `lineup_ev` path as `adp_v3a` / `MarginalValueStrategy`).

**Cross-position-aware score:**

\[
M_{B1}(p) = M_D(p) - a^*(p)
\]

Rank by \(M_{B1}\) descending; tie-breaks identical to D (ADP, then name).

### What this can say

> Taking \(p\) consumes a pick while another **currently empty** starter need
> still has a higher-valued remaining player at a **different** position —
> so the pick’s raw \(M_D\) overstates the construction value of using this
> scarce pick now.

### What this must not say

> \(p\)'s own position has a high same-position replacement \(r^*\).

That is B.0 and is already falsified.

### Uniform / position-agnostic

- Same rule for all positions and rounds.
- No WR protection coefficient, no QB ban, no Allen special case.
- If WR is “protected,” it must emerge because \(N(R)\) still contains WR (or
  FLEX with a strong remaining WR) while the candidate is elsewhere.

---

## 4. Explicit B.0 distinction (mechanical)

| | B.0 `replacement_nextbest_v1` | B.1.0 `crosspos_empty_need_nextbest_v1` |
| --- | --- | --- |
| Subtracts | \(r^*(p)=\) best remaining **same** \(\mathrm{pos}(p)\) | \(a^*(p)=\) best remaining in \(N(R)\) with **different** position |
| Depends on empty needs \(N(R)\)? | No | **Yes** |
| Can equal \(M_D - r^*\)? | Definitionally yes | **Only by accident** when the max cross-need player happens to match same-pos next-best — not by construction |

**Contract test (required before ladder):**

On a synthetic board with empty WR and empty RB, candidate = best WR, best other WR = \(w_2\), best RB = \(b_1\), with \(v(b_1) \neq v(w_2)\):

- B.0 subtracts \(v(w_2)\)
- B.1.0 subtracts \(v(b_1)\)
- Assert \(a^* \neq r^*\) on that fixture

If a purported B.1 implementation always equals B.0 on such fixtures, it **fails
the contract** and must not run the 60-board ladder.

---

## 5. Falsification (frozen before 2024 eval)

Primary contrast: **B.1 − D** (same role as E−D for B.0).

| Metric | Support requires |
| --- | --- |
| Mean Δ | > 0 |
| Median Δ | > 0 |
| Win rate | > 50% |
| **p10** | **first-class** — not materially worse than D’s left tail |

No parameter sweep. No choosing the formula after seeing results.

| Outcome | Reading |
| --- | --- |
| All four pass | Current-state cross-pos OC supported (n=1 season) |
| Mean ↑, p10 worse | Tradeoff failure — document; no λ |
| Fails cleanly | Proxy does not demonstrate the hypothesis — **do not** auto-open B.1.1 |

---

## 6. Lookahead exclusion (hard)

Illegal under this contract:

- simulating opponent picks / future boards
- “value if I wait N picks”
- survival / V2 lookahead mix
- any term that requires players not in the **current** remaining pool

Legal:

- \(N(R)\) from current counts
- \(v(\cdot)\) from frozen map on current remaining players
- \(M_D\) from current roster + candidate

---

## 7. Implementation gate

- [x] Hypothesis frozen (`e96ba69`)
- [x] Operationalization frozen (this document)
- [x] \(N(R)\), \(\mathcal{A}(p)\), \(a^*\), \(M_{B1}=M_D-a^*\) named
- [x] B.0 mechanical distinction + fixture test specified
- [x] Four-way success criteria frozen (p10 first-class)
- [ ] Unit/spec tests for \(N(R)\), \(a^*\), B.0≠B.1 fixture
- [ ] Strategy `adp_v3b1` (or equivalent) reusing D’s \(M_D\) only
- [ ] Smoke (1–2 boards): \(M_D\) identical; Δ attributable only to \(a^*\)
- [ ] 60-board ladder vs D; report mean/median/WR/p10; **no retune**

**Suggested strategy name (when opened):** `adp_v3b1`  
**Suggested construction id:** `crosspos_empty_need_nextbest_v1`

---

## 8. Status

| Layer | Status |
| --- | --- |
| Cross-position hypothesis | 🟢 frozen |
| B.1.0 operationalization | 🟢 **frozen here** |
| B.1 implementation | 🔴 gated |
| B.0 | 🔴 falsified (do not revive) |
| Lookahead / V2 | 🔴 frozen |
| UI | `marginal` |

---

## 9. One-sentence contract

> **B.1.0 ranks by \(M_D(p) - a^*(p)\), where \(a^*\) is the best frozen V3-A
> value among currently remaining players who fill a currently empty starter
> need at a different position than \(p\); this is not same-position
> replacement; judge by mean, median, WR, and p10 vs D; no lookahead; no
> retune.**
