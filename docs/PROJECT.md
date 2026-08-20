# Project methods

This file explains **what was done to the data**: sources, freezes, the recommendation
math that actually exists in the code, the harness gates, and the experiment map.

It does **not** replace the living experiment log. Numbers and verdicts live in
[`LAB_LOG.md`](LAB_LOG.md). If a table here disagrees with that log, the log wins.

Live product discipline: [`../results/AUTOPSY_GATE.md`](../results/AUTOPSY_GATE.md).  
Version ladder: [`../ROADMAP.md`](../ROADMAP.md).  
Harness rules: [`HARNESS_SPEC.md`](HARNESS_SPEC.md).  
Integrity track: [`FORMAL.md`](FORMAL.md).  
Source checklist: [`../DATA_SOURCES.md`](../DATA_SOURCES.md).

---

## 1. Reading order

| Document | Job |
|---|---|
| **This file** | Methods, math, provenance, how to read a result |
| [`LAB_LOG.md`](LAB_LOG.md) | Hypotheses, E-ids, tables, verdicts (append-only) |
| [`HARNESS_SPEC.md`](HARNESS_SPEC.md) | As-of-T reconstruction rules and pass/fail gates |
| [`FORMAL.md`](FORMAL.md) | What Lean/property tests could protect vs what statistics prove |
| [`../ROADMAP.md`](../ROADMAP.md) | Version ladder (may lag the log; do not treat as the experiment log) |
| [`../results/AUTOPSY_GATE.md`](../results/AUTOPSY_GATE.md) | Live Gate 2 protocol |

Python tells us what happened. Statistics tell us whether it is reproducible.
Formal integrity would tell us whether we accidentally changed the question while measuring it.

---

## 2. What the system is

Draft Optimizer V1 is a **projection-first** 12-team PPR snake redraft practice room
with a FLEX-aware marginal recommendation engine.

```text
Sleeper / DynastyProcess / ESPN (+ optional FantasyPros overlay)
        |
        v
   ingest -> data/raw/* + data/draftopt.db
        |
        v
   recommend(strategy=marginal)   FLEX-aware starter lift
        |
        v
   draft UI / live_sim / CPU ADP opponents
        |
        v
   autopsy case dump + disagreement log   (does not change TAKE)
        |
        v
   results/* artifacts
```

The recommendation engine is the brain. The draft UI is a **viewer and practice
room for frozen TAKE**, not a second place where a new strategy is silently chosen.
FantasyPros overlay sits **beside** TAKE only.

---

## 3. Data sources and provenance

Layers (do not mix in code) — see [`../DATA_SOURCES.md`](../DATA_SOURCES.md):

1. **Identity / state** — who the player is, injury, team, bye  
2. **Market** — ADP / draft price  
3. **Expectation** — projections / rankings / uncertainty  
4. **Derived (ours)** — marginal, VOR, survival stubs, etc.

### Live V1 (production)

| Source | Layer | Role in TAKE |
|---|---|---|
| Sleeper players API | Identity | Roster of NFL players |
| DynastyProcess `db_playerids` | Identity | Crosswalk spine |
| DynastyProcess ECR | Expectation | Tie-break / display (not ESPN-proj substitute) |
| ESPN fantasy (undocumented) | Market + expectation | ADP + season PPR `appliedTotal` for `marginal` |

### Phase-2 historical (research)

| Source | Role |
|---|---|
| FFC 12-team PPR ADP (dated) | Decision-time market for structural ladder |
| 2024 actual PPR (contract `ppr_eval_v1_2024`) | Outcome scoring only |
| V3-A map train 2021–2023 | Calibration instrument for D |

### What a recommendation at time T may see

| Input | Allowed |
|---|---|
| Player identity / team / pos | Yes |
| ADP with `as_of <= T` | Yes |
| Projection with `as_of <= T` | Yes |
| Draft slot / remaining pool | Yes |
| Actual season PPR | **No** (scoring only) |
| Post-cutoff news / injuries | **No** (preseason harness) |

---

## 4. Versions, tags, freezes

**Production freeze:** TAKE = raw V1 `marginal`. Ship readiness and autodraft use it.
Do not silently swap in VOR / V2 / V3 / FP proj.

**Research freezes (selected):**

| Freeze | Meaning |
|---|---|
| Phase-2 historical design | [`../results/PHASE2_HISTORICAL_EVAL.md`](../results/PHASE2_HISTORICAL_EVAL.md) |
| P22C ADP structural methodology | [`../results/PHASE2_P22C_ADP_STRUCTURAL.md`](../results/PHASE2_P22C_ADP_STRUCTURAL.md) |
| V3-A calibration definition | Gate 3 + train 2021–2023 map |
| V3-B construction menu | Closed at `6ad702b` |
| Autopsy stubs | Crude ADP sigmoid + ADP-greedy `two_pick_ev` — do not retune yet |
| V2 objective note | Primary EV; floor/regret are diagnostics only |

Research can change beliefs. It cannot change frozen TAKE without a gated promotion.

---

## 5. Pipeline

```text
candidate_pool(draft)
  -> resolve_projection (ESPN only for V1; quality=high required)
  -> lineup_ev(roster) = base starter points
  -> for each candidate: lineup_ev(roster + cand) - base  => marginal M
  -> sort by (-M, ADP, ECR, name)
  -> top-n recommendations
```

Live: `python -m draftopt.serve` (TAKE via `recommend(..., strategy="marginal")`).  
Synthetic lab: `python -m draftopt.backtest`.  
Historical: Phase-2 modules under `draftopt.phase2.*`.  
Autopsy: `python -m draftopt.autopsy ...`.

---

## 6. Methods encyclopedia

Only methods that exist in this repository.

### 6.1 Lineup EV (greedy starters)

**Where:** `draftopt/lineup.py`.

Fill fixed slots (QB, RB, WR, TE, DST, K) by descending season points, then FLEX
from leftover RB/WR/TE. Bench/IR counts do not contribute to EV.

```text
lineup_ev(players, slots).total = sum of assigned starter points
```

This is a **greedy assignment**, not an ILP. It is the V1 definition of roster value.

### 6.2 Marginal value (V1 TAKE)

**Where:** `draftopt/strategies/marginal.py`.

```text
M(p) = lineup_ev(roster ∪ {p}) - lineup_ev(roster)
```

- Projection path: ESPN only (`resolve_projection(..., allow_proxy=False)`).
- Skip candidates without high-quality positive ESPN points (including DST).
- Tie-break: ADP, then FantasyPros ECR, then name.

Scarcity-blind: does not model P(survive) or future picks.

### 6.3 ADP / feasible / structural / V3-A (research strategies)

**Where:** `draftopt/strategies/adp*.py`.

Used in Phase-2 ladders, not production TAKE:

| Strategy | Idea |
|---|---|
| `adp_baseline` | Pick by ADP |
| `adp_feasible` | ADP subject to roster feasibility |
| `adp_structural` | Feasible + structural valuation on ADP curve |
| `adp_v3a` | Same construction as structural; calibrated curve values |

### 6.4 Experimental / rejected strategies (not TAKE)

| Strategy | Status |
|---|---|
| `marginal_vor` | Research / ablation |
| `marginal_no_qb_r1` | Diagnostic policy |
| `marginal_v2` | V2-alpha two-pick EV; failed production bar |
| `marginal_v2_beta` | Rejected equal-weight mixture |
| `robust_min` | Rejected as final objective |

See [`../results/V2_OBJECTIVE_DESIGN.md`](../results/V2_OBJECTIVE_DESIGN.md),
[`../results/V2_ALPHA_BASELINE.md`](../results/V2_ALPHA_BASELINE.md),
[`../results/V2_BETA.md`](../results/V2_BETA.md).

### 6.5 Autopsy stubs (frozen)

**Where:** `draftopt/autopsy.py` (+ related).

- `P(survive)` — crude ADP sigmoid  
- next pick — ADP-greedy `two_pick_ev`  

Diagnostic only. Improving them now would optimize a model for a problem Gate 2
may not confirm.

### 6.6 Phase-2 contrasts

Primary historical metric: realized **starter PPR**.

| Contrast | Meaning |
|---|---|
| B − A | Feasibility gain |
| C − B | Valuation gain (load-bearing for structural thesis) |
| D − C | Calibration gain under fixed construction |
| E − D | Construction overlay (V3-B; closed) |

Do not authorize TAKE changes from synthetic ESPN-proj backtests alone.

### 6.7 V3-A calibration map

Train seasons 2021–2023 FFC ADP → per-position bin means → isotonic regression →
apply to 2024 ADP. Gates 1–4 + leakage audit in `results/phase2_v3a_gate*.md`.
Map frozen; do not refit from 2024 Δ.

---

## 7. Hypotheses and gates (summary)

Full board: [`LAB_LOG.md`](LAB_LOG.md).

| ID | Claim | Status |
|---|---|---|
| H-marginal-v1 | FLEX-aware starter lift is a coherent production baseline | supported (shipped) |
| H-C-B | Structural valuation beats feasible ADP on 2024 starter PPR | preliminary support (`evaluable=0`) |
| H-V3A | Frozen train calibration improves D vs C on mean | supported / frozen (left-tail tradeoff) |
| H-V3B | Licensed construction overlays beat D | **rejected** (closed) |
| H-V2-prod | Ship survival / two-pick EV into TAKE | **not authorized** (failed / gated) |
| H-autopsy-oc | Live disagreements are mostly opportunity-cost | **open** (Gate 2) |

Harness gates: [`HARNESS_SPEC.md`](HARNESS_SPEC.md).  
Autopsy gates: [`../results/AUTOPSY_GATE.md`](../results/AUTOPSY_GATE.md).

---

## 8. Experiment map

Details: [`LAB_LOG.md`](LAB_LOG.md). One line each.

| ID | Question | Verdict |
|---|---|---|
| **E001** | Is V1 `marginal` shippable on 2026 live DB? | PASS ship readiness |
| **E002** | Phase-2 pipeline proof freeze | `evaluable=0` ingest/leakage only |
| **E003** | ADP → feasible → structural on 2024 actuals | C-B preliminary support |
| **E004** | V3-A calibration D vs C | Supported / frozen tradeoff |
| **E005** | V3-B construction vs D | Closed; inert or harmful |
| **E006** | Empty 1.01 autopsy Allen/Gibbs/Puka | Gate 1 closed; no V2 ship |
| **E007** | Live_sim disagreement classification | **queued / NEXT** |
| **E-FORMAL** | Property tests for evaluation integrity | queued (not a Gate 2 blocker) |

---

## 9. What V1 is not

- A scarcity / survival model. Autopsy stubs are diagnostics.
- A recommendation to replace ESPN proj with FP consensus inside TAKE.
- Permission to reopen V3-B or retune V3-A from one live draft.
- A claim that Phase-2 `evaluable=0` ladders are fully green evaluation snapshots.

---

## 10. Citations / external data

1. Sleeper public NFL players API.  
2. DynastyProcess player IDs / ECR mirrors.  
3. ESPN fantasy public endpoints (undocumented; personal-use adapter).  
4. Fantasy Football Calculator ADP (historical / attribution; Cloudflare caveats).  
5. FantasyPros API (optional overlay; free tier limited).  

No third-party blog is cited as a method we implemented. Marginal lift and Phase-2
structural strategies are original to this repo.
