# P2.2 — Historical sources + outcome ingest

**Status:** Stage A feasibility spike ran (2024). **Not evaluable.**

**Depends on:** P2.1 pipeline proof ✅ · flags `pipeline_proof` / `evaluable` ✅

---

## Terminology

| Kind | Flags | Use |
| --- | --- | --- |
| **PIPELINE PROOF** | `pipeline_proof=1`, `evaluable=0` | Ingest + leakage only. Example: `2026-preseason-2026-08-12` |
| **STAGE A / SOURCE VALIDATION** | `evaluable=0`, `validation_status=source_validation` | FFC+nflverse+mapping; no strategy claims |
| **EVALUATION SNAPSHOT** | `pipeline_proof=0`, `evaluable=1`, `outcome_season` set | Replay + actual PPR scoring (requires Gate 4 projections) |

```powershell
python -m draftopt.phase2.assert_evaluable 2024-preseason-2024-09-01-ffc-pending
# → REFUSE (exit 1)
```

---

## Stage hierarchy (locked)

| Stage | Question | `evaluable` |
| --- | --- | --- |
| **A — Feasibility** | Trustworthy historical ADP + outcomes + ID map? | always `0` |
| **B — Scientific eval** | A + **dated historical projections**? | `1` only then |
| **C — Proxy** | ECR→proj only if B impossible, labeled separately | never default |

---

## 2024 spike result

Report: [`phase2_p22_feasibility_2024.md`](phase2_p22_feasibility_2024.md)

| Gate | Result |
| --- | --- |
| FFC ADP provenance (10-team request) | **FAIL** — `adp_league_size_mismatch` (meta.teams=**12**) |
| FFC dating | Window `2024-08-31`→`2024-09-01`; as_of=`end_date` is interpretable |
| Player mapping | **PASS** 179/205 (87.3%), name-only=**0**, unresolved retained |
| Outcome coverage | **PASS** 178/179 mapped-with-gsis (99.4%) |
| Historical projections | **FAIL** — not in scope for Stage A |
| `evaluable` | **0** |

Primary reason stored: `adp_league_size_mismatch` (also `historical_projection_missing`).

This is a **successful fail-closed experiment** for 10-team FFC: dated window exists, but the API returned 12-team meta for a 10-team request. Do not promote to evaluable.

```powershell
pip install -e ".[eval]"
# If Cloudflare blocks FFC, save JSON in browser then:
python -m draftopt.phase2.feasibility_spike --year 2024 --teams 10 --raw-json data/raw/ffc_adp_ppr_10tm_2024.json
```

---

## Candidate sources

### Decision-time ADP

| Source | Historical as_of? | Notes |
| --- | --- | --- |
| **FFC** | `meta.start_date` / `end_date` window | 2024 dated; **league-size param not honored** in observed pull |
| FantasyPros ECR archive | scrape dates when present | Rank ≠ ADP |
| Archived ESPN pulls | only if we saved dated files | |

### Outcomes

| Source | Notes |
| --- | --- |
| **nflverse / nflreadpy** | Weekly stats → `week_ppr_points()` → season total (`nflverse_computed`) |

### Soft join

FFC → DynastyProcess name+pos(+team) → canonical `player_id` + `gsis_id` → nflverse. Unresolved rows in `eval_player_unresolved`. **No name-only joins.**

---

## Explicit non-goals (Stage A)

- Draft replay / ADP vs `marginal`
- VOR / V2 / β
- Setting `evaluable=1`
- Using current ESPN projections for 2024 players

---

## Next: P2.2B projection audit

See [`PHASE2_P22B_PROJECTION_AUDIT.md`](PHASE2_P22B_PROJECTION_AUDIT.md).

Gate 4 (dated historical `proj_ppr`) is the blocker for `evaluable=1`. ESPN live API cannot time-travel; Clay PDF / FantasyPros API are the leading probes; ECR≠projections.
