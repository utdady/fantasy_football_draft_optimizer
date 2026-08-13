# Fantasy Draft Optimizer

10-team PPR snake redraft practice room + V1 marginal lineup-value recommendations.

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

Checked-in reports: [`results/`](results/). `win_rate` = paired starter-points wins (not WR share).

## Tests

```powershell
pytest
```
