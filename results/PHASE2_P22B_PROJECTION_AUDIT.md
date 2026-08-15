# P2.2B — Historical projection source audit

**Status:** audit complete (desk research + prior spike evidence). **No ingest. No replay. `evaluable` stays 0.**

**Parent:** [`PHASE2_P22_SOURCES.md`](PHASE2_P22_SOURCES.md) · Stage A spike [`phase2_p22_feasibility_2024.md`](phase2_p22_feasibility_2024.md)

**Rule:** no trustworthy publish / `as_of` date → not usable for scientific `marginal` evaluation.

---

## Progress lock

```text
P2.1   ██████████ DONE   (2026 pipeline proof)
P2.2A  ██████████ DONE   (FFC + nflverse + mapping feasibility)
P2.2B  ██████████ CLOSED  (FP free API — no Stage B projections)
P2.2C  ░░░░░░░░░░ ADP-STRUCTURAL (see PHASE2_P22C_ADP_STRUCTURAL.md)
P2.3   ░░░░░░░░░░ ENFORCE ON HISTORICAL CUT when evaluable path lands
P2.4+  ░░░░░░░░░░ blocked until evaluable=1 for the labeled experiment
```

---

## What Gate 4 needs

For `marginal` vs ADP on **actual** 2024 PPR:

| Field | Requirement |
| --- | --- |
| `proj_ppr` | Season-long PPR points (or full stat line → our scorer) |
| `proj_as_of` | ISO date ≤ snapshot decision date |
| Join | Map to canonical `player_id` (no name-only) |
| League fit | Prefer same expectation stack as production (ESPN-shaped) |

**Forbidden:** current/2026 ESPN projections on 2024 players.

---

## Candidate scorecard

| # | Source | Exact date? | Format → `proj_ppr`? | Coverage (expected) | Join path | Verdict |
| --- | ---: | --- | --- | --- | --- | --- |
| 1 | **ESPN live API** (our ingest) | Only `pulled_at` of *today* | Yes (`appliedTotal`) | High | `espn_id` | **REJECT for 2024** — no historical season endpoint in our adapter |
| 2 | **Mike Clay / ESPN Draft Kit PDF 2024** | Yes — e.g. guide stamped **Updated: 9/4/2024** | Stat lines in PDF (manual/parse) | Positional tables | name/pos/team → DP (weak) or manual | **CONDITIONAL** — dated, but 9/4 may be **after** draft-week ADP (`FFC end_date 2024-09-01`); need a **late-Aug** PDF revision if one exists |
| 3 | **ESPN projections SPA** historical | No public year archive | SPA / unofficial scrapers | — | — | **REJECT** as pipeline source — live page replaces past seasons |
| 4 | **FantasyPros projections API** | TBD (needs key) | Yes (stat line / season) | High if licensed | `fantasypros_id` via DP | **PROBE IN PROGRESS** — CLI `fp_projection_probe`; no key in env yet → blocked |
| 5 | **DynastyProcess / FP ECR archive** | Yes — `scrape_date` | **Rankings, not points** | High | `fantasypros_id` | **REJECT for Stage B default** — ECR≠`proj_ppr` (Stage C proxy only, labeled) |
| 6 | **Our own `data/raw` ESPN dumps** | Only if we saved 2024 files | Yes | — | existing | **N/A** — no 2024 preseason raw archive in-repo (gitignored raw is current-era) |
| 7 | **Wayback / third-party mirrors** | Sometimes | HTML/PDF scrape | Uneven | fragile | **LAST RESORT** — only if snapshot URL has clear crawl date ≤ decision date |

---

## Detail notes

### 1–3 ESPN family (ideal stack, weak history)

- Production `draftopt.sources.espn` hits **current** `leaguedefaults` season URL — not a time machine.
- Clay PDF guides are the strongest **dated** ESPN-adjacent artifact found in audit: explicit update stamp + full projection tables.
- Risk: update stamp after Week 1 / after typical draft weekend ⇒ **leakage vs a late-August draft snapshot**. Align `proj_as_of` and ADP `as_of` deliberately or fail closed.
- Action if pursuing: locate **August 2024** Clay/ESPN kit revision (or Wayback of projections page from ~2024-08-25–31), parse once into eval DB, stamp `proj_source=espn_clay_pdf`, never silently mix with live API.

### 4 FantasyPros projections

- Official API documents season/weekly projections; historical/bulk called out on commercial tier.
- Fits identity graph (`fantasypros_id`) better than PDF name matching.
- Action: request/use prototype or HOF key; query whether **2024 preseason** projections return with a publish timestamp. If only “season=2024” with no date → **FAIL** same as undated ADP.

### 5 ECR archive (not Gate 4)

- `load_ff_rankings(type="all")` / DynastyProcess `db_fpecr` has `scrape_date` — excellent for **dated ranks**, not for reproducing ESPN `proj_ppr`.
- Keep listed under Stage **C** only.

### Escape hatch (not Stage B)

**ADP-only historical evaluation** (12-team FFC labeled, or a true 10-team ADP if found):

- Tests simulator / roster construction under historical ADP.
- Does **not** evaluate `marginal`.
- Separate experiment id / docs; never set `evaluable=1` for `marginal` claims.

---

## Alignment with Stage A artifacts

| Snapshot | Keep? | Evaluable? |
| --- | --- | --- |
| `2024-preseason-2024-09-01-ffc-pending` (10-team **request**) | Yes | **No** — `adp_league_size_mismatch` |
| 12-team FFC variant | Yes, as **12-team Stage A** only | **No** — still missing projections |
| `2026-preseason-2026-08-12` | Yes | **No** — pipeline proof |

Do **not** use 12-team ADP to claim 10-team optimizer performance.

---

## Recommended next actions (ordered)

1. **FantasyPros API probe:** `python -m draftopt.phase2.fp_projection_probe --season 2024` with `FANTASYPROS_API_KEY` set — see [`phase2_p22b_fp_probe.md`](phase2_p22b_fp_probe.md)
2. **Clay/ESPN PDF hunt (short):** find a revision dated **≤ 2024-08-31**; if only 9/4+ exists, FAIL for draft-weekend cut
3. If FP fails provenance → **stop projection archaeology**; open labeled **ADP-only** track
4. Still blocked: draft replay, `marginal` vs ADP, VOR/V2

---

## Explicit non-goals (this audit)

- Implementing projection ingest
- Setting `evaluable=1`
- Optimizer / V2 changes
- Multi-hour site crawls

---

## Checklist template (reuse per source)

```text
source:
access:
as_of / publish date:
fields → proj_ppr without ECR→points? (Y/N)
player coverage vs draftable pool:
join path:
verdict: usable_stage_B | adp_only | reject
notes:
```
