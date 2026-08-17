# P2.2B — FantasyPros projections API probe

- probed_at: `2026-08-17T04:03:11Z`
- season: **2024**
- http_status: **200**
- gate: **fail**
- verdict: **fail_stage_B**
- reason: `projection_as_of_unverified`

## Auth canary (`/nfl/players`)

- http_status: **200**
- key_appears_valid: **True**

## Notes

- Payload has players but no clear publish/as_of timestamp. season=2024 + week=0 is not sufficient provenance.

## Date-like fields (sample)

_None found._

## Hard rule

No verifiable as_of → **reject for Stage B**. Do not convert ECR→points.
Re-run: `python -m draftopt.phase2.fp_projection_probe --season 2024`
