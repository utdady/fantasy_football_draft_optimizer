# Experiment Log

Living record of hypotheses, tests, and results. **Append new experiments; do not rewrite old verdicts.** If a later test overturns an earlier one, add a new row and link back.

Related specs: [`../ROADMAP.md`](../ROADMAP.md), [`PROJECT.md`](PROJECT.md), [`HARNESS_SPEC.md`](HARNESS_SPEC.md), [`FORMAL.md`](FORMAL.md), [`../results/AUTOPSY_GATE.md`](../results/AUTOPSY_GATE.md).

Production TAKE (`marginal`) stays frozen until a gated experiment says otherwise.

**Authority:** this log wins over `ROADMAP.md` if they disagree. Detailed tables often live under `results/`; this file holds the verdict spine.

---

## Two freezes

**Production freeze** — V1 `marginal` recommendation, ESPN projection path, lineup EV, autodraft TAKE. Generates live picks.

**Research calendar** — Phase-2 ladders, V3-A/B, autopsy, FP overlay. May run anytime. Informs **post-classification** development only.

> Research can change our beliefs during the draft season. It cannot change frozen TAKE without an explicit promotion gate.

| May modify | May NOT modify |
|---|---|
| Hypotheses, V2 priorities, autopsy categories, docs | Production `marginal` code path used by TAKE |
| Offline strategies / Phase-2 DBs | Silent UI strategy swaps |
| Disagreement logs | Autopsy stub retunes before Gate 2 says so |

---

## How to add a future test

1. Copy the template below into **Queued**, assign the next `E0xx` id.
2. When you run it, move it to **Completed**, fill Results / Verdict / Artifacts.
3. Update the **Hypothesis board** status (`open` / `supported` / `weak` / `rejected` / `contaminated` / `preliminary`).
4. Do not delete old experiments. Note contamination instead.

### Template

```md
### E0xx — short title
- **Date:** YYYY-MM-DD
- **Status:** queued | running | completed
- **Hypothesis:** H?
- **Question:** one sentence
- **Method:** command / setup / information cutoff
- **Metrics:**
- **Results:**
- **Verdict:**
- **Artifacts:**
- **Follow-up:**
```

---

## Hypothesis board

| ID | Claim | Status | Evidence |
|---|---|---|---|
| **H-marginal-v1** | FLEX-aware ESPN marginal is a coherent production baseline | **supported** | Ship readiness; live UI |
| **H-C-B** | Structural valuation beats ADP-feasible on 2024 starter PPR (after feasibility/DST controls) | **preliminary** | P22C ladder; `evaluable=0` |
| **H-V3A** | Frozen 2021–2023 ADP calibration (D) improves mean vs structural (C) | **supported / frozen** | V3-A ladder; left-tail tradeoff |
| **H-V3B** | Licensed construction overlays beat D | **rejected** | V3-B closeout `6ad702b` |
| **H-V2-alpha** | Two-pick EV / survival stubs should ship into TAKE | **not authorized** | V2 baseline + Gate 1 |
| **H-V2-beta / robust** | Mixture or min_f as final objective | **rejected** | `V2_BETA.md` |
| **H-autopsy-oc** | Live disagreements are dominated by opportunity-cost / survival | **open** | Gate 2 |
| **H-autopsy-policy** | Live disagreements are preference (e.g. no early QB) | **open** | Gate 2 |
| **H-autopsy-data** | Live disagreements are stale / bad projections | **open** | Gate 2 |
| **H-external** | Phase-2 / V3 results generalize beyond 2024 FFC harness | **open** | Not established |

---

## Completed experiments

### E001 — 2026 draft readiness (frozen marginal)
- **Date:** 2026-08-17
- **Status:** completed
- **Hypothesis:** H-marginal-v1
- **Question:** Is the live DB + `marginal` TAKE ready for continued mock / live_sim use?
- **Method:** `draftopt.ship_readiness` on `data/draftopt.db`; full mock slot 1 seed 42; snipe/undo/latency gates
- **Metrics:** check pass count; recommend latency vs 60s clock; projection/ADP coverage
- **Results:** 20/20 (later 25/25 with skill-proj gate) PASS; p95 recommend ~15ms
- **Verdict:** Production baseline is shippable for UX / autopsy work. Not a construction or Phase-2 claim.
- **Artifacts:** `results/SHIP_2026_DRAFT_READINESS.md`, `results/SHIP_2026_SOURCE_VERIFY.md`
- **Follow-up:** live_sim + autopsy; do not reopen V3-B

### E002 — Phase-2 pipeline proof + historical design freeze
- **Date:** 2026-08 (design + P2.1)
- **Status:** completed (pipeline proof)
- **Hypothesis:** as-of-T snapshots can be frozen and leakage-checked
- **Question:** Can we freeze a decision-time snapshot that validates ingest/leakage without claiming evaluable outcomes?
- **Method:** `phase2.freeze_snapshot` / `validate_snapshot`; design in `PHASE2_HISTORICAL_EVAL.md`
- **Metrics:** leakage pass/fail; `evaluable` gate refusal on pipeline-proof ids
- **Results:** `2026-preseason-2026-08-12` pipeline proof; `evaluable=0`
- **Verdict:** Capture path works. Evaluation claims require `evaluable=1` + outcomes.
- **Artifacts:** `results/PHASE2_HISTORICAL_EVAL.md`, `results/PHASE2_P21_SNAPSHOT.md`, `results/phase2_validate_*.md`
- **Follow-up:** P22 sources → structural ladder

### E003 — P22C ADP → feasible → structural ladder (2024 actual PPR)
- **Date:** 2026-08
- **Status:** completed
- **Hypothesis:** H-C-B
- **Question:** After feasibility, does structural valuation still beat ADP-feasible under 2024 starter PPR?
- **Method:** Paired boards on snapshot `2024-preseason-2024-09-01-ffc12`, contract `ppr_eval_v1_2024`; strategies A/B/C
- **Metrics:** mean/median Δ, win rate; full starter and ex-DST; DST fill rates
- **Results (headline):** Feasibility B−A mean ≈ +53.7 (full); **valuation C−B mean ≈ +76.5**, WR 67% (full). Ex-DST C−B still positive (~+67.8). `evaluable=0`.
- **Verdict:** **Preliminary support** for structural valuation after controls. Not a TAKE promotion. Closeout pointed V3-A (calibration) over TE/QB special cases.
- **Artifacts:** `results/phase2_p22c_adp_feasible_ladder.md`, `results/PHASE2_P22C_ADP_STRUCTURAL.md`, `results/phase2_p22c_closeout.md`
- **Follow-up:** V3-A calibration gates; do not fix TE/QB specifically from symmetry

### E004 — V3-A calibration (D vs C)
- **Date:** 2026-08
- **Status:** completed / frozen
- **Hypothesis:** H-V3A
- **Question:** Does a train-only (2021–2023) ADP→value map improve 2024 starter PPR vs structural under identical construction?
- **Method:** Gates 1–4 pre-registered; isotonic per-position maps; D = `adp_v3a`; compare D−B, D−C; leakage audit
- **Metrics:** mean/median Δ, WR, p10/p90; train MAE improvement
- **Results:** D−C mean ≈ +22.1, WR 55%, p10 ≈ −268 (fat left tail). Train MAE improved (~87.8→54.3). Flags: mean-up / left-tail-worse tradeoff.
- **Verdict:** **Supported as frozen instrument / control D.** Not a clean free lunch; not a UI ship decision; do not retune map from 2024 Δ.
- **Artifacts:** `results/V3A_CALIBRATION_DESIGN.md`, `results/phase2_v3a_ladder.md`, `results/phase2_v3a_gate1_*.md` … `gate4_*.md`
- **Follow-up:** V3-B construction menu against D

### E005 — V3-B construction program vs D
- **Date:** 2026-08
- **Status:** completed / closed
- **Hypothesis:** H-V3B
- **Question:** Do licensed construction overlays (B.0 / B.1 / A / B) beat frozen D on 2024 starter PPR?
- **Method:** Pre-registered branch menu; ladders + mechanism audits; checkpoint `6ad702b`
- **Metrics:** pick divergence; mean Δ vs D; mechanism diagnosis
- **Results:** B.0 harmful (−24.3); B.1 inert (0/60); A inert (0/60); B active but harmful (−57.5, WR 37%)
- **Verdict:** **Entire V3-B program closed.** No construction retune. Does not falsify V3-A. Escape hatches (CVaR, V2 revive, map retune, subsetting) explicitly forbidden as V3-B follow-ups.
- **Artifacts:** `results/PHASE2_V3B_CLOSEOUT.md`, `results/phase2_v3b*_*.md`, design spine `V3B_*.md`
- **Follow-up:** Autopsy / live classification — not more construction knobs

### E006 — Autopsy Gate 1 (empty 1.01 Allen / Gibbs / Puka)
- **Date:** 2026-08
- **Status:** completed / closed
- **Hypothesis:** H-V2-alpha (production ship?)
- **Question:** On empty board 1.01, is `marginal` strange, and does stub two-pick EV authorize V2?
- **Method:** `draftopt.autopsy` on draft `eb8374278e41`; frozen stubs
- **Metrics:** M scores; stub two-pick EV
- **Results:** Allen 369.21 > Gibbs 365.27 > Puka 356.57. Stub 2-pick EV prefers Gibbs (~688 vs Allen ~642). Same long-wait V2-alpha family already failed production bar.
- **Verdict:** Gate 1 **closed** (pass / inconclusive). Explains human Gibbs preference without authorizing V2. Forbidden: more empty-board Allen/Gibbs variations.
- **Artifacts:** `results/autopsy_r1.md`, `results/AUTOPSY_GATE.md` (`04d7304`, `a68346e`)
- **Follow-up:** Gate 2 live_sim

---

## Queued / in progress

### E007 — Autopsy Gate 2 (live_sim disagreements)
- **Date:** open
- **Status:** running / NEXT
- **Hypothesis:** H-autopsy-oc / H-autopsy-policy / H-autopsy-data
- **Question:** On real live_sim boards, what failure modes dominate human vs TAKE disagreements?
- **Method:** Do not manufacture cases. Dump case + log disagree as felt. Include controls where TAKE feels right. Categories: `opportunity_cost`, `bad_data`, `roster_construction`, `human_policy`, `uncertainty`, `rec_sensible`, `other`.
- **Metrics:** Distinct mode counts (not arbitrary N=100); qualitative cluster among first ~15 awkward decisions
- **Results:** —
- **Verdict:** —
- **Artifacts:** `results/autopsy_cases/`, `results/autopsy_disagreements.jsonl`, protocol `results/AUTOPSY_GATE.md`
- **Follow-up:** Only a consistent opportunity-cost cluster earns real survival-model engineering (Path A/B). Preference cluster → Path C. Sensible TAKE → leave `marginal`.

```powershell
python -m draftopt.autopsy case --draft-id <id>
python -m draftopt.autopsy analyze --draft-id <id> --players "A,B,C" --out results/autopsy_<label>.md
python -m draftopt.autopsy disagree --draft-id <id> --recommended "..." --chosen "..." --category ... --reason "..."
```

### E-FORMAL — Evaluation-integrity property tests
- **Date:** after Gate 2 is underway is fine; not a blocker
- **Status:** queued
- **Hypothesis:** evaluation protocol is independent of model predictions
- **Question:** Do `evaluable`, leakage findings, and lineup scoring identities keep their stated dependencies?
- **Method:** pytest property tests first ([`FORMAL.md`](FORMAL.md)); optional Lean later
- **Metrics:** labels identical after recommendation shuffle; no outcome imports in recommend path; shared feasible set on ladders
- **Results:** —
- **Verdict:** —
- **Artifacts:** `docs/FORMAL.md`; tests TBD
- **Follow-up:** Lean `formal/` only after property tests exist

---

## Current call (do not skip when adding tests)

As of 2026-08-20:

1. **Production freeze intact.** TAKE = `marginal`. No survival / VOR / construction / FP-as-rank in TAKE.
2. **H-C-B preliminary; H-V3A frozen; H-V3B rejected.**
3. **Autopsy Gate 1 closed.** Do not rerun empty-board Allen/Gibbs.
4. **NEXT = E007 Gate 2.** Classify live disagreements before any Path A/B/C engineering.
5. **Autopsy stubs stay frozen** until Gate 2 says opportunity cost dominates.
6. **E-FORMAL** is parallel integrity work — not a version gate.

---

## Index of commands

```powershell
# Live
python -m draftopt.ingest
python -m draftopt.serve
python -m draftopt.fp_overlay
python -m draftopt.ship_readiness

# Autopsy
python -m draftopt.autopsy case --draft-id <id>
python -m draftopt.autopsy analyze --draft-id <id> --players "A,B,C" --out results/autopsy_<label>.md
python -m draftopt.autopsy disagree --draft-id <id> --recommended "..." --chosen "..." --category ... --reason "..."

# Synthetic lab (ESPN proj scoring)
python -m draftopt.backtest --n 50 --slot 1 --seed 0

# Phase-2 harness
python -m draftopt.phase2.freeze_snapshot
python -m draftopt.phase2.validate_snapshot <snapshot_id>
python -m draftopt.phase2.assert_evaluable <snapshot_id>
```
