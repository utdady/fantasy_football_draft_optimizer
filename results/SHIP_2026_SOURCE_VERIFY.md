# 2026 live source verification (shipping prep)

**As of:** 2026-08-15  
**Purpose:** Verify V0 ingest sources for the production `draftopt.db` path.
Phase-2 historical DBs stay frozen / untouched.

---

## Summary

| Source | Live for 2026? | Usable by current ingest? | Notes |
| --- | --- | --- | --- |
| **Sleeper** players + state | ✅ | ✅ | `season=2026`, `season_type=pre` |
| **DynastyProcess** IDs | ✅ | ✅ | 8308 id rows |
| **DynastyProcess** FP ECR | ✅ | ✅ | 576 ECR rows; `scrape_date=2026-08-14` |
| **ESPN** kona_player_info `seasons/2026` | ✅ endpoint | ⚠️ **parser bug** | ADP + ranks OK; **season proj may latch 2025** |
| **FantasyPros** web ADP/ECR | ✅ site | ⚠️ not primary ingest | 2026 PPR ADP live; full table often gated |
| **FFC** ADP API | ❌ here | known | HTTP **403** Cloudflare (unchanged) |

**Ship gate implication:** ESPN `seasonId` latch is **fixed** (`espn._season_projection`
prefers config `SEASON`). Live DB re-ingested **2026-08-15T16:18:27Z** — Gibbs season
proj **365.3** (was latching ~317 from 2025). Phase-2 DB hashes unchanged.

---

## Probes (this check)

### Sleeper
- `GET https://api.sleeper.app/v1/state/nfl` → `league_season` / `season` **2026**, `season_type` **pre**
- `GET .../players/nfl` → **12,218** players; skill counts present; **458** with `years_exp=0`; injury statuses populated; **2,312** skill players with `espn_id`

### DynastyProcess
- `db_playerids.csv` → **200 OK**, 8308 parsed rows
- `db_fpecr_latest.csv` → **200 OK**, 576 ECR rows  
  Sample: scrape_date **`2026-08-14`** (fresh)

### ESPN (config URL already points at 2026)
```
.../games/ffl/seasons/2026/segments/0/leaguedefaults/3?view=kona_player_info
```
- **800** players with `ownership.averageDraftPosition` and PPR draft ranks
- Top ADP matches market (Gibbs ~1.57, Bijan ~2.6, …)
- Season projection blocks include **both** `seasonId=2025` and `seasonId=2026`
- Current `_season_projection()` **prefers `seasonId == SEASON` (2026)**; prior-year
  blocks are fallback only (fixed 2026-08-15).
- Re-ingest validation: Gibbs **365.3**, Bijan **353.0**, Puka **356.6** (2026 totals).

### FantasyPros (browser)
- [PPR ADP](https://www.fantasypros.com/nfl/adp/ppr-overall.php): title **“PPR Leagues 2026”**; season control **2026**; sources ESPN/CBS/Sleeper/…; top names Gibbs / Bijan / Chase / Puka / CMC
- Consensus cheatsheets page titled **2026**; Rookies nav present
- Full ADP detail often behind signup — fine; production path uses DP ECR mirror + ESPN, not scraping FP HTML

### FFC
- `fantasyfootballcalculator.com/api/v1/adp/ppr?teams=10&year=2026` → **403** in this environment (same class of blocker as `DATA_SOURCES.md`)

---

## Live `draftopt.db` (production path)

| Field | Value |
| --- | --- |
| Path | `data/draftopt.db` |
| Players | 859 |
| Last ADP/proj pull | **2026-08-15T16:18:27Z** (post seasonId fix) |
| ESPN ADP rows | 800 |
| ESPN proj rows | 777 (Gibbs **365.3** — 2026 season total) |
| ECR rows | 511 |
| Top ADP | Gibbs, Bijan, Puka, Chase, JSN — market-shaped |

**Do not mutate** `data/draftopt_p22c*.db` / V3-A research DBs during the refresh.

---

## Recommended Days 1–3 actions (ordered)

1. ~~**Fix** `espn._season_projection` to prefer `seasonId == 2026`~~ **Done**
2. ~~Run `python -m draftopt.ingest` into live `draftopt.db`~~ **Done** (`2026-08-15T16:18:27Z`)
3. Validate V0 gate in UI mock draft (ADP + 2026 proj + ECR + injury + DST/K)
4. Optional later: FP official API / FFC if 403 clears — not required to mock-draft

---

## Explicit non-goals from this check

- No construction retune / V3 reopen
- No baking rookie capital into `marginal`
- No Phase-2 DB mutation
