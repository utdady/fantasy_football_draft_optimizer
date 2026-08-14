# V2-beta design (pilot)

Equal-weight mixture of deterministic futures — no Monte Carlo, no learned weights.

\[
EV_\beta(p)=\tfrac13\bigl(EV_{ADP}(p)+EV_{proj}(p)+EV_{VOR}(p)\bigr)
\]

Each \(EV_f\) uses the same two-pick raw starter objective as V2-alpha
(`L(R∪{p,q})` with `q` = best raw marginal among survivors), but advances the
board under future policy \(f\) instead of only ADP-greedy.

| | Alpha | Beta |
| --- | --- | --- |
| Strategy | `marginal_v2` | `marginal_v2_beta` |
| Futures | ADP-greedy only (frozen) | ADP + proj + VOR, equal weight |
| UI default | still `marginal` | still `marginal` |

## Success (pilot)

Shrink proj-greedy catastrophe relative to α while keeping **most** of α’s
noisy-ADP edge. Not required to fully eliminate losses.

## Eval command (slot-1 lean pilot)

```powershell
python -m draftopt.stress_opponent --n 10 --slots 1 --seed 0 `
  --out results/stress_v2beta_pilot_slot1.md
```
