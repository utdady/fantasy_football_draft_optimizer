# Autopsy gate — experimental discipline

**Status:** active product rule  
**Production TAKE:** frozen V1 **`marginal`** (`M`) only  
**Not authorized:** shipping survival / lookahead / VOR / construction into TAKE

---

## Principle

> We are not currently building V2. We are deciding whether V2 deserves to exist.

`marginal` is the **control group**. Every future strategy must beat it under a predefined evaluation before it may influence TAKE.

`live_sim` generates realistic boards. Autopsy tooling inspects decisions **without** changing recommendations.

---

## Gates (required before Path A)

### Gate 1 — Frozen case

Capture a concrete board (e.g. 1.01 Allen vs Gibbs vs Puka) via:

```powershell
python -m draftopt.autopsy case --draft-id <id>
```

### Gate 2 — Transparent autopsy

```powershell
python -m draftopt.autopsy analyze --draft-id <id> --players "Josh Allen,Jahmyr Gibbs,Puka Nacua" --out results/autopsy_r1.md
```

Ask: does a defensible future-board stub make Gibbs (or anyone) beat Allen on **EV**, and by how much (`Δ = EV − M`)?

If ranking does not flip → **do not build lookahead**.

### Gate 3 — Human judgment under the clock

During `live_sim`, log disagreements (UI or CLI):

```powershell
python -m draftopt.autopsy disagree --draft-id <id> --recommended "..." --chosen "..." --category opportunity_cost --reason "..."
```

Categories: `opportunity_cost` · `bad_data` · `roster_construction` · `human_policy` · `uncertainty` · `rec_sensible` · `other`

---

## Paths

| Path | Meaning | Risk |
| --- | --- | --- |
| **A** | New ranking engine in TAKE | High — V3-B lesson |
| **B** | Diagnostic overlay beside TAKE | Low — preferred next product experiment *after* offline autopsies |
| **C** | Soft policy (e.g. no R1 QB) | Product preference, not math superiority |

---

## Loop

**Frozen `marginal` → live draft → disagreement log → case dump → offline autopsy → one hypothesis → offline compare vs control → only then consider Path B/A.**

Artifacts: `results/autopsy_cases/` · `results/autopsy_disagreements.jsonl`
