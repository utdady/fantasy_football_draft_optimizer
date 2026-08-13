# Fantasy Draft Optimizer

10-team PPR snake redraft practice room + V1 marginal lineup-value recommendations.

## Setup

```powershell
cd C:\Users\addyb\fantasy_football_draft_optimizer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## Backtest (ADP vs marginal)

```powershell
python -m draftopt.backtest --n 50 --slot 1 --preset league_default --seed 0
```

Paired snakes: each sim seed is shared across strategies; CPU RNG is keyed by overall pick # so opponents only diverge when the remaining board differs. Scores starter EV on ESPN projections (not ECR proxies). Reports starter pts, starter rank, roster-sum rank, and win rate.

## Tests

```powershell
pytest
```
