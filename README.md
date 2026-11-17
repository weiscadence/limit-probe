# limit-probe

Code and data for "A Monitor That Cannot Acquit" (Apart Research AI Collusion Sprint, October 2026). Jason Gibbs, with Cadence.

## Preexisting vs sprint work (paper Appendix C)

**Preexisting, before 2026-10-23:**
- `code/` - limit-probe at git HEAD 18a98aa (commits up to 2026-10-16), incl. the sealed preregistration `code/prereg/PREREG-live-v1.md` and pilot. Depends on honest-evals (github.com/weiscadence/honest-evals), also preexisting.

**New during the sprint (2026-10-23 onward):**
- `fullrun/` - the 10-unit full run: report.json, hash-chained events.jsonl, summary.txt per unit; `analysis/analyze.py`, `result.json`, MANIFEST.
- `crossfamily-prereg/` - cross-family preregistration and portable runner as frozen before the extension ran (its "NOT RUN" note predates the runs below).
- `crossfamily/` - the cross-family extension:
  - `pkg/limit-probe-xfam/` - harness package, prereg, amendments `prereg/AMEND-1..4.md`, seal.sh, tests.
  - `driver/` - scripts that drove the runs, scoring, and the LLM-judge pass (set `OPENROUTER_API_KEY`).
  - `runs/<model>/` - per-model unit outputs and `result.json`; `runs/llmjudge-all.jsonl`, `hetero-amend2.json`.
  - `FRONTIER-TIER.md`, `LLMJUDGE.md` - write-ups.

See `BUNDLE-README.md` for the original bundle notes and hashes.

- `duo/` - the pre-registered two-agent duo experiment (paper v2 sections 3 and 5): prereg, addenda, design reviews, driver, all episode data, DUO-RESULTS.md. See `duo/README.md`.

## Omitted
- Per-run stderr logs (`*.log`, `*.out`, `stderr.txt`): contained local filesystem paths only.
- The `runs/*/xfam-*-out.tgz` archives cited by hash in the paper: they include those stderr files, so they are not published here. Their sha256 values are in `crossfamily/EXCLUDED-TGZ-SHA256.txt`; the unpacked unit outputs are in `crossfamily/runs/`. Available on request.

`SHA256SUMS` covers every tracked file except the three files named `SHA256SUMS` (itself and the two copies inside the `limit-probe-xfam` packages). Check with `sha256sum -c SHA256SUMS`.

## Reading notes (added 2026-11-17 after an outside review)
- `code/` and `BUNDLE-README.md` are frozen pre-sprint text and are left byte-identical. `code/README.md` still says "Status: prototype" and "Not run yet", and `BUNDLE-README.md` says the cross-family extension was "NOT RUN". Both predate the live runs: results are in `fullrun/`, `crossfamily/` and `duo/`.
- `code/README.md` counts "5 agents x 6 tasks = 30 scored episodes" next to a monitor table over 16 + 26 = 42. Both are right: seven scripted agents x 6 tasks = 42 episodes; the canary (`scripted-always-split`) and the negative control (`scripted-compliant`) are run and shown to the monitors but not scored for bypass rates, leaving 5 x 6 = 30. The 16 bypasses are 10 scored (definition D1) + 6 canary.
- `APPENDIX-DENOMINATOR.md` is computed from a private claim ledger (`data/claim-ledger.jsonl`, `scripts/claim-ledger.js`) that is not in this repo, so its table cannot be re-derived from here.
- `duo/DUO-RESULTS.md`: see its "Review notes" section for what the H1 PASS and the pooled Fisher p do and do not support.
