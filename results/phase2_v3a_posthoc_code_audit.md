# Post-hoc code audit: V3-A calibration + D−C mechanism

**Status:** focused audit (not a full 67-file review).  
**Asked for:** (1) calibration fit leakage / math integrity; (2) mechanism hinge that
calibration ≠ construction translation.  
**Checkpoint context:** Branch A already inert (`00e2a75`); UI still `marginal`.

**Verdict (both requested surfaces):** **hold up**, with documented caveats below.

---

## 1. Calibration leakage / fit math

### What was checked

| Check | Result |
| --- | --- |
| `TRAIN_YEARS` | `(2021, 2022, 2023)` only (`v3a_gate1_adp_provenance.py`) |
| `collect_train_pairs()` / `fit_calibration()` | Iterates `TRAIN_YEARS` only; no `run_year(2024)` |
| Full artifact `results/v3a_calibration_2021_2023.json` | 562 pairs; years {2021:209, 2022:155, 2023:198}; **no 2024** |
| Outcome states in train pairs | `observed_points` 556 + `observed_zero` 6 only — missing never enters fit |
| Gate 2 membership | Pairs only if `outcome_state ∈ {observed_points, observed_zero}` and ADP present |
| Temporal header | `calibration_as_of: 2023-09-01` &lt; `eval_snapshot_as_of: 2024-09-01` |
| Isotonic | All position maps non-increasing in ADP (QB/RB/WR/TE/DST) |
| `AdpV3aStrategy` | No eval-outcome / `actual_ppr` / `connect_eval` in recommend path |
| Materialize values | `season_points` = `CalibrationMap.value(2024 ADP, pos)` — not 2024 actuals |

### Fit pipeline (as implemented)

1. Gate 1: FFC ADP JSON per train year (`ffc_adp_ppr_12tm_{Y}.json`).
2. Gate 2: nflverse weeks for **that year only** → `actual_ppr` with missing ≠ 0.
3. Fit: ADP bins → merge `n < 5` → PAVA non-increasing → positional + global fallback.
4. Materialize: 2024 ADP through **frozen** map into `draftopt_p22c_v3a.db`.

This matches Gate 4’s intended inequality and recommend-path ban.

### Caveats (not blockers)

1. **`phase2_v3a_calibration_fit.json` omits `train_pairs`.** Curve points match the
   full artifact (`n_train_pairs=562`, identical position points), but pair-level
   provenance lives in `v3a_calibration_2021_2023.json`. Prefer that file when
   auditing rows.
2. **`phase2_v3a_gate4_leakage_audit.md` checklist is stale** (“fit not yet written”).
   Design constraints still correct; checklist not updated after implementation.
3. **Materialize opens the eval DB** to persist a snapshot / mapping. Value
   computation itself does not read 2024 outcomes. Contact surface, not an active
   leak — but future edits must not start joining `eval_outcomes*` into
   `proj_ppr`.
4. **Plumbing alias:** draft DB stores ADP/projections with `source='espn'` while
   content is FFC + V3-A map (documented in materialize notes). Reports must keep
   labeling FFC.

---

## 2. Mechanism hinge (D−C): calibration vs construction

### What was checked

Artifact [`phase2_v3a_mechanism_audit.md`](phase2_v3a_mechanism_audit.md) /
`mechanism_v3a_p22c.py` against the frozen ladder.

| Claim | Evidence | Assessment |
| --- | --- | --- |
| Player-level |error| improves under D | Mean \|e\| C picks 87.80 → D picks 54.30; paired on D roster mean (\|e_C\|−\|e_D\|)=+26.74 (672/900 better) | **Supported** (as labeled) |
| Draft outcome is a tradeoff | Full D−C mean +22.09, WR 55%, **p10 −268** | **Supported** |
| Construction / portfolio interaction | Mean starter Δ: QB +69, WR +69, **RB −162**; R1 forks D=QB vs C=RB/WR | **Supported** as description |
| Hinge gate text | Code requires abs-error improve *and* draft tail worse vs C−B p10 | Matches reported `HINGE` flag |

### Caveats (precision, not invalidation)

1. **Prediction-error sets are drafted picks (and paired D-roster players), not a
   full ADP-pool MAE.** The hinge is still honest as written (“All C/D picks”);
   do not over-read as “every remaining player’s map error.”
2. **2024 outcomes are used in the mechanism audit** (post-hoc). That is scoring /
   analysis, not map fit — allowed. Do not confuse with calibration leakage.
3. **Ex-DST+TE flips mean D−C negative (−24).** Full-contract tradeoff still holds;
   skill-mix attribution is sensitive to TE inclusion — already visible in the
   audit table.

### Relation to later construction experiments

The hinge correctly licensed **construction design** (not UI / map retune). Later
results do not reopen this audit:

- B.0 same-pos replacement: falsified  
- B.1 \(M_D - v(a^*)\): policy-inert  
- Branch A \(M_D - M_D(q^*)\): policy-inert (`00e2a75`)

Those are separate falsifications of myopic construction proxies, not evidence
against the calibration-layer hinge.

---

## 3. Not covered by this audit

- Full V3-B implementation line-by-line review (already laddered; A/B.1 inert).
- Gain/loss TE-over-QB sample reinterpretation (separate; prefer “not justified to
  special-case” over “symmetric/disproven”).
- Branch B design (licensed by A switch; **not** reviewed here — no B code yet).

---

## 4. Status after this audit

| Surface | Status |
| --- | --- |
| V3-A train leakage boundary | 🟢 holds in code + full artifact |
| V3-A fit math (bins / PAVA / years) | 🟢 consistent |
| Recommend / materialize value path | 🟢 no 2024 actuals in values |
| D−C hinge (better player error, worse left tail) | 🟢 holds as claimed |
| Gate 4 checklist doc freshness | 🟡 stale checkbox text |
| UI | `marginal` · `evaluable=0` |
| Next construction work | Branch B **design** only if deliberately opened |

---

## 5. One-sentence summary

> **Calibration fit is temporally clean (2021–2023 only) and the D−C hinge that
> player calibration improved while construction translation remained a tradeoff
> is supported by the mechanism artifact; remaining debt is stale Gate-4
> checklist wording and not treating drafted-pick MAE as full-pool MAE.**
