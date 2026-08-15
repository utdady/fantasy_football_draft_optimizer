# P2.1 — Frozen preseason snapshot

**Status:** PASS (pipeline proof only)

| Field | Value |
| --- | --- |
| snapshot_id | `2026-preseason-2026-08-12` |
| season | 2026 |
| snapshot_date | 2026-08-12 |
| **pipeline_proof** | **1** |
| **evaluable** | **0** |
| outcome_season | null |
| players | 800 |
| eval DB | `data/draftopt_eval.db` (gitignored) |
| validation | [`phase2_validate_2026-preseason-2026-08-12.md`](phase2_validate_2026-preseason-2026-08-12.md) |

Frozen from live ESPN ADP + projections (`pulled_at` → `as_of`). This is a
**PIPELINE PROOF** for ingest + leakage — **not** an evaluation snapshot.
Evaluation runners refuse it via `require_evaluable()`.

```powershell
python -m draftopt.phase2.freeze_snapshot
python -m draftopt.phase2.validate_snapshot 2026-preseason-2026-08-12
python -m draftopt.phase2.mark_snapshot 2026-preseason-2026-08-12 --pipeline-proof 1 --evaluable 0
python -m draftopt.phase2.assert_evaluable 2026-preseason-2026-08-12
# → REFUSE (expected)
```

Next: **P2.2** — historical evaluation snapshot + outcomes
([`PHASE2_P22_SOURCES.md`](PHASE2_P22_SOURCES.md)). Do not claim strategy wins
on actual points until `evaluable=1`.
