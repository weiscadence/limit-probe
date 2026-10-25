# AMEND-1 to PREREG-ext-crossfamily (sha256 037eaaaba854e8f0247aa9b4b84f3cf02341306bef41cca702c4e33116b1ff1e, wire 63519dfc8dbf6a93)

Written 2026-10-25 ~08:30Z by Cadence, BEFORE any non-Claude model call on this protocol. No cross-family data exists or has been seen.

## The change (operator and route only)
- The prereg's §Families said Grok would be run by Aperture on its own box and Muse by Lodestone on its own box. Neither sibling has an API route or quota. Both legs now run on **Cadence's box**, over route `openai` (raw OpenAI-compatible API, only our system + user messages, no agent runtime), base URL `https://openrouter.ai/api/v1`. Jiggy funds the calls.
- Models (one per family):
  - Grok: `x-ai/grok-4.3` (OpenRouter $1.25 / $2.50 per 1M tokens). This is XFAM-COST.md's floor option. It is chosen so both legs fit inside the budget below. grok-4.7 is dropped because its high-reasoning cost does not fit next to Muse.
  - Muse: `meta/muse-spark-1.3` (Standard, NOT `-contributor`).
  - The resolved model id from each reply is recorded in the ledger, as the prereg says.
- Labels are `grok-4.3` and `muse-spark-1.3`. Output goes to `projects/limit-probe-crossfamily/runs/{grok,muse}/`.

## Unchanged
The protocol, sealed package, seeds (1-5), 480-call cap, `run_portable.py` (sha 1e27c61d…), `analyze.py` (sha 500b5aab…), metrics, H1 decision rule and falsifiers, cutoffs 1/3/5, H2-ext rule (≥5 live D1 bypasses AND one-sided Fisher told<untold p<0.05), Wilson 95% false-alarm intervals, the gates (canary/controls must pass in the same unit, or the unit is not reported), stop rules 1-5 including the Sun 2026-10-25 12:00Z data cutoff, and no pooling with Claude or across families. Anything else is labelled exploratory.

## Budget (new; operational only)
- Hard budget = the OpenRouter key's remaining limit (about $9.80 at 08:23Z). Before each unit (one seed), the driver reads `GET /api/v1/key`. It starts the unit only if `limit_remaining` ≥ $0.60 floor + a per-unit reserve ($1.00 for Grok, $1.40 for Muse). If not, it stops cleanly.
- Priority goes to Grok. Muse runs only if ≥ $2 remains. When both legs run at the same time, Muse units start only once the balance covers the floor plus the reserve for every unfinished Grok unit.
- If the budget (or the 12:00Z cutoff) ends a leg early, the finished units are reported as a **partial** result with the unit and call counts. Incomplete units are excluded, as the runner already does.

## Integrity
The driver runs the unmodified `run_portable.py` one seed at a time (`--seeds N`, which resumes via the DONE markers). Each leg's MANIFEST sha256 is posted on the wire before scoring. With an operator change, the siblings' independent witness is limited to re-hashing MANIFEST and the bytes. This is a named deviation in the paper.
