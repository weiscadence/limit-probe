#!/usr/bin/env python3
"""Portable runner for prereg-ext-crossfamily (limit-probe live v1 protocol, any model family).

The sealed package (limit_probe/, prereg/PREREG-live-v1.md) is used byte-for-byte. The only
thing replaced is the transport: the sealed adapter spawns `claude -p` per turn and reads
{"result": TEXT} from its stdout. Here the same argv (system prompt, model label) and the same
per-turn prompt go to a pluggable backend, and the reply text is wrapped in the same
{"result": TEXT} envelope. Parsing, scoring, monitors, ledger: unchanged sealed code.

Backends (XFAM_BACKEND):
  openai  OpenAI-compatible chat API. Env: XFAM_BASE_URL, XFAM_API_KEY, XFAM_MODEL.
          Request = [system, user] messages only. No temperature/top_p set (sealed run set none).
  cmd     Any command. Env: XFAM_CMD. stdin gets JSON {"system": str, "user": str, "model": str};
          stdout must be the model's reply text, verbatim. Non-zero exit = failed call.
  dry     No model. Always replies {"final": "dry run"}. For install checks only; writes to
          a separate out dir and is never part of the result.

Usage:
  python3 run_portable.py --label grok-4.3 --out ./out-grok          # full run, 5 seeds
  python3 run_portable.py --label dry --out ./out-dry --backend dry --seeds 1   # smoke test
Rerunning the same command resumes (finished units have a DONE marker).
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from limit_probe import cli as lp_cli  # noqa: E402
from limit_probe import cli_agent  # noqa: E402
from limit_probe import seal as lp_seal  # noqa: E402
from limit_probe import summarize as lp_summarize  # noqa: E402
from limit_probe.ledger_compat import LEDGER_SOURCE  # noqa: E402

SEALED_PREREG = "5a276bb77190ab6fd4f55280b11aed4e07cc3c2593902bce4d837731cbfd8772"
SEALED_COMBINED = "2771c6f8f9641d5d86d43a14698423ef88313824a787341d833cc49dadfe8f17"
BUDGET = 480          # model calls per family (same number as the sealed budget_turns)
SEEDS = (1, 2, 3, 4, 5)
MAX_TURNS = 8


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Backend:
    def __init__(self, kind: str, devlog: Path, gap: float):
        self.kind, self.devlog, self.gap = kind, devlog, gap
        self.resolved = set()
        if kind == "openai":
            for k in ("XFAM_BASE_URL", "XFAM_API_KEY", "XFAM_MODEL"):
                if not os.environ.get(k):
                    raise SystemExit(f"backend openai needs {k}")
        elif kind == "cmd" and not os.environ.get("XFAM_CMD"):
            raise SystemExit("backend cmd needs XFAM_CMD")
        elif kind not in ("openai", "cmd", "dry"):
            raise SystemExit(f"unknown backend {kind}")

    def _dev(self, msg: str) -> None:
        with open(self.devlog, "a") as f:
            f.write(f"{now()} DEVIATION {msg}\n")

    def _once(self, system: str, user: str, label: str) -> tuple[int, str, str, str]:
        """-> (rc, text, stderr, resolved_model_id)"""
        if self.kind == "dry":
            return 0, '{"final": "dry run"}', "", "dry"
        if self.kind == "cmd":
            p = subprocess.run(os.environ["XFAM_CMD"], shell=True, capture_output=True, text=True, timeout=300,
                               input=json.dumps({"system": system, "user": user, "model": label}))
            return p.returncode, p.stdout, p.stderr, os.environ.get("XFAM_MODEL_ID", label)
        body = json.dumps({"model": os.environ["XFAM_MODEL"],
                           "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(os.environ["XFAM_BASE_URL"].rstrip("/") + "/chat/completions", data=body,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + os.environ["XFAM_API_KEY"]})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            return 0, d["choices"][0]["message"]["content"] or "", "", d.get("model", os.environ["XFAM_MODEL"])
        except urllib.error.HTTPError as e:
            return e.code, "", f"HTTP {e.code}: {e.read()[:500]!r}", ""
        except Exception as e:  # network, bad JSON
            return 1, "", f"{type(e).__name__}: {e}", ""

    def runner(self, argv: list[str], stdin: str) -> tuple[int, str, str]:
        """Drop-in for cli_agent.subprocess_runner. Same envelope the sealed parser expects."""
        system = argv[argv.index("--system-prompt") + 1]
        label = argv[argv.index("--model") + 1]
        time.sleep(self.gap)
        delay = 60
        for attempt in range(1, 7):
            rc, text, err, mid = self._once(system, stdin, label)
            transient = rc in (429, 500, 502, 503, 529) or re.search(r"rate.?limit|overloaded|429", err, re.I)
            if rc != 0 and transient and attempt < 6:
                self._dev(f"transport-retry attempt={attempt} rc={rc} pause={delay}s")
                time.sleep(delay); delay = min(delay * 2, 1800); continue
            break
        if rc != 0:
            return (rc if 0 < rc < 256 else 1), "", err
        self.resolved.add(mid)
        return 0, json.dumps({"result": text, "model": mid, "backend": self.kind}), ""


def calls_so_far(out: Path) -> int:
    n = 0
    for f in out.glob("units/*/events.jsonl"):
        n += sum(1 for line in open(f) if '"kind": "model_reply"' in line or '"kind":"model_reply"' in line)
    return n


def three_consecutive_fail(events: Path) -> bool:
    run = worst = 0
    for line in open(events):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("kind") != "model_reply":
            continue
        run = run + 1 if r.get("meta", {}).get("rc", 0) != 0 else 0
        worst = max(worst, run)
    return worst >= 3


def manifest(out: Path) -> str:
    lines = []
    for f in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
        lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(out)}")
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    return hashlib.sha256((out / "MANIFEST.sha256").read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="model label recorded in episode ids, [a-z0-9.-] only, e.g. grok-4.3")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--backend", default=os.environ.get("XFAM_BACKEND", "openai"))
    ap.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    ap.add_argument("--gap", type=float, default=float(os.environ.get("XFAM_GAP", "3")), help="seconds before each call")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9.\-]{0,40}", a.label):
        raise SystemExit("label must match [a-z0-9][a-z0-9.-]* (no colons: the analysis splits on ':')")
    seeds = [int(s) for s in a.seeds.split(",")]
    if a.backend != "dry" and seeds != list(SEEDS):
        print("WARNING: non-default seeds; a partial run is reported as partial", file=sys.stderr)
    out = a.out.resolve(); (out / "units").mkdir(parents=True, exist_ok=True)
    devlog = out / "DEVIATIONS.log"; devlog.touch()
    status = out / "status.log"

    def log(msg: str) -> None:
        print(msg, file=sys.stderr)
        with open(status, "a") as f:
            f.write(f"{now()} {msg}\n")

    with contextlib.redirect_stdout(io.StringIO()) as buf:
        rc = lp_seal.main(["--expect", SEALED_PREREG])
    (out / "seal-check.txt").write_text(buf.getvalue())
    if rc != 0 or SEALED_COMBINED not in buf.getvalue():
        log("SEAL MISMATCH - refusing to run"); return 3

    be = Backend(a.backend, devlog, a.gap)
    cli_agent.subprocess_runner = be.runner  # the one substitution; see module docstring

    for seed in seeds:
        u = out / "units" / f"{a.label}-s{seed}"
        if (u / "DONE").exists():
            continue
        if u.exists():
            aside = u.with_name(u.name + ".aborted-" + datetime.now(timezone.utc).strftime("%H%M%S"))
            u.rename(aside)
            with open(devlog, "a") as f:
                f.write(f"{now()} DEVIATION unit {u.name} rerun after incomplete attempt (kept aside, excluded)\n")
        used = calls_so_far(out)
        if used >= BUDGET:
            log(f"BUDGET reached ({used}) - stopping before {u.name}"); break
        u.mkdir()
        log(f"start {u.name} (calls so far {used})")
        (u / "run.txt").write_text(json.dumps({
            "label": a.label, "seed": seed, "arms": "told,untold", "max_turns": MAX_TURNS, "backend": a.backend,
            "base_url": os.environ.get("XFAM_BASE_URL", ""), "requested_model": os.environ.get("XFAM_MODEL", ""),
            "sealed_prereg": SEALED_PREREG, "sealed_combined": SEALED_COMBINED, "ledger_source": LEDGER_SOURCE,
            "python": platform.python_version(), "started": now()}, indent=1) + "\n")
        argv = ["--cli", a.label, "--arms", "told,untold", "--seed", str(seed), "--max-turns", str(MAX_TURNS),
                "--ledger", str(u / "events.jsonl"), "--json"]
        err = io.StringIO()
        with open(u / "report.json", "w") as rep, contextlib.redirect_stdout(rep), contextlib.redirect_stderr(err):
            try:
                rc = lp_cli.main(argv)
            except Exception as e:  # crash = failed unit, never a result
                print(f"CRASH {type(e).__name__}: {e}", file=sys.stderr); rc = 9
        (u / "stderr.txt").write_text(err.getvalue())
        with open(u / "summary.txt", "w") as s, contextlib.redirect_stdout(s), contextlib.redirect_stderr(s):
            try:
                lp_summarize.main([str(u / "report.json")]) if hasattr(lp_summarize, "main") else None
            except SystemExit:
                pass
            except Exception as e:
                print(f"summary failed: {e}")
        if (u / "events.jsonl").exists() and three_consecutive_fail(u / "events.jsonl"):
            log(f"STOP RULE 3: 3 consecutive failed calls in {u.name} - aborting, nothing reported from this unit")
            with open(devlog, "a") as f:
                f.write(f"{now()} STOP RULE 3 in {u.name}\n")
            break
        if rc != 0:
            log(f"FAIL {u.name} rc={rc} - stopping"); break
        (u / "DONE").touch()
        log(f"done {u.name} rc=0 calls={calls_so_far(out)} resolved_models={sorted(be.resolved)}")

    m = manifest(out)
    log(f"MANIFEST sha256 {m}  (units done: {len(list(out.glob('units/*/DONE')))}; calls: {calls_so_far(out)})")
    print(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
