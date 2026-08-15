# V3-B Branch A operationalization (frozen contract)

**Status:** frozen **operationalization** — one myopic proxy named below.
**No A strategy / ladder / eval code** until the implementation checklist is
checked open. Do not retune after seeing 2024 Δ.

**Production UI:** remains raw **`marginal`**.  
**`evaluable`:** **0**

**Parents:**

- Branch selection [`V3B_BRANCH_SELECTION.md`](V3B_BRANCH_SELECTION.md) (`3465c06`)
- Branch freeze [`V3B_CONSTRUCTION_BRANCH_FREEZE.md`](V3B_CONSTRUCTION_BRANCH_FREEZE.md) (`cfc49b9`)
- B.1 inert [`phase2_v3b1_ladder.md`](phase2_v3b1_ladder.md) (`6355ab9`)
- B.1 ops [`V3B_CROSS_POSITION_OPERATIONALIZATION.md`](V3B_CROSS_POSITION_OPERATIONALIZATION.md) (`bfa9840`)
- Frozen map `adp_emp_pos_v1_train_2021_2023`

**Philosophical closer:**

> B.1 asked how valuable the alternative *player* is (\(v\)). Branch A asks how
> much *lineup marginal* that alternative would deliver *on the current roster*
> (\(M_D\)). Same current-state eligibility; different subtractand. Still not
> lookahead.

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
frozen V3-A values (for lineup EV only), roster slot template, and the full
current-state \(M_D(\cdot)\) map over remaining candidates (same path as D).

**Forbidden:** actual PPR, future picks, simulated future boards, survival /
lookahead, λ/CVaR, WR/QB penalties, map retune, B.1.1-style magnitude tweaks.

---

## 2. Eligibility: reuse B.1’s \(N(R)\) and \(\mathcal{A}(p)\)

**Do not invent a parallel roster model.** Reuse
`empty_capacity_positions` / FLEX accounting identical to B.1 /
`adp_feasible` (`crosspos_empty_need` / `min_starter_picks_needed` spirit).

### 2.1 Empty starter capacity \(N(R)\)

Same as B.1 §2.1:

1. Fixed positions with \(\mathrm{def}(x) > 0\).
2. If \(\mathrm{def}(\mathrm{FLEX}) > 0\), include \(\{\mathrm{RB},\mathrm{WR},\mathrm{TE}\}\).

Invariant:

> **\(N(R)\) determines which positions have live capacity;**
> **\(\mathrm{pos}(q) \neq \mathrm{pos}(p)\) determines the alternative is
> genuinely cross-position.**

Live need ≠ mere label mismatch: a WR is an alternative for a QB candidate only
if WR ∈ \(N(R)\) (fixed WR deficit and/or open FLEX).

### 2.2 Eligible alternative set \(\mathcal{A}(p)\)

Same membership as B.1 §2.2: remaining \(q \neq p\) with \(\mathrm{pos}(q) \in N(R)\)
and \(\mathrm{pos}(q) \neq \mathrm{pos}(p)\), and with a defined decision-time
\(M_D(q)\) (same scoring loop as D).

If \(N(R)=\emptyset\) or \(\mathcal{A}(p)=\emptyset\): alternative missing;
rank by \(M_D\) alone; set `cross_alt_missing=true`.

---

## 3. Definition of \(q^*\) (distinct from B.1)

**B.1 chose** \(q^*\) / \(a^*\) by **calibrated value**:

\[
a^*(p) = \max\{ v(q) : q \in \mathcal{A}(p) \}
\]

**Branch A chooses** \(q^*\) by **decision-time marginal**:

\[
q^*(p) = \arg\max_{q \in \mathcal{A}(p)} M_D(q)
\]

with ties broken identically to D’s recommend sort (ADP, then name) among
\(\mathcal{A}(p)\).

**Hard rule:** do **not** select \(q^*\) by \(\arg\max v\) and then subtract
\(M_D(q^*)\). That hybrid is forbidden — it would blur A vs B.1 after failure.

When \(\mathcal{A}(p)=\emptyset\): treat \(M_D(q^*)\) as \(0\) and
`cross_alt_missing=true` (flagged; not a silent “normal” zero).

---

## 4. One formula \(M_A\) (no tunable parameters)

**Construction id:** `crosspos_empty_need_marginal_v1`  
**Suggested strategy name:** `adp_v3ba` (or `adp_v3bA`)

**Base marginal (byte-identical to D):**

\[
M_D(x) = L(R \cup \{x\}) - L(R)
\]

same `MarginalValueStrategy` / `adp_v3a` path for every remaining \(x\).

**Branch A score:**

\[
M_A(p) = M_D(p) - M_D(q^*(p))
\]

Rank by \(M_A\) descending; tie-breaks identical to D.

### What this can say

> Taking \(p\) forgoes the **current-roster marginal** of the best remaining
> player who fills a different live need — so raw \(M_D(p)\) overstates the
> construction value of using this scarce pick now.

### What this must not say

- Same-position replacement \(r^*\) (B.0 — falsified).
- Subtract calibrated \(v(q^*)\) (B.1 — inert).
- Future availability / one-step lookahead (Branch B — deferred).

### Uniform / position-agnostic

Same rule for all positions and rounds. No WR/QB coefficients, no Allen case.

---

## 5. Explicit B.1 distinction (mechanical)

| | B.1 `crosspos_empty_need_nextbest_v1` | A `crosspos_empty_need_marginal_v1` |
| --- | --- | --- |
| Eligibility \(N(R)\), \(\mathcal{A}(p)\) | Current empty need + cross-pos | **Identical** |
| Selects \(q^*\) by | \(\arg\max v(q)\) | \(\arg\max M_D(q)\) |
| Subtracts | \(v(q^*)\) | \(M_D(q^*)\) |
| Can equal B.1? | — | **Only by accident** when \(v\)-argmax and \(M_D\)-argmax coincide *and* \(v=M_D\) numerically — not by construction |

**Contract tests (required before ladder):**

1. **B.1 ≠ A selection:** fixture where in \(\mathcal{A}(p)\), player \(u\) has
   highest \(v\) but player \(w\) has highest \(M_D\), \(u \neq w\). Assert A’s
   \(q^* = w\) and B.1’s alternative is \(u\).
2. **Subtractand:** assert A’s penalty equals \(M_D(q^*)\), not \(v(q^*)\), on
   that fixture.
3. **Same \(N(R)\)** fixtures as B.1 (fixed deficits, FLEX expansion, empty set /
   bench fallback).
4. **No same-position** alternative in \(\mathcal{A}(p)\).

If a purported A implementation always equals B.1 on fixtures where
\(v\)-argmax ≠ \(M_D\)-argmax, it **fails the contract** and must not run the
60-board ladder.

---

## 6. Falsification (frozen before 2024 eval)

Primary contrast: **A − D**.

| Metric | Role |
| --- | --- |
| Mean Δ | Predeclared |
| Median Δ | Predeclared |
| Win rate | Predeclared |
| **p10** | First-class |
| **Boards with ≥1 changed pick** | **First-class** (post–B.1) |

No parameter sweep. No choosing the formula after seeing results.

### Switch rules (from `3465c06` — exact)

| Outcome | Reading | Next |
| --- | --- | --- |
| **0/60** boards with ≥1 pick change | A policy-inert | **Stop A**; open Branch B design |
| Pick changes but **A−D ≤ 0** (mean/median/WR/p10 fail) | A falsified | **Stop A**; open Branch B design |
| **A−D** positive on predeclared metrics | Provisional support | **Mechanism audit first**; do **not** iterate A |

**No A.1.** If inert or falsified, do not multiply, soften, or second-best.

Branch B, if opened: **one-step state-dependent opportunity cost**, not “bring
V2 back.”

---

## 7. Lookahead exclusion (hard)

Illegal under this contract:

- simulating opponent picks / future boards
- “value if I wait N picks”
- survival / V2 lookahead mix
- any term requiring players not in the **current** remaining pool
- selecting \(q^*\) with future-state information

Legal:

- \(N(R)\) from current counts (same as B.1)
- \(M_D(\cdot)\) from current roster + each remaining candidate (same as D)
- \(q^* = \arg\max M_D\) on \(\mathcal{A}(p)\)

---

## 8. Non-goals

- No B.1.1 / A.1 retunes
- No λ / CVaR
- No V2 / lookahead / Branch B implementation in this gate
- No V3-A map or value changes
- No positional penalties or special cases
- No comparing against C as the construction baseline (baseline is **D**)

---

## 9. Implementation gate

- [x] Branch A selected (`3465c06`)
- [x] \(N(R)\), \(\mathcal{A}(p)\) reused from B.1
- [x] \(q^* = \arg\max M_D\) on \(\mathcal{A}(p)\) named
- [x] \(M_A = M_D(p) - M_D(q^*)\) named; construction id named
- [x] B.1 mechanical distinction + fixture tests specified
- [x] Metrics + switch rules frozen (incl. pick-change count)
- [ ] Unit/spec tests for \(N(R)\), \(q^*\) by \(M_D\), B.1≠A fixture
- [ ] Strategy `adp_v3ba` reusing D’s \(M_D\) only
- [ ] Smoke: \(M_D\) identical to D; Δ attributable only to \(M_D(q^*)\)
- [ ] 60-board ladder vs D; report mean/median/WR/p10 + **n boards with pick Δ**; **no retune**

---

## 10. Status

| Layer | Status |
| --- | --- |
| Branch A selection | 🟢 frozen (`3465c06`) |
| A operationalization | 🟢 **frozen here** |
| A implementation | 🔴 gated |
| B.1 | ❌ inert (do not revive / retune) |
| Branch B | 🟡 deferred |
| UI | `marginal` · `evaluable=0` |

---

## 11. One-sentence contract

> **Branch A ranks by \(M_D(p) - M_D(q^*)\), where \(q^*\) is the remaining
> player in B.1’s cross-need set \(\mathcal{A}(p)\) with highest current-state
> \(M_D\) (not highest \(v\)); judge by A−D mean/median/WR/p10 and boards with
> ≥1 pick change; no lookahead; no retune; no A.1.**
