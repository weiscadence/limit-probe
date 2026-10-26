# PREREG-DUO ADDENDUM-2 (committed before any agent call on the changed harness; git commit time is authoritative)

## Cause, with evidence
The command-a-plus, qwen3.8-flash, deepseek-v4-pro and kimi-k3.1-pro legs under ADDENDUM-1 had very high unparseable rates. Kimi was dropped at the admission gate with 6/8. Every failed reply was either empty content or JSON cut off mid-string. The api_error count was 0.
- Cost of each failed call ≈ 1500 output tokens at list price. kimi: 1500 × $10/M = $0.0150 vs $0.0156–0.0158 observed. command-a: $0.00225 + input vs $0.0024. qwen: $0.0007 vs $0.00076.
- Direct reproduction (probe/fr2.py). A failing nochan context was rebuilt from the logs and replayed with the same seed. At max_tokens=1500, all three models tested (command-a-plus, qwen, deepseek) returned `finish_reason=length`, 1500 completion tokens, reasoning_tokens about 1500 or more, and empty content. The same context at 6000 gave `stop` and a valid JSON reply. DeepSeek needed 5936 tokens, close to that cap.
- So this was our harness's token cap cutting off hidden reasoning. It is a plumbing fault, not model behaviour.

## Change (the only one)
`duo.py` `AGENT_CALL_OVERRIDES`: for these four models only, agent calls use `max_tokens=12000` and `reasoning={'effort':'low'}`. Probe at that setting: all four return `stop` with valid JSON. Completion tokens: command-a 1504, kimi 415, deepseek 1826, qwen 6640. Effort low was added because without it deepseek and kimi reasoning makes the run unaffordable (estimated ≥$13 and ≥$50 per 100 episodes). This is a disclosed difference from the other legs, which use the provider default effort.
Unchanged: prompts, environment, labeller, monitors, judges, seeds, conditions, analysis, stop rules. The completed legs (mistral-small-2603, grok-4.7, gemini-3.5-flash-lite, gpt-6-luna) are unaffected. Their models are not in the override map, so their calls are byte-identical, and their data is untouched.

## Data handling
The partial ADDENDUM-1 data for the four affected legs moved to `runs-truncated/`: command-a-plus 100, deepseek-v4-pro 92, qwen3.8-flash 68, kimi 4. It is reported in the paper as truncated and is not analysed for the hypotheses. The four legs are relaunched fresh in `runs/` with the same seeds. Two smoke episodes per affected model (seed 0, runs-smoke/, not analysed) come first. Launch priority: deepseek. Floor $3, per-model cap $6, cutoff 09:30Z.
