#!/usr/bin/env bash
# Print the sha256 of the prereg and of the task/tool/adapter definition files, plus a combined seal.
# Usage: prereg/seal.sh            -> prints hashes; the first line is the prereg sha to pass as --sealed
#        prereg/seal.sh --expect SHA -> exit 3 if the prereg sha differs
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
exec "$PY" -m limit_probe.seal "$@"
