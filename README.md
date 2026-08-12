# V0 Draft Optimizer

10-team PPR snake redraft simulator. Keyboard-first local web UI. Data from Sleeper, DynastyProcess (FantasyPros ECR + IDs), and ESPN.

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

Writes snapshots under `data/raw/` and a SQLite DB at `data/draftopt.db`.

## Run the draft UI

```powershell
python -m draftopt.serve
```

Open **http://127.0.0.1:8001** (8000 is used by another app on this machine).

1. Enter your name, draft slot, and lineup preset (default: **no K, 7 bench**).
2. CPU teams pick automatically (ADP + a little randomness).
3. On your turn you have **90 seconds**. Filter/search the player table and press **Enter**, or click a row. If the clock hits zero, the app autodrafts the recommended player.
4. **]** collapses/expands the TAKE rail. **Ctrl+Z** undoes your last pick (and CPU picks after it).
5. At the end, a scorecard ranks all teams by projected points + ADP value.

V0 recommendation is remaining players sorted by ESPN ADP (ECR fallback).

## Tests

```powershell
pytest
```
