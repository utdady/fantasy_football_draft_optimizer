# Autopsy gate — experimental discipline

**Status:** active product rule  
**Instrumentation:** `46f5691` (not a strategy commit) · live_sim `9225113`  
**Production TAKE:** frozen V1 **`marginal`** (`M`) only  
**Autopsy stubs:** frozen (crude sigmoid + ADP-greedy next-pick) — **do not improve yet**  
**Not authorized:** shipping survival / lookahead / VOR / construction into TAKE

---

**Docs spine:** [../ROADMAP.md](../ROADMAP.md) · [../docs/LAB_LOG.md](../docs/LAB_LOG.md) (E007) · [../docs/PROJECT.md](../docs/PROJECT.md) · [../docs/FORMAL.md](../docs/FORMAL.md)

## Current research state

```text
marginal
   │
   ├── production TAKE ──────────────── FROZEN
   │
   └── autopsy
          │
          ├── Gate 1: empty 1.01 ────── CLOSED (pass / inconclusive)
          │     artifact: results/autopsy_r1.md  (04d7304)
          │     do not rerun Allen/Gibbs on empty boards
          │
          └── Gate 2: live_sim ──────── NEXT
                    │
                    ├── collect disagreements (as felt)
                    ├── include a few “TAKE was right” controls
                    ├── classify causes
                    └── ask whether future value is the
                        dominant missing signal on real boards
```

---

## Gate 1 — CLOSED

Empty 1.01, slot 1, draft `eb8374278e41`.

| Question | Answer |
| --- | --- |
| Is `marginal` behaving strangely? | **No.** Allen 369.21 > Gibbs 365.27 > Puka 356.57 (~4 pt M gap) |
| Is there a plausible better draft objective? | **Possibly.** Stub 2-pick EV: Allen ~642, Gibbs ~688 |
| Does that authorize V2? | **No.** Same long-wait V2-alpha family; already failed production |

The autopsy **explains why** a human might prefer Gibbs without proving the proposed solution is better. Those two questions stay un-blurred.

**Forbidden:** more empty-board Allen/Gibbs variations.

---

## Gate 2 — live_sim (open)

Do **not** manufacture cases. Let the draft produce them.

**Post-pick capture (UI):** after *your* pick is committed, if chosen ? TAKE the app auto-dumps the case with frozen pre-pick TAKE math, then pauses for optional category/note. Continue never blocks (`skipped_reason=true` if no category). Autopick / CPU / opponent live_sim seats do not trigger this. Observability only ? TAKE stays `marginal`.


High-value logs:

| | When | Example |
| --- | --- | --- |
| **A** | TAKE you strongly reject | TAKE QB, you RB |
| **B** | TAKE wait / other; you think X disappears | “X won’t survive” |
| **C** | Rec changes a lot after a positional run | board-state response |
| **D** | TAKE feels obviously correct | **control**, not just complaints |

Log **exactly as experienced**. Do not pre-assign scarcity.

Sample size: enough **distinct failure modes**, not an arbitrary 100 drafts.

If the first ~15 awkward decisions cluster as:

| Pattern | Then the project is… |
| --- | --- |
| “won’t survive” | opportunity-cost / possible V2 ticket later |
| “projection is stale” | information layer, not V2 |
| “I just don’t want QB early” | Path C policy |
| TAKE was actually reasonable | leave `marginal` |

Until that classification exists, **no new optimizer strategy** and **no better survival model**.

We are asking: *does this frozen hypothesis repeatedly explain live disagreements?*  
Only a consistent **yes** earns engineering on a real survival model.

---

## Frozen stubs (do not retune)

- `P(survive)` — crude ADP sigmoid  
- next-pick — ADP-greedy `two_pick_ev`  

Improving them now would be building a beautiful survival model for a problem that may not dominate.

---

## Loop

**Frozen `marginal` → live_sim → dump + disagree → offline analyze (same stubs) → classify → only then Path B/A/C.**

```powershell
python -m draftopt.autopsy case --draft-id <id>
python -m draftopt.autopsy analyze --draft-id <id> --players "A,B,C" --out results/autopsy_<label>.md
python -m draftopt.autopsy disagree --draft-id <id> --recommended "..." --chosen "..." --category ... --reason "..."
```

Categories: `opportunity_cost` · `bad_data` · `roster_construction` · `human_policy` · `uncertainty` · `rec_sensible` · `other`

---

## Paths (still gated)

| Path | Meaning | When |
| --- | --- | --- |
| **A** | New ranking engine in TAKE | Only after live classification + beat-control |
| **B** | Diagnostic overlay beside TAKE | After offline autopsies, still not TAKE |
| **C** | Soft policy (e.g. no R1 QB) | If disagreements are preference, not math |

Artifacts: `results/autopsy_cases/` · `results/autopsy_disagreements.jsonl` · `results/autopsy_r1.md`
