# V3-B construction design (frozen contract)

**Status:** frozen design checkpoint — **no E strategy / ladder / eval code**
until this note is revised or the implementation checklist below is checked off.

**Production UI:** remains raw **`marginal`**.

**Parents:**

- R1 opportunity-cost audit [`phase2_v3a_r1_opportunity_cost_audit.md`](phase2_v3a_r1_opportunity_cost_audit.md) (`7ae30b4`)
- V3-A mechanism audit [`phase2_v3a_mechanism_audit.md`](phase2_v3a_mechanism_audit.md) (`4753d2e`)
- V3-A.0 ladder [`phase2_v3a_ladder.md`](phase2_v3a_ladder.md) (`f6c5010`)
- V3-A calibration design [`V3A_CALIBRATION_DESIGN.md`](V3A_CALIBRATION_DESIGN.md)
- Frozen map `curve_id = adp_emp_pos_v1_train_2021_2023`

**Philosophical closer:**

> Replacement is an **opportunity-cost estimate**, not a prediction of future
> availability. V3-B changes **construction only**. It must not quietly become
> V2/lookahead/survival.

---

## 1. Why V3-B is justified

V3-A showed:

| Layer | Result |
| --- | --- |
| Player valuation | 🟢 supported (`\|e\|` 87.8 → 54.3; nearer on ~75% of paired picks) |
| Roster translation | 🟡 mean-up / tail-worse under unchanged marginal construction |
| R1 mechanism | 🟢 `D_combination` |

R1 audit (`7ae30b4`):

- `lineup_before = 0` on **all 60** boards → empty-slot / zero-replacement (**A**)
- Replacement gap exists but is unused by \(M_D\) (**B**)
- Downstream portfolio cost on **39/60** (**C**)
- Allen wins the *pick* on actual (~95% WR) while RB starters go **−162**

**Causal reading (frozen):**

> V3-A selects genuinely valuable players, but \(M_D(p)=L(R+p)-L(R)\) treats an
> empty positional slot as zero and therefore overstates the immediate value of
> filling it. It also fails to price the positional opportunity consumed by the
> pick.

That is **not** an Allen-selection problem and **not** permission to retune the
map.

---

## 2. Hypothesis

**V3-B hypothesis (replacement-aware construction):**

> Holding the frozen V3-A value map fixed, a single uniform construction change
> that subtracts a decision-time positional replacement/opportunity cost from the
> existing marginal will improve realized roster outcomes vs D (**E−D**),
> including the left tail — without lookahead, survival, or risk machinery.

**D asks:** *Is this player valuable?*  
**E asks:** *Is this player valuable enough to justify consuming this positional
opportunity?*

Name: **replacement-aware marginal** — one construction adjustment only.

---

## 3. Causal ladder (evaluation)

```text
B  ADP-feasible
│
C  ADP structural (linear curve + current construction)
│
D  V3-A calibrated valuation + current construction
│
E  V3-A calibrated valuation + replacement-aware construction
```

| Contrast | Question |
| --- | --- |
| **D−C** | Calibration effect (already measured; do not retune) |
| **E−D** | **Primary** — construction effect under identical values |
| E−B | Overall vs feasible — secondary / descriptive only |
| E−C | Not load-bearing for V3-B |

### Hard invariant

> **D and E use exactly the same frozen V3-A value map
> (`adp_emp_pos_v1_train_2021_2023`). Only the construction / ranking rule
> changes.**

If the map is edited because E disappoints, the experiment is void.

---

## 4. Frozen operationalization: V3-B.0

### 4.1 Inputs (decision-time only)

| Allowed | Forbidden |
| --- | --- |
| Frozen V3-A calibrated `season_points` (same DB as D) | Eval-season actual PPR / outcomes |
| Current remaining draftable pool | Future-pick / availability simulation |
| Position, ADP (tie-breaks only, as in D) | Curve retune / new `curve_id` |
| Current user roster \(R\) | λ, CVaR, survival, V2 lookahead |
| Empty-slot / lineup EV as in D | Position-specific QB/RB/TE penalties |

**Principle:**

> Replacement is an opportunity-cost estimate from the **current remaining
> pool**, not a forecast of who will be available later.

### 4.2 Base marginal (unchanged from D)

\[
M_D(p) = L(R \cup \{p\}) - L(R)
\]

Same FLEX-aware `lineup_ev` construction as `MarginalValueStrategy` /
`adp_v3a`.

### 4.3 Replacement estimate \(\hat r\)

For candidate \(p\) with position \(\mathrm{pos}(p)\):

\[
\hat r_{\mathrm{pos}}(p)
=
\begin{cases}
\max\bigl\{ v(q) : q \in \mathcal{P}_{\mathrm{pos}(p)},\; q \neq p \bigr\}
& \text{if at least one other remaining player at }\mathrm{pos}(p) \\
0
& \text{otherwise}
\end{cases}
\]

where:

- \(v(\cdot)\) = **frozen V3-A calibrated value** (decision-time projection)
- \(\mathcal{P}_{\mathrm{pos}}\) = remaining draftable players at that position
- “Best remaining **other than** \(p\)” = the positional opportunity consumed if
  \(p\) is taken (VORP-like next-best, not “2nd-best including \(p\)” when \(p\)
  is not #1)

**Missing replacement:**

- Use \(\hat r = 0\) **only** when no other player remains at that position.
- Decision / recommend artifacts **must** record
  `replacement_missing=true` (or equivalent) in that case.
- Do **not** silently COALESCE missing replacement without a recorded flag.

DST / K: same rule if present in the pool; no special-case exemption.

### 4.4 E score (ranking objective)

\[
M_E(p) = M_D(p) - \hat r_{\mathrm{pos}}(p)
\]

- Rank by \(M_E\) descending.
- Tie-breaks: identical to D (ADP, then name / existing marginal tie order).
- **Uniform** across all roster states and rounds — **no R1 special case**,
  **no QB special case**.

If Allen (or any player) becomes less attractive because \(\hat r\) is high,
that is a **result**, not a design target.

### 4.5 Strategy / materialize labels (when implemented)

| Field | Frozen intent |
| --- | --- |
| Strategy name | `adp_v3b` (or `adp_v3a_replacement`) |
| Values DB | Same as D: `draftopt_p22c_v3a.db` / identical projections |
| Construction id | `replacement_nextbest_v1` (suggested; freeze at implement) |
| UI | stays `marginal` |

---

## 5. Evaluation protocol

| Field | Frozen value |
| --- | --- |
| Boards | Same **60** `(slot, seed)` pairs as V3-A ladder (slots 1–12 × 5, seed0=42) |
| Opponents | modeled `noisy_adp` |
| Scoring | `ppr_eval_v1_2024` |
| Snapshot / market | FFC 12-team PPR; V3-A decision world |
| `evaluable` | **0** (one-season modeled historical experiment) |
| Primary contrast | **E−D** |
| Also report | E−B (secondary), D−C (context only; already known) |
| Contracts | full / ex-DST / ex-DST+TE (same attribution ladder) |

### Success criteria (no single-metric victory)

Declare E supportive **only if** E−D improves **all** of:

1. mean starter Δ  
2. median starter Δ  
3. win rate vs D  
4. **left tail (p10)** — must not reproduce V3-A’s mean-up / tail-worse pattern

Interpretive flags (examples):

| Outcome | Reading |
| --- | --- |
| E−D ↑ mean/median/WR **and** p10 improves | Replacement-aware construction supported (n=1 season) |
| E−D ↑ mean but p10 worse | Tradeoff failure — do not ship; do not add λ |
| E−D ≈ 0 | Simple replacement insufficient → multi-round OC may be next *design* question |
| E−D ↓ | Construction hypothesis fails cleanly on this board |

---

## 6. Explicitly forbidden

Do **not**, in V3-B.0:

- change or refit `adp_emp_pos_v1_train_2021_2023`
- add λ, CVaR, robust min, or any risk objective
- add survival / lookahead / “picks until next turn” machinery (V2)
- add QB / RB / TE / R1 penalties or bans
- design E to stop Josh Allen specifically
- use 2024 actuals inside `recommend()`
- treat missing \(\hat r\) as zero without recording `replacement_missing`
- change opponent policy, seeds, or scoring contract mid-experiment
- set `evaluable=1`

A new construction id / design revision is required for any change to
\(\hat r\) definition, \(M_E\) formula, or success criteria.

---

## 7. Leakage boundary

```text
 frozen V3-A values + remaining pool
              │
              ▼
     M_D(p) and r̂_pos(p)     ← decision-time only
              │
              ▼
           M_E(p) rank
              │
              ▼
         draft completes
              │
              ▼
      actual PPR scoring   ← outcomes only here
```

Same honesty invariants as Phase 2 / V3-A: FFC ≠ ESPN, 12 ≠ 10 production UI,
modeled opponents, `evaluable=0`.

---

## 8. Implementation checklist (gate)

Do **not** write E until all boxes are acknowledged:

- [x] Hypothesis frozen (replacement-aware, one change)
- [x] \(\hat r\) = best remaining **other than** \(p\) at position; 0 + flag if none
- [x] \(M_E = M_D - \hat r\); uniform; position-agnostic
- [x] D/E share identical frozen V3-A values
- [x] Primary contrast E−D; success needs mean, median, WR, **and p10**
- [x] Forbidden list frozen (no V2/λ/Allen engineering/map retune)
- [ ] Strategy + ladder implemented under this contract (next PR after freeze)
- [ ] Report written with E−D distribution + interpretation flags

**Next (after this freeze):** implement `adp_v3b` + same-board E−D ladder only.
No parallel construction variants in the first E PR.

---

## 9. Status board (at freeze)

| Layer | Status |
| --- | --- |
| V3-A valuation | 🟢 supported |
| V3-A roster translation | 🟡 failure mechanism identified (`D_combination`) |
| Replacement-cost hypothesis | 🟢 **formalized here** |
| V3-B design | 🟢 **frozen** |
| V3-B implementation | 🔴 blocked until checklist gate opens |
| Risk / survival / V2 | 🔴 remain frozen |
| External validity | 🔴 one season / modeled opponents |
| UI | `marginal` |

---

## 10. One-sentence contract

> **E = D’s frozen calibrated values + one uniform next-best positional
> replacement subtraction from empty-slot-aware marginal; judge by E−D mean,
> median, win rate, and p10; never retune the map or resurrect V2 to make E win.**
