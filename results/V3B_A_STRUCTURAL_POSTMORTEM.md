# V3-B Branch A structural postmortem

**Status:** frozen reading of `00e2a75` + diagnostic
[`phase2_v3ba_structural_inertness.md`](phase2_v3ba_structural_inertness.md).

**Not to be confused with V3-A** (calibration map). This is **V3-B Branch A**
(`adp_v3ba` / `crosspos_empty_need_marginal_v1`).

---

## 1. What the ladder showed

- A−D ≡ 0 on 60 boards
- **0/60** boards with ≥1 pick change
- Decision-time check: **A top1 = D top1 on 900/900** user picks

That result is **real**. The interpretation below is what it means.

---

## 2. Better reading (locked)

> **This operationalization was structurally near-inert** — not a strong
> empirical falsification that “cross-position opportunity cost doesn’t matter.”

Wrong sentence: *OC failed; therefore only lookahead remains.*  
Right sentence: *Single-reference, position-excluded \(M_D(p)-M_D(q^*)\) does not
meaningfully re-rank vs D under this draft regime.*

---

## 3. Two mechanisms that explain 900/900 identity

### A. Incumbent protection (early / mid starter needs)

\(q^*(p)\) excludes **all** of \(\mathrm{pos}(p)\). So the unique global \(M_D\)
argmax \(p^*\) only subtracts the best *other-position* need player, while
cross-position rivals can subtract \(p^*\) itself.

Diagnostic: **structural_protected** on **285/900 (31.7%)** of decisions —
especially **R1–R2 at 100%**, still high through R5–R6. Among protected
decisions, **A≠D count = 0**.

### B. Missing-alternative fallback (late / filled capacity)

When \(\mathcal{A}(p)=\emptyset\), \(M_A:=M_D\) by contract.

Diagnostic: **cross_alt_missing on 534/900 (59.3%)**. Unprotected breakdown is
almost entirely this fallback (534) plus tied global max (81). Still **A≠D = 0**.

Together: **~91%** of decisions are either incumbent-protected or exact \(M_D\)
fallback. The remainder (tied \(M_D\) max) also never diverged on these boards.

---

## 4. Same-position near-ties are a red herring

Same-pos \(M_D\) gaps: median **0**, mean ~4.5 (many ties).

That **cannot** create A≠D: within a position everyone shares the same outside
\(q^*\), so \(M_A\) is an affine shift of \(M_D\) and preserves order.

---

## 5. Implications for Branch B (and any further myopic OC)

Licensed: continue to a **Branch B design** artifact (one-step state-dependent),
with an explicit **shape guard**:

> Forbidden: scores \(M_D(p)-c(p)\) where \(c\) is constant across candidates or
> systematically smaller for the current \(M_D\)-argmax than for cross-position
> rivals (the B.1 / Branch A failure mode).

Not licensed: “OC is false” or automatic multi-horizon V2 resurrection.

---

## 6. Status

| Item | Status |
| --- | --- |
| Ladder `00e2a75` | 🟢 real 0/60 identity |
| Structural diagnostic | 🟢 run (900 decisions) |
| Reading | 🟢 **structurally near-inert** |
| A.1 retune | 🔴 forbidden |
| Branch B | 🟡 design licensed; must avoid trivial-shift shape |
| UI | `marginal` · `evaluable=0` |
