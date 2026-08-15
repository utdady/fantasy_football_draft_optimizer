# Phase 2 — Historical evaluation (design + schema stubs)

**Status:** design freeze for Phase 2 MVP. **No V3/β3 strategies.** Phase 1 algorithms remain research-only; UI stays `marginal`.

**Parent objective note:** [`V2_OBJECTIVE_DESIGN.md`](V2_OBJECTIVE_DESIGN.md)

---

## Scientific upgrade

| Phase 1 (done) | Phase 2 (next) |
| --- | --- |
| Better roster under **our projection model** | Better roster under **actual season fantasy points** |
| CPU policies = research lab | CPU / ADP sim = evaluation harness |
| Model evidence | Fantasy evidence |

Question Phase 2 answers:

> Given only information available on snapshot date \(T\), does strategy \(S\) build a roster that subsequently scores more **actual** PPR points?

---

## Architecture (locked)

```text
┌─────────────────────┐
│ Decision-time DB    │  ADP, projections, pool, dates
└──────────┬──────────┘
           │  recommend()  ← ZERO access to outcomes
           ▼
    simulated draft (player IDs only)
           │
           ▼
┌─────────────────────┐
│ Outcome DB          │  actual season PPR (independent)
└──────────┬──────────┘
           │  score after draft complete
           ▼
     realized starter points
```

### Hard rules

1. **`recommend()` must have zero access to the outcome database.**
2. Soft join only: draft emits **`player_id`s**; outcomes attach later.
3. Leakage constraint (pipeline hard-fail, not README hope):

\[
\texttt{source\_as\_of} \le \texttt{snapshot\_date}
\]

4. Outcome scoring uses the **same roster slots** as the league (PPR: QB, 2 RB, 2 WR, TE, 2 FLEX, DST, …).
5. Phase 1 synthetic simulator is retained as a **lab**, not as the definition of success.
6. **Optimizer vs evaluator information** (record on every experiment):

| Data | Optimizer? | Evaluator? |
| --- | ---: | ---: |
| Preseason ADP (dated) | ✅ | — |
| Preseason projection (dated) | ✅ | — |
| Draft slot / league settings | ✅ | — |
| Actual season PPR | ❌ | ✅ |
| In-season injuries / weekly news | ❌ | ❌* |
| End-of-season rankings | ❌ | ❌* |

\*Unless the experiment is explicitly an in-season system.

Label markets honestly: **FFC ADP ≠ ESPN ADP**, **12-team ≠ 10-team**, **ECR ≠ `proj_ppr`**, **ADP-as-curve ≠ ESPN `proj_ppr`**.

---

## Milestones (do in order)

| ID | Milestone | Done when |
| --- | --- | --- |
| **P2.1** | Historical snapshot ingestion | ✅ `2026-preseason-2026-08-12` frozen + validate PASS (**pipeline proof**, `evaluable=0`) |
| **P2.2** | Outcome + projection path | 🟡 **2A** done · **2B CLOSED** (FP free API) · **2C** ADP-structural methodology frozen ([`PHASE2_P22C_ADP_STRUCTURAL.md`](PHASE2_P22C_ADP_STRUCTURAL.md)) |
| **P2.3** | Leakage validator | ✅ module + snapshot gate (`validate_snapshot`) |
| **P2.4** | Historical draft replay | Existing strategies draft from an **`evaluable=1`** snapshot only |
| **P2.5** | Outcome scoring | Rosters → actual starter PPR |
| **P2.6** | Baseline comparison | ADP vs `marginal` on actual points |
| **P2.7** | VOR / V2 experiments | Only after P2.1–P2.6 are green |

**Do not start P2.7 before P2.3.** Contaminated pipelines waste more time than slow data work.

### Snapshot kinds

| Kind | Flags | Allowed for |
| --- | --- | --- |
| **PIPELINE PROOF** | `pipeline_proof=1`, `evaluable=0` | Ingest / leakage validation only |
| **EVALUATION** | `pipeline_proof=0`, `evaluable=1`, `outcome_season` set | Replay, scoring, ADP vs `marginal` |

Hard gate: `draftopt.phase2.require_evaluable(conn, snapshot_id)` — raises
`SnapshotNotEvaluable` otherwise. Never mutate a frozen id’s meaning; mint a
new dated id if you need a different cut.

### First MVP cut

One frozen preseason snapshot is enough to prove the pipeline. Prefer a past
season once historical ADP/proj sources are wired; until then, freezing the
current live ingest (with `pulled_at` as `as_of`) is a valid **P2.1 pipeline
proof** — outcomes (P2.2) wait until actual season points exist.

```powershell
# Freeze live ESPN ADP/proj into data/draftopt_eval.db (defaults: pipeline_proof)
python -m draftopt.phase2.freeze_snapshot

# Validate (must PASS before P2.2)
python -m draftopt.phase2.validate_snapshot 2026-preseason-2026-08-12

# Evaluation gate must REFUSE this id
python -m draftopt.phase2.assert_evaluable 2026-preseason-2026-08-12
```

---

## Logical tables

### Decision-time

**`eval_snapshots`**

| Column | Meaning |
| --- | --- |
| `snapshot_id` | PK |
| `season` | NFL season year |
| `snapshot_date` | ISO date — decision cutoff |
| `label` | e.g. `2024-preseason-late-aug` |
| `notes` | free text |
| `pipeline_proof` | 1 = ingest/leakage proof only |
| `evaluable` | 1 = allowed for replay/scoring |
| `outcome_season` | season year for actual PPR (required if evaluable) |
| `validation_status` | e.g. `source_validation` |
| `validation_reason` | e.g. `adp_as_of_unverified`, `historical_projection_missing` |

**`eval_snapshot_players`**

| Column | Meaning |
| --- | --- |
| `snapshot_id` | FK |
| `player_id` | FK → `players` |
| `position` | as-of snapshot |
| `team` | as-of snapshot |
| `adp` | decision-time ADP |
| `adp_source` | e.g. `espn`, `ffc` |
| `adp_as_of` | timestamp ≤ snapshot_date |
| `proj_ppr` | decision-time season projection |
| `proj_source` | e.g. `espn` |
| `proj_as_of` | timestamp ≤ snapshot_date |

### Outcome (separate concern)

**`eval_outcomes`**

| Column | Meaning |
| --- | --- |
| `season` | |
| `player_id` | |
| `actual_ppr_points` | season total (or week-sum source of truth) |
| `games_played` | optional |
| `source` | e.g. `nflverse` |
| `pulled_at` | ingest time (not used as decision input) |

### Replay artifacts

**`eval_drafts`** / **`eval_picks`**

| Column | Meaning |
| --- | --- |
| `eval_draft_id` | |
| `snapshot_id` | which decision world |
| `strategy` | `adp`, `marginal`, … |
| `slot`, `seed`, `n_teams`, … | |
| picks: `overall`, `player_id`, `made_by` | player IDs only |

Outcomes attach only in a **scoring** step that reads picks + `eval_outcomes`.

---

## Schema stubs (code)

See `src/draftopt/phase2/`:

- `schema.py` — DDL + `migrate_eval_schema` (flag columns)
- `leakage.py` — validator: every decision row must satisfy `*_as_of ≤ snapshot_date`
- `evaluable.py` — `require_evaluable` hard gate for runners
- `mark_snapshot.py` — set `pipeline_proof` / `evaluable` / `outcome_season`
- `freeze_snapshot.py` / `validate_snapshot.py` — P2.1 freeze + validate

Apply deliberately when implementing P2.1 (separate eval DB path recommended: e.g. `data/draftopt_eval.db` vs live `data/draftopt.db`).

---

## Promotion bar (not yet)

Nothing ships to UI from Phase 1 alone.

First promotion-worthy claim looks like:

> Across \(X\) independent preseason snapshots and \(Y\) draft slots, strategy A produces higher **actual** season-long fantasy points than ADP, under leakage-safe evaluation.

Until then: **model evidence**, not fantasy evidence.

---

## Explicit non-goals (for now)

- Reconstructing private league historical pick-by-pick boards
- Training λ / CVaR / β3 against Phase 1 stress CPUs
- Changing production default off `marginal`
