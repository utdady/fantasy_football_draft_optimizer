# Autopsy gate — experimental discipline

**Status:** active product rule  
**Instrumentation:** `46f5691` (not a strategy commit)  
**Production TAKE:** frozen V1 **`marginal`** (`M`) only  
**Not authorized:** shipping survival / lookahead / VOR / construction into TAKE

---

## Principle

> We are not currently building V2. We are deciding whether V2 deserves to exist.

`marginal` is the **control group**. Every future strategy must beat it under a predefined evaluation before it may influence TAKE.

`live_sim` generates realistic boards. Autopsy tooling inspects decisions **without** changing recommendations.

```text
TAKE → frozen marginal
     → live_sim real board
     → awkward / disagreement pick
     → dump case + log disagree (as felt)
     → offline analyze (M, P(survive), Δ)
     → classify
     → only then a hypothesis / experiment
```

---

## What to dump

Do **not** dump only 1.01. Dump picks that feel questionable:

1. **R1 QB vs RB/WR** (Allen vs Gibbs/Puka/…)
2. **Won't survive** — TAKE says wait; board looks like it will take him
3. **Obviously survives** — TAKE says take now
4. **Positional runs** — 3+ RB/WR/QB/TE in a burst
5. **Awkward roster / FLEX** — RB–WR–FLEX interactions
6. **Late-round weirdness** — especially `M ≈ 0`

Log disagreements **exactly as experienced**. Do not pre-decide the category must be scarcity.

Example:

```text
Pick: 1.01
TAKE: Josh Allen
Human: Jahmyr Gibbs
Category: opportunity_cost
Reason: elite RB much harder to replace than QB
```

---

## Gates (required before Path A)

### Gate 1 — Frozen case

```powershell
python -m draftopt.autopsy case --draft-id <id>
```

### Gate 2 — Transparent autopsy

For the first awkward cases, **do not aggregate**. Analyze named candidates:

```powershell
python -m draftopt.autopsy analyze --draft-id <id> --players "Josh Allen,Jahmyr Gibbs,Puka Nacua" --out results/autopsy_r1.md
```

Inspect **separately**: `M`, crude `P(survive)`, `Δ(EV−M)`.

Question: **does the future-board term contain enough signal to explain the human disagreement?**

A ranking flip is interesting; the **explanation** matters more at first.

`P(survive)` and ADP-greedy next-pick are **crude diagnostic stubs**. Do not conclude from one number (e.g. “17% → draft Gibbs”).

If the stub never helps explain real disagreements → **do not build lookahead**.

### Gate 3 — Human judgment under the clock

```powershell
python -m draftopt.autopsy disagree --draft-id <id> --recommended "..." --chosen "..." --category opportunity_cost --reason "..."
```

Categories: `opportunity_cost` · `bad_data` · `roster_construction` · `human_policy` · `uncertainty` · `rec_sensible` · `other`

---

## Success criterion (after ~20–30 awkward picks)

Classify disagreements; **then** choose the next build:

| Mostly this | Next step |
| --- | --- |
| Opportunity cost / survival | V2 experiment *may* earn a ticket |
| Projection / data / news | Information layer, not V2 |
| “I just don’t want R1 QB” | Path C policy overlay |
| TAKE was actually reasonable | Leave `marginal` alone |

Until that table exists, no new optimizer strategy.

---

## Paths

| Path | Meaning | Risk |
| --- | --- | --- |
| **A** | New ranking engine in TAKE | High — V3-B lesson |
| **B** | Diagnostic overlay beside TAKE | Low — only after offline autopsies |
| **C** | Soft policy (e.g. no R1 QB) | Product preference, not math superiority |

---

Artifacts: `results/autopsy_cases/` · `results/autopsy_disagreements.jsonl`
