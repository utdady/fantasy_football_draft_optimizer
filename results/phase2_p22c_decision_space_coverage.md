# P2.2C decision-space coverage

- snapshot: `2024-preseason-2024-09-01-ffc12`
- evaluable: **0** (locked)
- decision_space_gate: **fail**
- reasons: unmapped_players_remain, unmapped_in_top_adp_bands, strategy_selected_unmapped_or_no_gsis

Board coverage ≠ outcome coverage. Unmapped ffc:* players remain draftable but are silent losses for actual-PPR scoring. No nflverse attach in this report. Not production marginal.

## Overall mapping

| Metric | Value |
| --- | ---: |
| Players | 205 |
| Mapped | 179 (87.3%) |
| Unmapped | 26 |
| Mapped with gsis | 179 (87.3%) |

## Top-N ADP coverage (lowest ADP)

| Band | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| Top 50 | 50 | 44 | 6 | 88.0% |
| Top 100 | 100 | 90 | 10 | 90.0% |
| Top 150 | 150 | 135 | 15 | 90.0% |

## Unmapped by ADP band

| Band | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| 1-50 | 50 | 44 | 6 | 88.0% |
| 51-100 | 50 | 46 | 4 | 92.0% |
| 101-150 | 50 | 45 | 5 | 90.0% |
| 151+ | 55 | 44 | 11 | 80.0% |

## Unmapped by position

| Pos | n | mapped | unmapped | coverage |
| --- | ---: | ---: | ---: | ---: |
| DST | 12 | 0 | 12 | 0.0% |
| K | 15 | 14 | 1 | 93.3% |
| QB | 26 | 25 | 1 | 96.2% |
| RB | 60 | 55 | 5 | 91.7% |
| TE | 20 | 19 | 1 | 95.0% |
| WR | 72 | 66 | 6 | 91.7% |

## All unmapped (ADP-ranked)

| ADP rank | ADP | Pos | Name | Team | reason |
| ---: | ---: | --- | --- | --- | --- |
| 18 | 17.6 | RB | Travis Etienne Jr. | JAX | no_crosswalk_match |
| 24 | 23.0 | WR | Deebo Samuel Sr. | SF | no_crosswalk_match |
| 32 | 30.3 | RB | James Cook III | BUF | no_crosswalk_match |
| 38 | 35.6 | RB | Kenneth Walker | SEA | no_crosswalk_match |
| 47 | 45.2 | WR | Michael Pittman Jr. | IND | no_crosswalk_match |
| 48 | 46.0 | RB | Aaron Jones Sr. | MIN | no_crosswalk_match |
| 56 | 55.2 | QB | Anthony Richardson Sr. | IND | no_crosswalk_match |
| 73 | 68.4 | WR | Chris Godwin Jr. | TB | no_crosswalk_match |
| 76 | 72.8 | TE | Kyle Pitts Sr. | ATL | no_crosswalk_match |
| 86 | 82.2 | WR | Hollywood Brown | KC | no_crosswalk_match |
| 119 | 116.1 | WR | Mike Williams | PIT | no_crosswalk_match |
| 138 | 131.2 | DST | Baltimore Defense | BAL | no_crosswalk_match |
| 141 | 133.4 | DST | San Francisco Defense | SF | no_crosswalk_match |
| 148 | 139.3 | DST | Dallas Defense | DAL | no_crosswalk_match |
| 150 | 140.8 | DST | NY Jets Defense | NYJ | no_crosswalk_match |
| 156 | 147.4 | DST | Chicago Defense | CHI | no_crosswalk_match |
| 158 | 148.6 | DST | Detroit Defense | DET | no_crosswalk_match |
| 171 | 155.1 | DST | Cleveland Defense | CLE | no_crosswalk_match |
| 177 | 157.8 | DST | Pittsburgh Defense | PIT | no_crosswalk_match |
| 179 | 158.8 | DST | Buffalo Defense | BUF | no_crosswalk_match |
| 189 | 160.9 | DST | Cincinnati Defense | CIN | no_crosswalk_match |
| 193 | 163.3 | DST | Kansas City Defense | KC | no_crosswalk_match |
| 195 | 164.1 | K | Michael Badgley | DET | no_crosswalk_match |
| 198 | 169.6 | WR | Gabe Davis | JAX | no_crosswalk_match |
| 201 | 174.0 | RB | Tyrone Tracy Jr. | NYG | no_crosswalk_match |
| 202 | 174.7 | DST | New Orleans Defense | NO | no_crosswalk_match |

## Strategy selections of unmapped / no-gsis

- slots: [1, 5, 10] · n_sims: 3 · seed0: 42
- user picks scanned: 270
- gate_strategy_unmapped_zero: **False**

### `adp_baseline` — 18 pick-events, 11 unique players

| ADP rank | Name | Pos | events (see JSON) |
| ---: | --- | --- | --- |
| 18 | Travis Etienne Jr. | RB | 1 |
| 24 | Deebo Samuel Sr. | WR | 1 |
| 32 | James Cook III | RB | 1 |
| 47 | Michael Pittman Jr. | WR | 2 |
| 56 | Anthony Richardson Sr. | QB | 6 |
| 73 | Chris Godwin Jr. | WR | 1 |
| 119 | Mike Williams | WR | 1 |
| 138 | Baltimore Defense | DST | 1 |
| 148 | Dallas Defense | DST | 1 |
| 156 | Chicago Defense | DST | 1 |
| 158 | Detroit Defense | DST | 2 |

### `adp_structural` — 23 pick-events, 11 unique players

| ADP rank | Name | Pos | events (see JSON) |
| ---: | --- | --- | --- |
| 18 | Travis Etienne Jr. | RB | 1 |
| 24 | Deebo Samuel Sr. | WR | 1 |
| 32 | James Cook III | RB | 1 |
| 47 | Michael Pittman Jr. | WR | 2 |
| 56 | Anthony Richardson Sr. | QB | 4 |
| 73 | Chris Godwin Jr. | WR | 1 |
| 76 | Kyle Pitts Sr. | TE | 1 |
| 138 | Baltimore Defense | DST | 9 |
| 148 | Dallas Defense | DST | 1 |
| 156 | Chicago Defense | DST | 1 |
| 158 | Detroit Defense | DST | 1 |

## Board-wide unmapped picks (secondary)

- board pick-events with unmapped/no-gsis: 398
- unique players: 25

**Next:** Fix high-value unmapped (Jr/Sr/III/nicknames/DST), rematerialize, re-run this report until gate=pass; then attach nflverse PPR.
