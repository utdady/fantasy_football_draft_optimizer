# Snapshot validation: `2026-preseason-2026-08-12`

- season: **2026**
- snapshot_date: **2026-08-12**
- players: **800**
- pipeline_proof: **1**
- evaluable: **0**
- outcome_season: **None**
- overall: **PASS**

| check | ok | detail |
| --- | --- | --- |
| snapshot_date_valid | ✓ | snapshot_date=2026-08-12 season=2026 |
| flags_mutually_consistent | ✓ | pipeline_proof=1 evaluable=0 outcome_season=None |
| evaluable_has_outcome_season | ✓ | evaluable=0 outcome_season=None |
| player_count | ✓ | n=800 (min 200) |
| player_ids_unique | ✓ | n=800 unique=800 |
| positions_valid | ✓ | invalid=0 |
| required_positions_present | ✓ | counts={'RB': 187, 'WR': 274, 'TE': 140, 'QB': 110, 'K': 57, 'DST': 32} missing=[] |
| adp_coverage | ✓ | 100.0% (800/800; min 70%) |
| projection_coverage | ✓ | 96.8% (774/800; min 70%) |
| adp_and_proj_coverage | ✓ | 96.8% (774/800; min 60%) |
| no_post_snapshot_records | ✓ | leakage_findings=0 |
| provenance_as_of_present | ✓ | missing_as_of_rows=0 |
| snapshot_reproducible_meta | ✓ | label='2026-preseason-2026-08-12' created_at=2026-08-14T19:34:52Z |
