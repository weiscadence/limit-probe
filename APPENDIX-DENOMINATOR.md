# Appendix: errors per auditable claim (reviewer fix #1 from paper 1)

STATUS: MEASURED 2026-10-23 from existing machinery. No new data was collected for this appendix.

## Source
- Ledger: `data/claim-ledger.jsonl` (Cadence), 35 rows, hash chain verified (`claim-ledger.js verify` → CHAIN OK; canary PASS).
  sha256 `d81dbd80738934bb909f8bbb33b8e7f613eac685733286df23fbdaf2afdaea8d`.
- Window: 2026-09-18 → 2026-10-14. The ledger has had no new rows since 10-14. It is dormant, and that is reported as a limit.
- Built for this purpose after paper 1: every claim is written at UTTERANCE TIME with `kind`, an `auditable` flag
  (a mechanical check exists) and a `checkCmd`. A later SETTLE row records the verdict and its verifier.
- Command: `node scripts/claim-ledger.js rate --days 60`.

## Result
Paper 1 reported "62 corrections over 23 days" (a count over time). The rate the reviewer asked for:

| | claims | auditable | settled | errors | rate | Wilson 95% |
|---|---|---|---|---|---|---|
| All (tool's rule) | 18 | 17 | 17 | 6 | 0.35 | [0.17, 0.59] |
| All, unresolvable excluded (KC1 F2 rule) | | | 16 | 6 | 0.375 | [0.19, 0.61] |

By verifier (who settled it):

| verifier | settled | errors | rate | Wilson 95% |
|---|---|---|---|---|
| self-canary | 10 (1 unresolvable) | 5 | 0.50 | [0.24, 0.76] |
| self-rerun | 4 | 0 | 0.00 | [0.00, 0.49] |
| log-evidence | 2 | 0 | 0.00 | [0.00, 0.66] |
| external | 1 | 1 | 1.00 | [0.21, 1.00] |

By claim type: existence 4/8 (0.50), numeric 1/4, state 1/4, causal 0/1 (the one causal claim is unresolvable).

## What this does and does not show
- It is a DETECTED-error frequency, a lower bound. Audit coverage here is 17/17, so nothing auditable went unchecked, but n is tiny.
- The verifier split is confounded with claim choice. Self-canary checks were aimed at claims already in doubt, which is why that rate (0.50) is far above the self-rerun rate (0.00). Per-verifier rates are descriptive only.
- Existence claims ("X exists / is applicable / compiles") carry most of the errors (4 of 6). That fits paper 1's stale-belief error class.
- n=16–17 has no power for between-cell comparisons; every interval overlaps.
- Same-author ledger: the claimant also chose which claims to log. This is a self-selected record (limit).
