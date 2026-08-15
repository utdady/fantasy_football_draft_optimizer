# V3-B cross-position opportunity-cost hypothesis (frozen contract)

**Status:** frozen **hypothesis** checkpoint — **no formula, no strategy code,
no ladder, no operationalization** until a later implementation gate is opened
under a *separate* design revision that names a specific proxy.

**Production UI:** remains raw **`marginal`**.

**Parents:**

- V3-B.0 failure audit [`phase2_v3b0_failure_audit.md`](phase2_v3b0_failure_audit.md) (`b668076`)
- V3-B.0 ladder / falsification [`phase2_v3b_ladder.md`](phase2_v3b_ladder.md) (`5a2d4fc`)
- V3-B.0 construction design [`V3B_CONSTRUCTION_DESIGN.md`](V3B_CONSTRUCTION_DESIGN.md) (`cb7a325`)
- V3-A.0 map `curve_id = adp_emp_pos_v1_train_2021_2023` (frozen)

**Philosophical closer:**

> Cross-position opportunity cost asks what valuable *capacity / alternative* the
> current pick consumes **now**, using only the current decision state.
> Lookahead asks what you will wish you had done later. Those are different
> hypotheses. This document freezes the former as a claim to test — not an
> algorithm to invent.

---

## 1. Exact claim

> **V3-B hypothesis:** Independent positional replacement values are
> insufficient because roster construction has a **cross-position opportunity
> cost**: taking player \(p\) consumes a roster slot (and draft capital) that
> could have been used for a player at **another** position, and that foregone
> alternative **cannot** be represented by \(r^*(p)\) computed only within
> \(p\)'s own position.

**What this is not:**

- Not a claim that lookahead / survival is necessary.
- Not a claim that any particular formula for cross-position cost is correct.
- Not permission to open B.1, retune \(r^*\), or resurrect V2.

---

## 2. Evidence motivating the hypothesis

From V3-B.0 (`5a2d4fc`, `b668076`):

| Observation | Implication |
| --- | --- |
| E−D = **−24.3** mean, **42%** WR, p10 **−204** | Simple positional \(M_E = M_D - r^*\) **falsified** on all four predeclared criteria |
| First-fork actual E−D ≈ **+10.7** (not uniformly bad) | Failure is **not** “E always picks worse immediate players” |
| At first fork: \(M_D(D)-M_D(E)\approx +34.7\), \(M_E(E)-M_E(D)\approx +13.7\) | E **follows** its objective; D keeps higher absolute \(M_D\) |
| First forks mostly **WR→RB / WR→TE** (R2–R4) | Composition shift, not primarily R1 Allen |
| Roster count Δ ≈ **−2.9 WR / +1.6 RB / +1.3 TE** | Cross-position reallocation |
| Starter Δ: WR **−384**, RB **+270**, TE **+93**; r11–15 **−172** | Early/local gains do not compensate for WR hole + late recovery failure |
| \(\|M_E\|\le 1\) on only ~**5%** of the decision pool | **Replacement-collapse** is not the primary mechanism |

**Central warning (preserve):**

> E gained RB/TE at the expense of WR, and the early gains did not compensate
> for the late WR loss.

**Candidate failure mechanism:** allocation of scarce picks **across positions
and future scarcity**, not merely a better within-position replacement number.

---

## 3. Falsifiable experimental question

The next *implementation* (when gated) must ask:

> Does a **minimal decision-time cross-position opportunity-cost signal**,
> while leaving frozen V3-A values and all other Phase-2 machinery unchanged,
> improve realized roster outcomes vs D?

**Primary contrast:** `new_construction − D`  
(same role E−D played for B.0).

**Not the question:**

> Can we invent a better roster optimizer?

Failure of a specific proxy **does not** automatically authorize the next proxy.
It means *that operationalization* did not demonstrate the hypothesis.

---

## 4. Hard boundaries (information & method)

| Allowed at decision time | Forbidden |
| --- | --- |
| Frozen V3-A calibrated values | Eval-season actual PPR in `recommend()` |
| Current remaining pool | Lookahead / survival / “picks until next turn” (V2 family) |
| Current roster / empty slots / starter needs | λ, CVaR, robust objectives |
| Deterministic functions of the above | Position-specific bans/penalties (WR protect, QB ban, Allen rules) |
| Same 60 `(slot, seed)`, opponents, `ppr_eval_v1_2024` | Retuning after seeing the 60-board Δ |
| `evaluable = 0` | Map / curve changes |

### Cross-position ≠ lookahead (hard separation)

| | Cross-position OC (this hypothesis) | Lookahead / survival (out of scope here) |
| --- | --- | --- |
| Asks | What valuable alternative capacity am I consuming **now**? | What will I wish I had done **several rounds later**? |
| Uses | Current decision state only | Future picks, simulated boards, or multi-step plans |
| If needed to “work” | — | You have left this hypothesis and entered the V2 family |

If an operationalization requires future picks, future outcomes, or simulated
survival to function, it is **not** a test of this hypothesis.

---

## 5. Success / falsification criteria

Same four-way test as B.0 (no single-metric victory):

| Metric | Requirement for support |
| --- | --- |
| Mean Δ vs D | positive |
| Median Δ vs D | positive |
| Win rate vs D | > 50% |
| p10 | not materially worse than D’s left tail under the same contract |

Interpretive discipline:

| Outcome | Reading |
| --- | --- |
| All four improve | Cross-position hypothesis **supported** by that proxy (n=1 season) |
| Mean ↑, p10 worse | Tradeoff failure — document; do not invent λ |
| Near zero / mixed | Proxy did not demonstrate the hypothesis |
| Mean ≤ 0 | Proxy **fails cleanly** — do not silently open B.2 |

---

## 6. Experimental contract (when implementation is later opened)

Freeze these before any code:

1. **Control D:** `adp_v3a` + frozen V3-A DB (unchanged).
2. **Treatment:** one named construction id; **one** decision-time cross-position
   signal (formula lives in a *future* design revision — **not here**).
3. **Values:** identical frozen map (`adp_emp_pos_v1_train_2021_2023`).
4. **Boards:** same 60 pairs, same `noisy_adp` opponents, same scoring.
5. **Primary contrast:** treatment − D (mean, median, WR, p10 + full pairs).
6. **No retune** after seeing Δ.

**Explicitly deferred:** the mathematical form of the cross-position term.
Inventing \(c^*_{\text{cross-pos}}\) in this document would repeat optimizer
tinkering. The next *design* PR after this freeze may propose **one** boring
proxy; this file only locks the **claim** and **gates**.

---

## 7. Implementation gate (closed)

Do **not** implement until a later revision:

- [x] Hypothesis claim frozen (this document)
- [x] B.0 evidence & ruled-out mechanisms recorded
- [x] Cross-pos vs lookahead boundary frozen
- [x] Four-way success criteria frozen
- [ ] Named operationalization of the cross-position signal (separate design)
- [ ] Unit/spec tests for that operationalization
- [ ] Strategy + smoke + 60-board ladder vs D
- [ ] Report with interpretation flags; no silent next proxy on failure

**`b668076` remains a scientific checkpoint.** This file does not reopen B.1.

---

## 8. Status board

| Question | Answer |
| --- | --- |
| Did V3-A improve valuation? | 🟢 Yes |
| Did that automatically improve rosters? | 🔴 No |
| Is zero-replacement the full explanation? | 🔴 No |
| Does simple positional replacement fix it? | 🔴 Falsified (B.0) |
| Is replacement-collapse the main issue? | 🔴 Unlikely (~5% near-zero \(M_E\)) |
| Is cross-position / allocation implicated? | 🟡 Provisionally yes |
| Is lookahead proven necessary? | 🔴 No |
| Should we code B.1 / a cross-pos formula now? | 🔴 **No** |

| Layer | Status |
| --- | --- |
| V3-B.0 | 🔴 falsified / frozen |
| Cross-position hypothesis | 🟢 **formalized here** |
| Operationalization | 🔴 not chosen |
| Implementation | 🔴 gated |
| V2 / risk / survival | 🔴 frozen |
| UI | `marginal` |

---

## 9. One-sentence contract

> **Independent within-position next-best replacement cannot represent the
> foregone value of using a scarce pick/slot for another position; any test of
> that claim must use only decision-time information, leave V3-A values frozen,
> forbid lookahead, and be judged by mean, median, win rate, and p10 vs D —
> without inventing the proxy in this document.**
