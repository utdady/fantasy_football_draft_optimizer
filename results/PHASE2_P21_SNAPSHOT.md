# P2.1 — Frozen preseason snapshot

**Status:** PASS

| Field | Value |
| --- | --- |
| snapshot_id | `2026-preseason-2026-08-12` |
| season | 2026 |
| snapshot_date | 2026-08-12 |
| players | 800 |
| eval DB | `data/draftopt_eval.db` (gitignored) |
| validation | [`phase2_validate_2026-preseason-2026-08-12.md`](phase2_validate_2026-preseason-2026-08-12.md) |

Frozen from live ESPN ADP + projections (`pulled_at` → `as_of`). This is a
**pipeline proof** for the current preseason; **P2.2 actual outcomes** are not
available until after the 2026 season (or until a past-season snapshot is added).

```powershell
python -m draftopt.phase2.freeze_snapshot
python -m draftopt.phase2.validate_snapshot 2026-preseason-2026-08-12
```

Next: **P2.2** outcome ingestion (prefer a completed season once historical
sources are wired; do not leak outcomes into `recommend()`).
