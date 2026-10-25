#!/usr/bin/env bash
# Pilot: 1 seed x 6 tasks x 2 arms x 1 model (sonnet) through `claude -p`. Refuses unless the
# prereg's sha256 equals --sealed SHA. Output: runs/<timestamp>/{events.jsonl,report.json,summary.txt,seal.txt,run.txt}
# Usage: scripts/pilot.sh --sealed <sha256 of prereg/PREREG-live-v1.md> [--model sonnet] [--seed 1]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
SEALED=""; MODEL="sonnet"; SEED=1
while [ $# -gt 0 ]; do
  case "$1" in
    --sealed) SEALED="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    *) echo "unknown arg $1" >&2; exit 2;;
  esac
done
[ -n "$SEALED" ] || { echo "refusing: pass --sealed <prereg sha256> (see prereg/seal.sh)" >&2; exit 3; }
"$PY" -m limit_probe.seal --expect "$SEALED" > /tmp/limit-probe-seal.$$ || { cat /tmp/limit-probe-seal.$$; echo "refusing: prereg sha differs from --sealed" >&2; exit 3; }
command -v claude >/dev/null || { echo "refusing: claude CLI not on PATH" >&2; exit 3; }
OUT="runs/$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$OUT"
mv /tmp/limit-probe-seal.$$ "$OUT/seal.txt"
{ echo "model=$MODEL seed=$SEED arms=told,untold max_turns=8 sealed=$SEALED"; claude --version; git rev-parse HEAD; } > "$OUT/run.txt"
echo "pilot -> $OUT  (12 episodes, <= 96 claude -p calls)"
"$PY" -m limit_probe --cli "$MODEL" --arms told,untold --seed "$SEED" --max-turns 8 --ledger "$OUT/events.jsonl" --json > "$OUT/report.json"
"$PY" -m limit_probe.summarize "$OUT/report.json" | tee "$OUT/summary.txt"
"$PY" - "$OUT" <<'PYEOF' | tee -a "$OUT/summary.txt"
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1] + "/events.jsonl") if l.strip()]
calls = sum(1 for r in rows if r["kind"] == "model_reply")
print(f"claude -p calls made: {calls}   (full-run rule: k = min(5, 480 // {calls}) = {min(5, 480 // max(calls, 1))})")
PYEOF
