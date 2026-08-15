# Branch B — light where/why (B−D ≤ 0)

**Ladder:** `results/phase2_v3bb_ladder.md` / `.json`  
**Construction:** `onestep_continuation_marginal_v1` · strategy `adp_v3bb`  
**Stop rule:** pick changes + **B−D ≤ 0** → **active but falsified**; freeze; no tune; no horizon↑ / λ / B.1.1.

This is a **light** audit (stop table: optional pick-trace). Full “OC validated” audit is **not** licensed — mean B−D is negative.

---

## Verdict

| Check | Finding |
| --- | --- |
| Policy-active? | **Yes** — 60/60 boards diverge; 703 changed picks (~11.7/board) |
| Useful vs D? | **No** — full-starter mean B−D **−57.5**, median **−53.1**, WR **37%**, 38/60 negative |
| Mechanism interesting? | **Mostly one artifact** — see below |

---

## 1. Where

- **First divergence:** round **1** on **60/60** boards.
- Cascade: mean ~11.7 later picks differ once R1 forks (path dependence), not independent late-round intelligence.

## 2. What

- **First fork position pair:** **QB→WR on 60/60** boards.
- Matches smoke (`phase2_v3bb_smoke.md`): D top1 Josh Allen (QB); B top1 a WR (Tyreek / Jefferson) with **tied or near-tied** \(M_B = M_D + C\).

## 3. Why (continuation arithmetic on empty R)

At R1, roster empty:

- Take WR \(w\): \(C \approx M_D(\text{best QB})\)
- Take QB \(q\): \(C \approx M_D(\text{best WR})\)

So \(M_B(w) \approx M_D(w)+M_D(q)\) and \(M_B(q) \approx M_D(q)+M_D(w)\) — **nearly equal**.  
Tie-break (ADP / name) then prefers the **WR**, so B systematically opens WR while D opens the higher single-pick \(M_D\) (QB).

That is **candidate-induced** \(C(R')\) in the narrow Gate P sense, but on real R1 boards it is largely an **additive double-count / tie-break** effect, not a deep roster-need story. Gate N still passed on a **late** TE/DST fixture; it did not forbid this early empty-roster pathology.

## 4. Concentration / tails

- Loss is broad (38/60 neg), not a single-board fluke.
- p10 **−288** (full); some large positive outliers (max **+530**) do not rescue the mean.
- Ex-DST / ex-DST+TE shrink |Δ| (−12 / −2) but stay ≤ 0 mean — DST/TE attribution is not the main story; the R1 QB→WR fork is.

## 5. Classification (frozen table)

> **Pick changes + B−D ≤ 0 → falsified as useful construction.**  
> Freeze Branch B operationalization. Do **not** weight \(C\), lengthen horizon, add λ/CVaR, or invent B.1.1.

**Do not** read this as “opportunity cost falsified forever” — only this **one-step max-next-\(M_D\)** additive form.  
**Do not** resurrect V2 / multi-round without a new licensed design.

---

## Status board

| Layer | Status |
| --- | --- |
| Gates P∧N | ✅ pass |
| Smoke | ✅ M_D reuse; formula; R1 order change |
| 60-board B−D | ❌ **active + falsified** (mean −57.5) |
| UI | `marginal` · `evaluable=0` |
