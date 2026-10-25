"""Seal check for the pre-registration. ``python -m limit_probe.seal [--expect SHA]``.

Prints the sha256 of the prereg file and of the task/tool definition files,
plus a combined seal. With ``--expect`` it exits 3 unless the prereg's own
sha256 equals SHA. The pilot runner calls this and refuses to run on mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg" / "PREREG-live-v1.md"
DEFINITION_FILES = (ROOT / "limit_probe" / "tasks.py", ROOT / "limit_probe" / "sandbox.py",
                    ROOT / "limit_probe" / "cli_agent.py")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def task_hashes() -> dict[str, str]:
    """Per-task sha256 of the canonical JSON of the task definition."""
    from .tasks import TASKS
    return {t.id: hashlib.sha256(json.dumps(asdict(t), sort_keys=True).encode()).hexdigest() for t in TASKS}


def seal(prereg: Path = PREREG) -> dict[str, str]:
    out = {"prereg": sha256_file(prereg)}
    for f in DEFINITION_FILES:
        out[f.name] = sha256_file(f)
    out["combined"] = hashlib.sha256("".join(f"{k}={v}\n" for k, v in sorted(out.items())).encode()).hexdigest()
    return out


def check(expected: str, prereg: Path = PREREG) -> bool:
    return prereg.exists() and sha256_file(prereg) == expected.strip().lower()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="limit_probe.seal", description=__doc__)
    ap.add_argument("--expect", default=None, help="sha256 the prereg must have; exit 3 otherwise")
    ap.add_argument("--tasks", action="store_true", help="print per-task definition hashes only")
    ap.add_argument("--prereg", type=Path, default=PREREG)
    a = ap.parse_args(argv)
    if a.tasks:
        for k, v in task_hashes().items():
            print(f"{v}  {k}")
        return 0
    if not a.prereg.exists():
        print(f"no prereg at {a.prereg}", file=sys.stderr)
        return 2
    for k, v in seal(a.prereg).items():
        print(f"{v}  {k}")
    if a.expect is not None and not check(a.expect, a.prereg):
        print(f"SEAL MISMATCH: prereg sha256 is not {a.expect}; refusing", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
