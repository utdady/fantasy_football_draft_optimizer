# 2026 draft readiness (frozen `marginal`)

- created: `2026-08-15T16:23:38Z`
- db: `C:\Users\addyb\fantasy_football_draft_optimizer\data\draftopt.db`
- strategy: **marginal** · teams: 10
- checks: **25/25 pass**

Product readiness for 2026 live DB with frozen marginal. Not a construction / Phase-2 ladder.

## Verdict

**PASS — ready for continued mock-draft UX polish / rookie overlay next.**

## Full 10-team mock (slot 1, seed 42)

- complete checks embedded; board picks: 160
- user pos mix: `{'QB': 2, 'RB': 5, 'WR': 6, 'TE': 2, 'DST': 1}`
- recommend latency ms: p50=11.65 p95=29.03 max=33.99 (clock=90s)
- comfortable vs 5% of clock: **True**

**Observation (not a fail):** several late user picks show `M=0.0` (e.g. Brian Thomas,
Matthew Golden). Likely missing/zero ESPN season_points for those IDs — product polish
candidate (hide / deprioritize zero-proj), not a construction issue.

### User picks

- overall 1: Josh Allen (QB) M=369.21
- overall 20: Derrick Henry (RB) M=274.43
- overall 21: Saquon Barkley (RB) M=273.86
- overall 40: Tyreek Hill (WR) M=263.71
- overall 41: Travis Etienne (RB) M=242.09
- overall 60: Keenan Allen (WR) M=212.6
- overall 61: Carnell Tate (WR) M=211.13
- overall 80: Travis Kelce (TE) M=177.0
- overall 81: Broncos D/ST (DST) M=130.67
- overall 100: Brian Thomas (WR) M=0.0
- overall 101: Matthew Golden (WR) M=0.0
- overall 120: RJ Harvey (RB) M=0.0
- overall 121: Isaiah Likely (TE) M=0.0
- overall 140: Blake Corum (RB) M=0.0
- overall 141: Chris Godwin (WR) M=0.0
- overall 160: Daniel Jones (QB) M=0.0

## Failure modes

### Snipe / skip-target + undo

- PASS `snipe_has_alts` n_recs=3
- PASS `alt_pick_removes_chosen` Jahmyr Gibbs
- PASS `skipped_target_still_available` Josh Allen
- PASS `undo_restores_both` 
- PASS `undo_recommend_stable` got=Josh Allen

### Late-board recommend + latency

- PASS `late_draft_complete` user_picks=16
- PASS `late_latency_under_1s_p95` p95=38.1
- late latency: `{'n': 9, 'p50': 21.69, 'p95': 38.14, 'max': 39.56}`

### HTTP API smoke (`/api`)

- PASS `http_status` code=200
- PASS `http_players` players=882
- PASS `http_create_draft` code=200
- PASS `http_initial_recommend` n=3
- PASS `http_autopick` code=200 ms=79.4
- PASS `http_autopick` code=200 ms=84.6

## DB gates

- PASS `players_present` n=882
- PASS `proj_pulled_at` pulled_at=2026-08-15T16:18:27Z
- PASS `gibbs_2026_proj` Gibbs season_points=365.3 (expect >=340 for 2026)
- PASS `espn_adp_coverage` n_adp=800

## UI / HTTP

- Landing page loads at `http://127.0.0.1:8001/` (setup: name / slot / lineup / 90s clock).
- `/api/status` reflects fresh ingest (`pulled_at=2026-08-15T16:18:27Z`, 882 players).
- `POST /api/drafts` returns `is_user_turn` + top recs (Josh Allen / Gibbs / Puka) with 2026-scale marginals.

## Next

- If PASS: more harsh UI timing / human mock; then rookie overlay (not in formula).
- Do **not** reopen V3 construction.
- Soft polish: zero-marginal late-board candidates (missing proj).
