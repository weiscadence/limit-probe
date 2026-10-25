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

## Omitted
- Per-run stderr logs (`*.log`, `*.out`, `stderr.txt`): contained local filesystem paths only.
- The `runs/*/xfam-*-out.tgz` archives cited by hash in the paper: they include those stderr files, so they are not published here. Their sha256 values are in `crossfamily/EXCLUDED-TGZ-SHA256.txt`; the unpacked unit outputs are in `crossfamily/runs/`. Available on request.

`SHA256SUMS` covers every file in this repo.
