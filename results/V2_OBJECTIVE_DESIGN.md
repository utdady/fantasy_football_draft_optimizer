# V2 objective & scenario semantics (frozen design note)

**Status:** frozen decision-theory checkpoint — **no new V2 strategy / λ / matrix** until this note is revised.

**Production UI:** remains raw **`marginal`**.

**Philosophical closer:**

> The optimizer should not eliminate uncertainty. It should quantify how much its recommendation depends on uncertainty.

---

## 1. Primary objective

For a normal human redraft, the primary goal is:

> **Maximize expected final roster value, subject to reasonable uncertainty about how the draft board evolves.**

\[
\boxed{\max\; \mathbb{E}[L(\text{final roster})]}
\]

- **Not** maximize floor.
- **Not** minimize regret.
- **Not** “never get sniped.”

Fantasy leagues are competitions over **season-long roster performance**. A strategy that systematically sacrifices expected points to avoid uncomfortable draft outcomes can become too conservative. This preserves the original insight behind V2-alpha (opportunity cost / next-pick EV), while refusing to promote stress-case floor into the objective.

---

## 2. Secondary diagnostics (not blind objectives)

For candidate \(p\), report alongside the primary EV score:

### Board downside (fragility)

\[
D(p) = EV(p) - \min_f EV(p \mid f)
\]

Answers: *How badly does this pick depend on the future board?*

### Maximum regret

\[
R(p) = \max_f \bigl( EV^*(f) - EV(p \mid f) \bigr)
\]

where \(EV^*(f) = \max_a EV(a \mid f)\).

Answers: *If a particular future happens, how much better could I have done?*

These are **warnings / decision diagnostics**, not things the optimizer should blindly minimize.

---

## 3. Two different notions of “risk” (empirical)

From [`case_study_risk_ev_surface.md`](case_study_risk_ev_surface.md) at slot-1 R1 (wait 18), the Pareto frontier is **two points only**:

| | Chase | Daniels |
| --- | ---: | ---: |
| Mean EV | **688.2** | 678.3 |
| Floor | 641.4 | **672.9** |
| Downside | 46.8 | **5.4** |
| Max regret | **31.6** | 38.7 |

Everything else is dominated.

**Chase/Daniels is not ambiguous data — the objective is:**

| Stated goal | Winner |
| --- | --- |
| Expected value under ADP-like behavior | **Chase** |
| Worst-case board protection (floor) | **Daniels** |
| Worst-case regret | **Chase** |

There is **no single scalar “risk”** the data tells us to optimize. Floor-risk and regret-risk disagree. Do **not** invent \(\mathrm{Score} = \mathrm{Mean} - \lambda \cdot \mathrm{Risk}\) until “risk” is named as one of these diagnostics (and even then, prefer exposing the frontier over a hidden λ).

---

## 4. Scenario semantics: planner vs stress

**Do not** treat ADP / proj / VOR as interchangeable “possible futures” with equal probability.

### Planner scenarios

Approximate **plausible opponent behavior** for modeling board evolution (e.g. ADP-like, need-aware, scarcity/VOR-oriented). Used when estimating \(\mathbb{E}[L]\).

### Stress scenarios

Deliberately **adversarial / extreme** board evolution (e.g. pure projection-greedy). Used to **test** robustness and to compute diagnostics \(D\), \(R\).

| Role | Example | Use in EV? | Use in stress / diagnostics? |
| --- | --- | --- | --- |
| Planner | ADP-like / noisy ADP | Yes | Optional |
| Stress | proj_greedy | **No** (not equal-weight) | Yes |

This is why prior branches failed:

- **Equal-weight mixture β** — treated stress as a planner future → diluted danger without fixing it ([`V2_BETA.md`](V2_BETA.md)).
- **`robust_min` (`min_f`)** — promoted stress floor to the objective → fixed proj-greedy, wiped ADP-like edge (~−72 vs α).

`proj_greedy` can be **useful as stress** and **inappropriate as an equally weighted expected future** at the same time.

---

## 5. What we are eventually evaluated against

Sim CPU policies are **models of the draft**, not the ultimate target.

\[
\boxed{\text{maximize actual season-long fantasy points}}
\]

using **preseason information only**.

Eventual research loop:

```text
Historical draft snapshot (preseason info)
        ↓
Optimizer decisions
        ↓
Actual historical board unfolds
        ↓
Actual season fantasy points
        ↓
Evaluate roster
```

Do not overfit the current three deterministic scenario policies.

---

## 6. Product philosophy (later — not now)

The optimizer should not pretend every state has one universally correct pick. Prefer exposing the **decision frontier**, e.g.:

> **CHASE** — best expected-value choice (~688 EV); board sensitivity high; worst modeled scenario ~641; max regret ~31.6  
> **DANIELS** — more resilient alternative (~678 EV); worst scenario ~673; max regret ~38.7  
> Tradeoff: ~10 EV for substantially less board fragility.

**Do not build this UI yet.** Science first; production remains `marginal`.

---

## 7. Locked decisions (checklist)

| Item | Decision |
| --- | --- |
| Primary objective | \(\max \mathbb{E}[L(\text{final roster})]\) |
| Secondary | Board downside \(D\) + max regret \(R\) as diagnostics |
| Planner scenarios | Plausible opponent behavior |
| Stress scenarios | Extreme board evolution; not equal-weight EV |
| Eval target | Actual season points (preseason info only) |
| Production | `marginal` |
| V2 | Research prototype; no promotion |
| Next algorithm work | **Frozen** until this note is revised |

---

## 8. Research progression (record)

```text
V1 raw marginal → VOR → V2-alpha
        ↓
survival failure (board evolution)
        ↓
policy mixture β          ✗ rejected
        ↓
robust minimax            ✗ too conservative (rejected final)
        ↓
risk/EV + Pareto surface  → Chase ↔ Daniels; floor ≠ regret
        ↓
THIS NOTE                 → objective & scenario semantics
        ↓
(only then) design next strategy / UI frontier
```

Evidence pointers:

- Alpha baseline: [`V2_ALPHA_BASELINE.md`](V2_ALPHA_BASELINE.md)
- Mixture / robust record: [`V2_BETA.md`](V2_BETA.md)
- Survival Outcome A: [`case_study_survival_chase_daniels.md`](case_study_survival_chase_daniels.md)
- Robust diagnostic: [`case_study_robust_min.md`](case_study_robust_min.md)
- Robust lean: [`stress_robust_min_slot1.md`](stress_robust_min_slot1.md)
- Risk surface: [`case_study_risk_ev_surface.md`](case_study_risk_ev_surface.md)
