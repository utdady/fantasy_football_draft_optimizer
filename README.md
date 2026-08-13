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

# Slot matrix (lean first pass; ~40+ min on real DB)
python -m draftopt.backtest --n 50 --slots 1,5,10 --seed 0

# Fuller run when you have time
python -m draftopt.backtest --n 200 --slots 1-10 --seed 0
```

Paired snakes: shared sim seed + CPU RNG keyed by overall pick # (same opponent *policy*; boards may still diverge after different user picks). Decisions and scoring use ESPN projections only — ECR is not converted into fake points. Ablation: if marginal beats greedy, lineup construction is adding value beyond “take highest proj.”

## Tests

```powershell
pytest
```
