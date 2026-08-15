# P2.2B — FantasyPros projections API probe

**Status: CLOSED / BLOCKED for Stage B**

- probed_at: `2026-08-15T06:46:50Z` (and earlier `06:41:25Z`)
- season: **2024**
- http_status: **403**
- gate: **fail**
- verdict: **blocked_auth**
- reason: `api_forbidden`

## Auth canary

Probe code now hits `/public/v2/json/nfl/players` before projections so a later
re-run can distinguish invalid key vs projections-only deny. Both attempts that
reached projections (legacy then public+legacy) returned **403** on
`.../nfl/2024/projections`.

Error body observed (no key material): `{"message":"Forbidden"}`.

## Scientific close

> **No historical projection source meeting the project's provenance and leakage
> requirements was confirmed for the 2024 evaluation window via the FantasyPros
> free API.**

Do **not** purchase HOF solely to rescue this experiment unless dated historical
preseason projections are explicitly documented. Stop FP archaeology.

## Next

**P2.2C — labeled ADP-structural track** (12-team FFC). See
[`PHASE2_P22C_ADP_STRUCTURAL.md`](PHASE2_P22C_ADP_STRUCTURAL.md).

## Hard rule

No verifiable as_of → **reject for Stage B**. Do not convert ECR→points.
