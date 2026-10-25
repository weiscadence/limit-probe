# RUN: limit-probe cross-family extension (prereg-ext-crossfamily)

Read PREREG-ext-crossfamily.md first. Python 3.10+, stdlib only. No pip install needed.

## 0. Verify the bytes (2 min)
    sha256sum -c SHA256SUMS            # every file must say OK
    python3 -m limit_probe.seal --expect 5a276bb77190ab6fd4f55280b11aed4e07cc3c2593902bce4d837731cbfd8772
    # expect combined = 2771c6f8f9641d5d86d43a14698423ef88313824a787341d833cc49dadfe8f17
    ./selftest/selftest.sh             # no model calls; must print SELFTEST PASS

## 1. Post on the wire BEFORE the first call
Your label, route and requested model id, e.g.
"xfam pre-data: label=grok-4.3 route=openai model=grok-4.3 base=https://api.x.ai/v1".
Route `openai` = raw API, only our system + user messages. Route `cmd` through your agent runtime
counts as agent-mediated (see the prereg); say which.

## 2. Run (about 360-480 calls, serial, resumable)
Raw API (preferred):

    export XFAM_BACKEND=openai XFAM_BASE_URL=https://api.x.ai/v1 XFAM_MODEL=<model id>
    export XFAM_API_KEY=...            # your own key; never printed or logged by the runner
    nice -n 19 python3 run_portable.py --label <label> --out ./out-<label>

Any other call path: write a command that reads JSON {"system","user","model"} on stdin and prints
the model's reply text verbatim (no edits, no retries that change the text), then:

    export XFAM_BACKEND=cmd XFAM_CMD="python3 my_call.py" XFAM_MODEL_ID=<resolved model id>
    nice -n 19 python3 run_portable.py --label <label> --out ./out-<label>

Label: lowercase [a-z0-9.-], no colons. Gap between calls defaults to 3 s (--gap). On 429/5xx it
backs off 60 s doubling (6 tries) and logs each retry to DEVIATIONS.log. If it stops, rerun the same
command; finished units are kept (DONE), incomplete ones are set aside and logged.
Stops by itself at 480 calls, on 3 consecutive failed calls, or on a seal mismatch.

## 3. Do not touch the outputs
Don't edit, filter or re-run selected episodes. If something went wrong, say so on the wire; a
partial or failed run is reported as such.

## 4. Hand back
The runner prints the sha256 of out-<label>/MANIFEST.sha256 at the end.

    tar czf xfam-<label>-out.tgz out-<label>
    sha256sum xfam-<label>-out.tgz

Post both hashes on the wire (manifest sha + tgz sha), then drop the tgz. Cadence scores it with
`python3 analyze.py out-<label>` (unchanged sealed analysis) only after the hashes match.

## Expected output layout
    out-<label>/seal-check.txt  status.log  DEVIATIONS.log  MANIFEST.sha256
    out-<label>/units/<label>-s{1..5}/{run.txt, events.jsonl, report.json, summary.txt, stderr.txt, DONE}
Each unit: 12 live episodes (6 tasks x told/untold) plus canary and controls; report.json has
chain_ok, control, episodes[]. Per unit 12 to 96 model calls.

Due: Sun 2026-10-25 12:00Z. Later data is reported as late and stays out of the paper.
Questions: on the wire to Cadence.
