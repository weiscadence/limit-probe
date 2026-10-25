# limit-probe: artifact bundle for "A Monitor That Cannot Acquit" (Apart AI Collusion Sprint, Oct 2026)

- code/: limit-probe at git HEAD 18a98aa (git archive; private launch script with a local key path removed).
  PREEXISTING: everything in code/ was written before the sprint (commits up to 2026-10-16).
- code/prereg/PREREG-live-v1.md: sealed preregistration (sha256 5a276bb7...8772); seal.sh recomputes the combined seal 2771c6f8...8f17.
- fullrun/: NEW during the sprint. Per-unit report.json, hash-chained events.jsonl, summary.txt for all 10 (model, seed) units;
  analysis/analyze.py, result.json (713f7df4...f159), MANIFEST.sha256; seal-check.txt from run time.
- crossfamily-prereg/: NEW during the sprint. PREREG-ext-crossfamily (sha256 037eaaab...1ff1e) and the portable runner. NOT RUN.
- Recompute: python3 fullrun/analysis/analyze.py (see the header of that file for paths).
- SHA256SUMS covers every file in this bundle.
