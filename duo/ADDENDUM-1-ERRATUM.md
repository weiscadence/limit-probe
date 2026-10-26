# ADDENDUM-1 erratum

PREREG-DUO-ADDENDUM-1.md says it was "written 2026-10-26 ~03:55Z". That time was a guess written into the file. The real write time was about 03:37Z. The git commit time is authoritative: commit 7a0296b, 2026-10-26T03:37:45Z.

No agent call on the amended harness came before that commit. The one-episode smoke run (runs-smoke/addendum1-smoke.json) was committed at 03:38:17Z. The earliest entry in any runs/*/driver.log is 03:38:32Z. The only calls before the commit were the three design-review calls (reviews/), and none of them was an agent or judge call. The addendum text and its sealed hash are not changed.
