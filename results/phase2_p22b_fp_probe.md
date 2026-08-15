# P2.2B — FantasyPros projections API probe

- probed_at: `2026-08-15T06:26:37Z`
- season: **2024**
- http_status: **None**
- gate: **fail**
- verdict: **blocked_no_key**
- reason: `api_key_missing`

## Notes

- Set FANTASYPROS_API_KEY (or FP_API_KEY) and re-run. Without a key the API returns 403; historical as_of cannot be verified.
- Docs: GET /v2/json/nfl/{season}/projections?week=0&scoring=PPR (week=0 = preseason). No as_of query parameter is documented — provenance must come from response fields or fail closed.

## Date-like fields (sample)

_None found._

## Hard rule

No verifiable as_of → **reject for Stage B**. Do not convert ECR→points.
Re-run: `python -m draftopt.phase2.fp_projection_probe --season 2024`
