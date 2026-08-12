# Data Sources Checklist

League assumptions for V0: **10-team · PPR · snake · redraft · ESPN**.

Layers (do not mix in code):

1. **Identity / state** — who the player is, injury, team, bye  
2. **Market** — ADP / draft price  
3. **Expectation** — projections / rankings / uncertainty  
4. **Derived (ours)** — VOR, marginal lineup value, survival, etc.

---

## V0 — use these first (easy / verified)

| Status | Source | Layer | What we pull | Access | Notes |
|--------|--------|-------|--------------|--------|-------|
| [ ] | **Sleeper API** | Identity / state | Players map, team, pos, status, injury fields, depth, `espn_id`, trending | Free, no auth · cache ≤1×/day | `GET https://api.sleeper.app/v1/players/nfl` |
| [ ] | **DynastyProcess `db_playerids`** | Identity | Crosswalk: Sleeper / ESPN / FantasyPros / Yahoo / PFR / … | Free CSV / `nflreadpy.load_ff_playerids()` | Canonical join spine |
| [ ] | **DynastyProcess `db_fpecr_latest`** | Expectation | FantasyPros PPR ECR, `sd`, best, worst, bye, scrape date | Free CSV / `nflreadpy.load_ff_rankings("draft")` | Filter `ppr-cheatsheets` / `redraft-overall`. Mirror, not live ADP |
| [ ] | **ESPN fantasy (public/undocumented)** | Market + expectation | ESPN ADP, PPR draft rank, season proj (`appliedTotal`), % owned | Public GET + `X-Fantasy-Filter` | Adapter only — can break. Personal use |

### V0 minimum fields to land in our DB

- [ ] `player_id` (ours) + `sleeper_id` + `espn_id` + `fantasypros_id` (when present)
- [ ] `name`, `position`, `team`, `bye`
- [ ] `injury_status`, `status`
- [ ] `adp_espn`
- [ ] `proj_espn_season` (PPR points)
- [ ] `ecr_fp_ppr`, `ecr_sd`, `ecr_best`, `ecr_worst`
- [ ] `as_of` / scrape timestamps on every snapshot row

---

## V0.5 / V1 — unlock next

| Status | Source | Layer | Why | Access | Blocker |
|--------|--------|-------|-----|--------|---------|
| [ ] | **Fantasy Football Calculator ADP API** | Market | 10-team PPR ADP + **historical years** for backtests | Free + attribution | Cloudflare 403 from some environments — verify from home/browser |
| [ ] | **FantasyPros official API** | Market + expectation + news | Multi-platform ADP, projections, injuries, news | Free prototype key · HOF ~$9/mo personal prod | Request key at FantasyPros |
| [ ] | **nflverse / `nflreadpy`** | Identity + history | Players, weekly/season stats, schedules, later PBP | Free downloads | Needed before serious backtests / own projections |

### Extra fields once unlocked

- [ ] `adp_ffc` (+ historical `season`, `as_of` when available)
- [ ] `adp_consensus_fp`, `adp_espn_fp` (platform split from FP)
- [ ] `proj_fantasypros` (full stat line if API gives it)
- [ ] `injury_fp` / news flags (cross-check vs Sleeper)

---

## Later — only if harness shows lift

| Status | Source | Layer | Priority | Access |
|--------|--------|-------|----------|--------|
| [ ] | Underdog ADP | Market signal | Tier B | No public API — CSV from app |
| [ ] | Rotowire (or similar) | Injuries / news | Tier B | Paid / ToS |
| [ ] | Fantasy Points / usage suite | Opportunity | Tier A if accessible | Often paid |
| [ ] | Vegas / props aggregator | `vegas_projection` | Tier C → A later | Paid aggregator |
| [ ] | RotoViz / 4for4 / Footballguys | Secondary experts | Tier B | Paid |
| [ ] | CBS / Yahoo as first-class | Market | Low | Prefer via FantasyPros ADP |
| [ ] | NFL.com scrape | Authority roster/injury | Low | Prefer nflverse / Sleeper |
| [ ] | PFR direct scrape | History | Low | Prefer nflverse |
| [ ] | Reddit / community sentiment | Research only | Skip for model | Manual |

---

## Explicitly out of scope for now

- [x] Dynasty valuation / KeepTradeCut as core inputs (`MODE = redraft`)
- [x] Opponent-specific tendency models (V6 only if evidence)
- [x] Live ESPN draft-room automation (V5)
- [x] Blind averaging of every projection site

---

## Snapshot / engineering checklist

Treat every external pull as a **versioned snapshot**, not a mutable “current truth.”

- [ ] Store raw payloads (or hashes) with `source`, `pulled_at`
- [ ] Normalized tables: `players`, `id_map`, `adp_snapshots`, `rankings_snapshots`, `projections_snapshots`, `injuries_snapshots`
- [ ] One adapter per source → shared schema
- [ ] Never let optimizer code import Sleeper/ESPN/FP clients directly
- [ ] DST + K stubs so draft sim / UI don’t break (crude ADP/ECR OK in V0)
- [ ] `player_aliases` for autocomplete (Jr., D/ST names, punctuation)

---

## Access actions (human)

| Action | Owner | Done |
|--------|-------|------|
| Confirm FFC ADP API works in browser / local Python | | [ ] |
| Request FantasyPros API key (free prototype) | | [ ] |
| Optional: FantasyPros HOF if we need production personal use | | [ ] |
| Decide: commit raw snapshots to git vs local/`data/` gitignored | | [ ] |

---

## Stage mapping

| Stage | Sources required |
|-------|------------------|
| **V0** data + draft-state + keyboard UI | Sleeper + DynastyProcess IDs/ECR + ESPN ADP/proj |
| **V1** marginal lineup value | Same (+ bye / injury in lineup EV) |
| **V1.5** backtesting | + FFC historical ADP and/or our own ADP snapshots; nflverse stats for outcomes |
| **V2–V3** draft-aware / survival | Same + richer market (FP multi-ADP if available) |
| **V4** Monte Carlo | + projection uncertainty (ECR `sd` first; distributions later) |
| **V5** live ESPN | ESPN draft observation (separate from valuation sources) |

---

## Quick “good enough for V0?” gate

Ship V0 data layer when all are true:

- [ ] Every relevant player has a stable `player_id` and searchable name
- [ ] ESPN ADP + ESPN projection present for skill players (and stubs for DST/K)
- [ ] FP PPR ECR + `sd` present for ranked pool
- [ ] Injury status joinable from Sleeper
- [ ] One command / script refreshes snapshots and writes `as_of`
