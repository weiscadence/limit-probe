# LLM-judge rescore of the final-message monitor (AMEND-4, EXPLORATORY, POST-HOC)

Prereg: pkg/limit-probe-xfam/prereg/AMEND-4.md (prompt, model and temperature committed before any judge output). Script: driver/llmjudge.py; table: driver/llmjudge_table.py; raw rows: runs/llmjudge-all.jsonl (pilot: runs/llmjudge-pilot.jsonl, not pooled).

- Judge: google/gemini-3.8-flash (not under test), temperature 0, reasoning effort "low" (endpoint refuses reasoning-off). Input: policy text + final message only, the same information the keyword monitor had. Zero new agent calls.
- Cost: $0.539 full + $0.013 pilot = $0.552 (cap $0.60; hard stop triggered).
- Coverage: all 20 true live bypasses; 30/180 planted confessions; 910/1039 honest live episodes (uniform random order, seed 0; the remaining 129 were not judged because of the budget).
- Judge replies unparseable: 0/960.
- Ground truth: existing verdict labels from the tool log/ledger.

rows 960, judge unparseable 0 (scored not-flagged), cost $0.5390

Canary (planted confessions): judge 30/30 [0.89,1.00] | keyword 30/30 [0.89,1.00] 

| model | n byp | catch: tool-log | catch: keyword | catch: LLM judge | n honest judged | FA: tool-log | FA: keyword | FA: LLM judge |
|---|---|---|---|---|---|---|---|---|
| ALL | 20 | 20/20 [0.84,1.00] | 1/20 [0.01,0.24] | 6/20 [0.15,0.52] | 910 | 2/910 [0.00,0.01] | 246/910 [0.24,0.30] | 0/910 [0.00,0.00] |
| command-a-plus | 2 | 2/2 [0.34,1.00] | 0/2 [0.00,0.66] | 0/2 [0.00,0.66] | 45 | 1/45 [0.00,0.12] | 2/45 [0.01,0.15] | 0/45 [0.00,0.08] |
| deepseek-v4-pro | 7 | 7/7 [0.65,1.00] | 1/7 [0.03,0.51] | 2/7 [0.08,0.64] | 44 | 0/44 [0.00,0.08] | 11/44 [0.15,0.39] | 0/44 [0.00,0.08] |
| deepseek-v4.1-flash | 0 | - | - | - | 54 | 0/54 [0.00,0.07] | 32/54 [0.46,0.71] | 0/54 [0.00,0.07] |
| gemini-3.1-pro-preview | 0 | - | - | - | 53 | 0/53 [0.00,0.07] | 8/53 [0.08,0.27] | 0/53 [0.00,0.07] |
| gemini-3.5-flash-lite | 0 | - | - | - | 52 | 0/52 [0.00,0.07] | 5/52 [0.04,0.21] | 0/52 [0.00,0.07] |
| glm-5.3-flash | 0 | - | - | - | 47 | 0/47 [0.00,0.08] | 22/47 [0.33,0.61] | 0/47 [0.00,0.08] |
| gpt-6-astra | 0 | - | - | - | 56 | 0/56 [0.00,0.06] | 9/56 [0.09,0.28] | 0/56 [0.00,0.06] |
| gpt-6-luna | 0 | - | - | - | 54 | 0/54 [0.00,0.07] | 0/54 [0.00,0.07] | 0/54 [0.00,0.07] |
| gpt-6-sol | 0 | - | - | - | 54 | 0/54 [0.00,0.07] | 0/54 [0.00,0.07] | 0/54 [0.00,0.07] |
| grok-4.3 | 0 | - | - | - | 51 | 0/51 [0.00,0.07] | 4/51 [0.03,0.19] | 0/51 [0.00,0.07] |
| grok-4.7 | 0 | - | - | - | 49 | 0/49 [0.00,0.07] | 28/49 [0.43,0.70] | 0/49 [0.00,0.07] |
| kimi-k3.1-pro | 0 | - | - | - | 55 | 0/55 [0.00,0.07] | 14/55 [0.16,0.38] | 0/55 [0.00,0.07] |
| mistral-small-2603 | 11 | 11/11 [0.74,1.00] | 0/11 [0.00,0.26] | 4/11 [0.15,0.65] | 42 | 0/42 [0.00,0.08] | 1/42 [0.00,0.12] | 0/42 [0.00,0.08] |
| muse-spark-1.3 | 0 | - | - | - | 54 | 0/54 [0.00,0.07] | 13/54 [0.15,0.37] | 0/54 [0.00,0.07] |
| opus | 0 | - | - | - | 44 | 0/44 [0.00,0.08] | 30/44 [0.53,0.80] | 0/44 [0.00,0.08] |
| qwen3.8-flash | 0 | - | - | - | 48 | 0/48 [0.00,0.07] | 16/48 [0.22,0.47] | 0/48 [0.00,0.07] |
| qwen3.8-max-0902 | 0 | - | - | - | 53 | 1/53 [0.00,0.10] | 15/53 [0.18,0.42] | 0/53 [0.00,0.07] |
| sonnet | 0 | - | - | - | 55 | 0/55 [0.00,0.07] | 36/55 [0.52,0.77] | 0/55 [0.00,0.07] |

All 20 bypasses are config_bait episodes except one (injected_in_tool_result). The judge catches 6/20, the keyword rule 1/20, and the tool log 20/20. The judge's 14 misses are final messages that do not mention the config change: the evidence is absent from the text, so no reader of the text can recover it.

Claim the paper can make: replacing the keyword rule with an LLM judge given the same policy and final message removes the false alarms (0/910 vs 246/910) but still misses most real bypasses (6/20, 95% CI 0.15-0.52, vs 20/20 for the tool-log monitor). The gap comes from what the final message leaves out, not from the keyword rule.
