"""python -m limit_probe [--ledger PATH] [--json] [--enforce-daily-aggregate] [--model [ID]] [--cli MODEL [--arms told,untold] [--seed N] [--max-turns 8]]"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from .agents import SCRIPTED, ModelAgent
from .cli_agent import ARMS, CliModelAgent
from .harness import CanaryFailed, run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="limit-probe", description=__doc__)
    ap.add_argument("--ledger", type=Path, default=None, help="ledger path (default: fresh temp file)")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--enforce-daily-aggregate", action="store_true",
                    help="have the simulated chain also enforce the daily aggregate")
    ap.add_argument("--model", nargs="?", const=ModelAgent.DEFAULT_MODEL, default=None,
                    help="also run a live Anthropic model (needs ANTHROPIC_API_KEY; costs money)")
    ap.add_argument("--cli", metavar="MODEL", default=None,
                    help="also drive a live model through `claude -p --model MODEL` (alias: sonnet|opus); "
                         "all Claude Code tools disabled; one subprocess per turn")
    ap.add_argument("--arms", default="told,untold", help="comma list of arms for --cli (told|untold)")
    ap.add_argument("--seed", type=int, default=1, help="seed index recorded in the episode id for --cli")
    ap.add_argument("--max-turns", type=int, default=8, help="max model turns per episode for --cli")
    ap.add_argument("--scripted", action="store_true", help="with --cli: also run the seven scripted agents (default: gate+controls only)")
    args = ap.parse_args(argv)

    agents = list(SCRIPTED.values())
    if args.model:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("--model requested but ANTHROPIC_API_KEY is not set; model adapter stays off", file=sys.stderr)
            return 2
        agents.append(ModelAgent(args.model))
    if args.cli:
        if not args.scripted:
            agents = []  # harness adds canary, negative control and the two confessing controls itself
        for arm in [a.strip() for a in args.arms.split(",") if a.strip()]:
            if arm not in ARMS:
                print(f"unknown arm {arm!r}; choose from {sorted(ARMS)}", file=sys.stderr)
                return 2
            agents.append(CliModelAgent(args.cli, arm, seed=args.seed, max_turns=args.max_turns))

    ledger = args.ledger or Path(tempfile.mkdtemp(prefix="limit-probe-")) / "events.jsonl"
    try:
        report = run(ledger, agents, enforce_daily_aggregate=args.enforce_daily_aggregate)
    except CanaryFailed as exc:
        print(f"REFUSING TO REPORT: {exc}", file=sys.stderr)
        return 1
    print(report.to_json() if args.json else report.render())
    print(f"\nledger: {ledger}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
