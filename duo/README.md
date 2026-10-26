# duo: two-agent joint overspend (paper v2, sections 3 and 5)

Copy of projects/limit-probe-duo at commit 62f37f7. Read PREREG-DUO.md, PREREG-DUO-ADDENDUM-1.md (+ ADDENDUM-1-ERRATUM.md), PREREG-DUO-ADDENDUM-2.md, then DUO-RESULTS.md. Reproduce every number: `python3 driver/table.py runs` (pilot: `runs-pilot`). Design reviews: `reviews/`.

Data: runs/ (analysed, 800 episodes), runs-pilot/ (pre-addendum Mistral pilot), runs-truncated/ (token-cap-truncated legs, not analysed), runs-smoke/ (not analysed).

## Scrub edits (the only changes vs the sealed originals)
Absolute home paths were replaced by paths relative to the script, and orkey.py reads OPENROUTER_API_KEY from the environment instead of a local key file. Omitted: runs/*.out (driver stdout with local paths) and __pycache__. Sealed sha256 of the edited files before scrubbing (match SEAL*.sha256 where listed):

```
b728f7d938fbfc0c38e99efec8fc17599daab0d0176ff354f24a394291a42264  reviews/ask.py
9735c5e03c24e59dddd3025e01215c67729b72c21e9643fe6d637e6861989a8f  driver/table.py
2b6285f96fa37a40ca1162686b6e2b0d157048fc1085c040e8f8170e7615ff2d  driver/drive.py
0693eb2afc68e20f381f1a4313b6ea3fa32223935c7e5bafb7145f7aebf272b4  probe/fr.py
686c88c15531a34fbc88ea21d6a7f10a511422972f6b95d1340fd6360a38358d  probe/fr2.py
e089b1fda4a7388fe48979401f3dfdf8d913a8b1ff786b4818b5a0b350ec3b42  driver/orkey.py
```
