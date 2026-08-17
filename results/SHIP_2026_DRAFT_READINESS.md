# 2026 draft readiness (frozen `marginal`)

- created: `2026-08-17T05:38:49Z`
- db: `C:\Users\addyb\fantasy_football_draft_optimizer\data\draftopt.db`
- strategy: **marginal** · teams: 12
- checks: **25/25 pass**

Product readiness for 2026 live DB with frozen marginal. Not a construction / Phase-2 ladder.

## Verdict

**PASS — ready for continued mock-draft UX polish / rookie overlay next.**

## Full mock (slot 1, seed 42)

- complete checks embedded; board picks: 192
- user pos mix: `{'QB': 3, 'RB': 4, 'WR': 6, 'TE': 1, 'DST': 2}`
- recommend latency ms: p50=13.15 p95=14.91 max=15.72 (clock=60s)
- comfortable vs 5% of clock: **True**

### User picks

- overall 1: Josh Allen (QB) M=369.21
- overall 24: Derrick Henry (RB) M=274.4
- overall 25: Kenneth Walker (RB) M=272.65
- overall 48: Tyreek Hill (WR) M=263.71
- overall 49: Davante Adams (WR) M=232.32
- overall 72: Keenan Allen (WR) M=212.6
- overall 73: Austin Ekeler (RB) M=207.83
- overall 96: Mark Andrews (TE) M=169.18
- overall 97: Broncos D/ST (DST) M=130.67
- overall 120: Jonathon Brooks (RB) M=0.0
- overall 121: Makai Lemon (WR) M=0.0
- overall 144: Jayden Reed (WR) M=0.0
- overall 145: Kyler Murray (QB) M=0.0
- overall 168: Chiefs D/ST (DST) M=0.0
- overall 169: Denzel Boston (WR) M=0.0
- overall 192: Cam Ward (QB) M=0.0

## Failure modes

### Snipe / skip-target + undo

- PASS `snipe_has_alts` n_recs=3
- PASS `alt_pick_removes_chosen` Jahmyr Gibbs
- PASS `skipped_target_still_available` Josh Allen
- PASS `undo_restores_both` 
- PASS `undo_recommend_stable` got=Josh Allen

### Late-board recommend + latency

- PASS `late_draft_complete` user_picks=16
- PASS `late_latency_under_1s_p95` p95=15.2
- late latency: `{'n': 9, 'p50': 14.43, 'p95': 15.2, 'max': 15.28}`

### HTTP API smoke (`/api`)

- PASS `http_status` code=200
- PASS `http_players` players=857
- PASS `http_create_draft` code=200
- PASS `http_initial_recommend` n=3
- PASS `http_autopick` code=200 ms=38.3
- PASS `http_autopick` code=200 ms=41.3

## DB gates

- PASS `players_present` n=857
- PASS `proj_pulled_at` pulled_at=2026-08-17T05:37:43Z
- PASS `gibbs_2026_proj` Gibbs season_points=365.3 (expect >=340 for 2026)
- PASS `espn_adp_coverage` n_adp=800

## Next

- If PASS: more harsh UI timing / human mock; then rookie overlay (not in formula).
- Do **not** reopen V3 construction.
