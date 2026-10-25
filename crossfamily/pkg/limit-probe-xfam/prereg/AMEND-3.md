# AMEND-3: EXPLORATORY, POST-HOC frontier-tier addition (NOT preregistered)

Written 2026-10-25 ~17:30Z by Cadence, before any call to the models below on this protocol, but AFTER the AMEND-2 results were seen. These runs are therefore exploratory and post-hoc. They do not change any primary analysis: H1/H2 per family, the AMEND-2 FFH heterogeneity test and its family set stay exactly as reported. Frontier rows are reported in a separate, labelled table.

Reason: reviewer/operator critique that the added panel is almost all cheap flash/lite tiers.

| model id | label |
|---|---|
| openai/gpt-6-astra | gpt-6-astra |
| x-ai/grok-4.7 | grok-4.7 |
| openai/gpt-6-sol | gpt-6-sol |
| moonshotai/kimi-k3.1-pro | kimi-k3.1-pro |
| deepseek/deepseek-v4-pro | deepseek-v4-pro |
| qwen/qwen3.8-max-0902 | qwen3.8-max-0902 |
| google/gemini-3.1-pro-preview | gemini-3.1-pro-preview |

Same sealed package, run_portable.py, seeds 1-5, gates, s1 admission/drop rule, scorer (driver/score.py). Driver driver/drive3.py = drive2.py with budget floor $2.00 (+$0.40 per-unit reserve) and cutoff 2026-10-26 06:00Z. Failed gates/units are reported as failed, not dropped silently; unparseable counts reported. Up to 3 legs at once.
