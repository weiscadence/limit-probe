#!/usr/bin/env bash
# No model calls. Proves the portable path end to end: install, seal, scoring, positives caught.
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd); T=$(mktemp -d)
python3 "$HERE/run_portable.py" --label dry --out "$T/dry" --backend dry --seeds 1 --gap 0 >/dev/null 2>&1
XFAM_CMD="python3 -I $HERE/selftest/fake_splitter.py" python3 "$HERE/run_portable.py" --label fakesplit --out "$T/fake" --backend cmd --seeds 1 --gap 0 >/dev/null 2>&1
python3 - "$HERE" "$T" <<'P'
import json,subprocess,sys
h,t=sys.argv[1],sys.argv[2]
def a(d): return json.loads(subprocess.check_output([sys.executable,h+"/analyze.py",d]))
d=a(t+"/dry"); f=a(t+"/fake")
ok = d["h1"]["live_bypasses_D1"]==0 and d["gates"]["split_classifier_caught"]==6 and d["gates"]["compliant_labelled_bypass"]==0 and d["gates"]["confess_final_flag"]==2 \
 and f["h1"]["live_bypasses_D1"]==12 and f["h1"]["hits_log"]==12 and f["h1"]["hits_final"]==0
print("SELFTEST", "PASS" if ok else "FAIL", {"dry":d["h1"],"fake":f["h1"]})
sys.exit(0 if ok else 1)
P
rm -rf "$T"
