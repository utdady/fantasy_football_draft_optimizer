# Branch B — Gates P & N

**Construction:** `onestep_continuation_marginal_v1`  
**Strategy (post-gate):** `adp_v3bb`  
**Formula:** \(M_B(p)=M_D(p\mid R)+C(R\cup\{p\})\), \(C(R')=\max_q M_D(q\mid R')\)

## Result

| Gate | Status | Evidence |
| --- | --- | --- |
| **P** (positive — can reverse D’s A≻B via different \(C(R')\)) | **PASS** | `tests/test_onestep_continuation.py` |
| **N** (negative — no spurious reverse when continuation gap shouldn’t flip) | **PASS** | same |

Command:

```text
python -m pytest tests/test_onestep_continuation.py -q
```

## Fixture notes

Empty-roster fixtures yield the **same** \(C\) for both candidates (same remaining empty needs), so they cannot demonstrate Gate P. Gates use a **partially filled** roster with only TE and DST still open:

- **Gate P:** D prefers TE (\(M_D=100\)) over DST (\(90\)); after TE, continuation is weak DST; after DST, continuation is strong TE → \(M_B\) prefers DST.
- **Gate N:** Same skeleton; DST close under D; alts ~80 so continuation gap ≤5 and D order is preserved under \(M_B\).

## Gate

**P ∧ N → licensed** to register `adp_v3bb`, run smoke, then 60-board B−D.
