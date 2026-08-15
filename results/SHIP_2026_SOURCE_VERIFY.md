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

**Ship gate implication:** Days 1–3 should re-ingest live DB **after** fixing ESPN `seasonId` selection. Do not treat a naive `python -m draftopt.ingest` as 2026-ready until that fix lands.

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
- Current `_season_projection()` takes the **first** `scoringPeriodId==0` / `statSourceId==1` match → for top players that is **2025** (e.g. Gibbs **317** vs 2026 **365**)
- **20/20** of top owned players checked: first-match year ≠ 2026

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
| Last ADP/proj pull | **2026-08-12T17:13:09Z** (~3 days stale) |
| ESPN ADP rows | 800 (mean ADP ~153) |
| ESPN proj rows | 774 (mean season_points ~75.5 — suspiciously low for full-season PPR; consistent with mixed/prior-year latch risk + deep bench) |
| Top ADP | Gibbs, Bijan, Puka, Chase, JSN — market-shaped |

**Do not mutate** `data/draftopt_p22c*.db` / V3-A research DBs during the refresh.

---

## Recommended Days 1–3 actions (ordered)

1. **Fix** `espn._season_projection` to prefer `seasonId == 2026` (config/season arg), never silently accept prior year.
2. Run `python -m draftopt.ingest` into **live** `draftopt.db` only; leave `data/draftopt_p22c*.db` alone.
3. Validate V0 gate: ADP + 2026 proj coverage, ECR join rate, injury join, DST/K stubs.
4. Optional later: FP official API / FFC if 403 clears — not required to mock-draft with ESPN+Sleeper+DP.

---

## Explicit non-goals from this check

- No construction retune / V3 reopen
- No baking rookie capital into `marginal`
- No Phase-2 DB mutation
