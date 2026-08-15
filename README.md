# Fantasy Draft Optimizer

10-team PPR snake redraft practice room + V1 marginal lineup-value recommendations.

> **V2-alpha is not yet validated as a real-world drafting advantage.** It currently
> demonstrates an advantage over V1 baselines under an ADP-greedy simulated
> lookahead (see [`results/V2_ALPHA_BASELINE.md`](results/V2_ALPHA_BASELINE.md)).
> The UI still uses raw **V1 `marginal`**. Objective / scenario semantics for
> further V2 work are frozen in [`results/V2_OBJECTIVE_DESIGN.md`](results/V2_OBJECTIVE_DESIGN.md)
> — no new V2 strategy until that note is revised.
>
> **Phase 2 (next research track):** historical snapshot + actual-points evaluation
> ([`results/PHASE2_HISTORICAL_EVAL.md`](results/PHASE2_HISTORICAL_EVAL.md)). Algorithms
> stay frozen; first promotion-worthy evidence must be leakage-safe **actual** PPR.
>
> **P2.1 done:** frozen snapshot `2026-preseason-2026-08-12` in `data/draftopt_eval.db`
> (**pipeline proof**, `evaluable=0` — not for actual-points claims). See
> [`results/PHASE2_P21_SNAPSHOT.md`](results/PHASE2_P21_SNAPSHOT.md). Next: **P2.2**
> historical eval snapshot + outcomes ([`results/PHASE2_P22_SOURCES.md`](results/PHASE2_P22_SOURCES.md)).
> Stage A spike: FFC 2024 10-team request **failed** league-size check (`evaluable=0`).
> **P2.2B:** projection source audit — [`results/PHASE2_P22B_PROJECTION_AUDIT.md`](results/PHASE2_P22B_PROJECTION_AUDIT.md)
> (Gate 4 still open; no replay).

## Setup

```powershell
cd fantasy_football_draft_optimizer
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## Ingest players

```powershell
python -m draftopt.ingest
```

Writes snapshots under `data/raw/` and SQLite at `data/draftopt.db`.

## Run the draft UI

```powershell
python -m draftopt.serve
```

Open **http://127.0.0.1:8001**

1. Enter name, slot, and lineup preset (default: no K, 7 bench).
2. CPU teams pick with ADP + noise.
3. On your turn (90s clock), TAKE uses **V1 marginal starter value** (FLEX-aware) from ESPN projections.
4. Timeout autodrafts the V1 recommendation. `]` toggles TAKE. Ctrl+Z undoes your pick.

Baseline ADP strategy remains available for experiments (`strategy=adp` on API / backtest).

## Backtest (ablation + slot matrix)

```powershell
# Single slot: ADP vs greedy-projection vs marginal
python -m draftopt.backtest --n 50 --slot 1 --preset league_default --seed 0

# Slot matrix
python -m draftopt.backtest --n 50 --slots 1-10 --seed 0 `
  --out results/ablation_espn_2026_slots_1-10.md

# Value-function ablation (raw marginal vs no-QB R1 vs VOR-lite)
python -m draftopt.backtest --n 50 --slot 1 --seed 0 `
  --strategies adp,marginal,marginal_no_qb_r1,marginal_vor `
  --out results/ablation_vor_slot1_n50.md

# VOR decision traces (baselines + top candidates for R1-R3)
python -m draftopt.diagnose_vor --n 10 --slot 1 --rounds 3 --seed 0 `
  --out results/diagnose_vor_slot1.md

# Frozen ESPN projection curves around replacement ranks (no draft)
python -m draftopt.audit_proj_curves --out results/audit_proj_curves_frozen.md
```

Paired snakes: shared sim seed + CPU RNG keyed by overall pick #. Scoring uses ESPN projections only.

- `marginal` — raw starter-point lift (FLEX-aware; scarcity-blind)
- `marginal_no_qb_r1` — raw marginal with QB banned in round 1 (diagnostic)
- `marginal_vor` — VOR-lite (`lineup_ev` uses projection minus positional replacement)
- `marginal_v2` — experimental V2-alpha (two-pick EV under ADP-greedy future); frozen baseline in [`results/V2_ALPHA_BASELINE.md`](results/V2_ALPHA_BASELINE.md)
- `marginal_v2_beta` — **rejected** equal-weight policy mixture; see [`results/V2_BETA.md`](results/V2_BETA.md)
- `robust_min` — experimental β2-robust diagnostic (`min_f`); **rejected as final**; see [`results/V2_BETA.md`](results/V2_BETA.md)
- Further V2 work: read [`results/V2_OBJECTIVE_DESIGN.md`](results/V2_OBJECTIVE_DESIGN.md) first (primary EV vs diagnostics; planner vs stress scenarios)

```powershell
# Three-way early-pick divergence (RAW / VOR / V2)
python -m draftopt.trace_v2_divergence --n 3 --slots 1,5,10 --picks 5 --seed 0 `
  --out results/divergence_raw_vor_v2_slots_1_5_10.md
```

Checked-in reports: [`results/`](results/). `win_rate` = paired starter-points wins (not WR share).

## Tests

```powershell
pytest
```
