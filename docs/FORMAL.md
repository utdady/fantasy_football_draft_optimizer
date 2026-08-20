# Formal integrity

> **Lean can prove that our experiment means what we say it means. It cannot prove that our data is truthful.**
>
> Python tells us what happened. Statistics tell us whether it is reproducible. Lean tells us whether we accidentally changed the question while measuring it.

This is an **integrity track**, not a version gate. Production TAKE stays frozen `marginal`. The next research lever remains **Autopsy Gate 2** (live_sim classification). See [`LAB_LOG.md`](LAB_LOG.md), [`HARNESS_SPEC.md`](HARNESS_SPEC.md), [`../results/AUTOPSY_GATE.md`](../results/AUTOPSY_GATE.md).

---

## Division of labour

```text
              DRAFT OPTIMIZER RESEARCH
                         |
          +--------------+--------------+
          |                             |
       Python                         Lean
          |                             |
   empirical science             formal integrity
          |                             |
   projections / ADP             dependency rules
   marginal / lineup             evaluation invariants
   Phase-2 ladders               snapshot cutoff types
   autopsy / live_sim            legality certificates
   calibration fits
          |                             |
          +--------------+--------------+
                         |
                         v
                  TRUSTWORTHY RESULTS
```

| Question | Tool |
|---|---|
| Is every drafted roster slot-legal? | Yes — later, as a certificate check |
| Does FLEX assignment match `lineup_ev`? | Yes — later |
| Does a recommender *type* exclude outcomes? | Yes |
| Do scoring contrasts mean what we claim (B-A, C-B, D-C)? | Yes |
| Is ADP calibration calibrated? | No — empirical (V3-A) |
| Does V2 beat `marginal`? | No — empirical (after Gate 2) |
| Did decision feeds leak past snapshot_date? | Provenance / leakage module, not a type theorem |
| Is Josh Allen the optimal 1.01? | No — model-dependent |

Lean is not used to prove football. It is used to protect definitions and dependency graphs.

---

## Three dependency graphs

Do not collapse these into one "no extra information" rule.

| Artifact | May depend on | Must not depend on |
|---|---|---|
| `recommend(Snapshot T)` / strategy pick | fields permitted at cutoff T | actual season PPR; post-cutoff news |
| Leakage / `evaluable` labels | structure, timestamps, declared flags | challenger scores, MAE, Δ, regret |
| Autopsy category tags | human log + board state at pick time | post-hoc outcome cherry-picks presented as causes |

`evaluable` and leakage are **evaluation-time / snapshot-meta** classification. They may use structural facts. They must not be set from "strategy X lost on this board."

Pre-registered leakage rule: `source_as_of <= snapshot_date` on every decision feed row (`draftopt.phase2.leakage`).

---

## Identical feasible set is not identical experiment

For a fair strategy compare, every challenger shares the same:

- player pool / identity map
- league slot set
- opponent policy + paired seeds
- scoring contract (e.g. `ppr_eval_v1_2024`)

Objective, value curve, and construction are **separate declarations**.

Changing only `season_points` (C → D) while holding construction fixed is a valid calibration counterfactual. Changing construction on top of D (V3-B) is a different experiment — already closed.

---

## What we will not formalize

- That C-B > 0 or D-C > 0 "proves" TAKE should change
- Calibration quality, MAE, win rates, autopsy category frequencies
- Solver / sort optimality of greedy `lineup_ev` beyond legality + reconstructed objective
- "Allen is better than Gibbs" as a theorem

Those remain empirical or product judgments.

---

## Implementation sequence

Not a version gate. Do not block Autopsy Gate 2 on this.

```text
NOW
  docs/FORMAL.md (this file)
  existing: leakage.py, evaluable.py, validate_snapshot

NEXT (property tests in pytest)
  + shuffle/replace strategy recommendations
    -> evaluable / leakage labels unchanged
  + outcome attach only after player_id draft complete
  + identical slot set / pool across A/B/C/D compares
  + lineup assignment: fixed slots then FLEX; bench ignored for EV
  + (if defined) autopsy / regret identities name their oracle

LATER (optional Lean core under formal/)
  + Snapshot.lean / RecommendCutoff.lean
  + EvaluableIndependence.lean
  + LineupLegality.lean
  + Regret.lean (only if a nested-oracle identity is kept)

OPTIONAL
  certificate checker for roster legality if bugs recur
```

Property tests come first. They are the executable invariant. Lean polishes the same claims.

Suggested first tests:

1. Mutate / shuffle strategy scores on a frozen snapshot; `evaluable` and leakage findings must be identical.
2. Assert `recommend` code paths never import or query outcome tables (static or runtime guard).
3. Assert paired ladder runs use the same `player_id` pool and slot dict.
4. Assert `lineup_ev` totals equal sum of assigned starter points under the slot rules.

Queued as a future lab entry (see [`LAB_LOG.md`](LAB_LOG.md) E-FORMAL).
