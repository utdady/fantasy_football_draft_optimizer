# Fantasy Draft Optimizer

10-team PPR snake redraft practice room + V1 marginal lineup-value recommendations.

> **Core thesis: 🟡 preliminary support (C−B > 0 after feasibility + DST controls).
> V3-A calibration: 🟡 supported / frozen (D−C tradeoff). V3-B construction: 🔴 closed.
> External validity 🔴. V3 beyond frozen D: 🔴 not justified. UI: `marginal`.**
>
> **V3-B:** licensed construction hypotheses (B.0 / B.1 / A / B) were policy-inert or
> harmful vs D. No construction retune authorized. Checkpoint `6ad702b`.
> Closeout: [`results/PHASE2_V3B_CLOSEOUT.md`](results/PHASE2_V3B_CLOSEOUT.md).
>
> Evidence: ADP → ADP-feasible → structural ladder under 2024 FFC actual PPR
> ([`results/phase2_p22c_adp_feasible_ladder.md`](results/phase2_p22c_adp_feasible_ladder.md);
> track [`results/PHASE2_P22C_ADP_STRUCTURAL.md`](results/PHASE2_P22C_ADP_STRUCTURAL.md);
> closeout [`results/phase2_p22c_closeout.md`](results/phase2_p22c_closeout.md)).
> V3-A: [`results/V3A_CALIBRATION_DESIGN.md`](results/V3A_CALIBRATION_DESIGN.md) ·
> ladder [`phase2_v3a_ladder.md`](results/phase2_v3a_ladder.md).
> Gates: [`gate1`](results/phase2_v3a_gate1_adp_provenance.md) ·
> [`gate2`](results/phase2_v3a_gate2_train_outcomes.md) ·
> [`gate3`](results/phase2_v3a_gate3_calibration_freeze.md) ·
> [`gate4`](results/phase2_v3a_gate4_leakage_audit.md).
> `evaluable=0`. No UI / V2 / CVaR / construction retune.
>
> Phase 1 synthetic decision research is frozen. UI still uses raw **V1 `marginal`**.
> V2 notes: [`results/V2_ALPHA_BASELINE.md`](results/V2_ALPHA_BASELINE.md),
> [`results/V2_OBJECTIVE_DESIGN.md`](results/V2_OBJECTIVE_DESIGN.md).
>
## Setup

```powershell
cd fantasy_football_draft_optimizer
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
# Optional: copy .env.example → .env and set FANTASYPROS_API_KEY for FP probe
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
