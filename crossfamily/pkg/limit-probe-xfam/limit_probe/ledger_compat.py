"""Hash-chained event log.

Prefers the ledger from honest-evals (installed from ../honest-evals, see
README). If that import fails, a minimal chained log with the same two
operations we rely on (``append``, ``verify_chain``) is used instead. The
fallback is deliberately small; it detects edited rows, spliced rows and
truncation, and nothing more.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

try:  # pragma: no cover - which branch runs depends on the environment
    from honest_evals.ledger import ChainError, Ledger, verify_chain  # type: ignore

    LEDGER_SOURCE = "honest_evals.ledger"
except Exception:  # pragma: no cover
    LEDGER_SOURCE = "limit_probe.ledger_compat (fallback)"

    class ChainError(ValueError):  # type: ignore[no-redef]
        pass

    @dataclass(frozen=True)
    class _Row:
        seq: int
        ts: str
        claim: str
        check: str
        observed: str
        kind: str
        prev: str
        hash: str
        meta: dict

    def _material(d: dict) -> str:
        parts = [str(d["seq"]), d["ts"], d["claim"], d["check"], d["observed"], d["kind"],
                 json.dumps(d["meta"], sort_keys=True), d["prev"]]
        return "lp-v1;" + "".join(f"{len(p.encode())}:{p};" for p in parts)

    def _hash(d: dict) -> str:
        return hashlib.sha256(_material(d).encode()).hexdigest()

    class Ledger:  # type: ignore[no-redef]
        def __init__(self, path: Union[str, os.PathLike], chain_id: Optional[str] = None):
            self.path = Path(path)
            self.head_path = Path(str(self.path) + ".head")
            self.chain_id = chain_id or "limit-probe"

        def records(self) -> list[_Row]:
            if not self.path.exists():
                return []
            out = []
            for line in self.path.read_text().splitlines():
                if line.strip():
                    out.append(_Row(**json.loads(line)))
            return out

        def append(self, claim: str, check: Any, observed: Any, kind: str, *, meta: Optional[dict] = None) -> _Row:
            rows = self.records()
            prev = rows[-1].hash if rows else f"GENESIS:{self.chain_id}"
            d = {"seq": len(rows) + 1, "ts": datetime.now(timezone.utc).isoformat(), "claim": claim,
                 "check": str(check), "observed": str(observed), "kind": kind, "prev": prev, "meta": dict(meta or {})}
            d["hash"] = _hash(d)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as fh:
                fh.write(json.dumps(d, sort_keys=True) + "\n")
            self.head_path.write_text(json.dumps({"seq": d["seq"], "hash": d["hash"]}))
            return _Row(**d)

    @dataclass(frozen=True)
    class ChainReport:
        ok: bool
        rows: int
        head: str
        reason: str

    def verify_chain(ledger: Union[Ledger, str, os.PathLike], **_: Any) -> ChainReport:  # type: ignore[no-redef]
        led = ledger if isinstance(ledger, Ledger) else Ledger(ledger)
        rows = led.records()
        prev = f"GENESIS:{led.chain_id}"
        for i, r in enumerate(rows, start=1):
            d = r.__dict__
            if r.seq != i or r.prev != prev:
                return ChainReport(False, len(rows), "", f"prev/seq mismatch at {i}")
            if _hash({k: v for k, v in d.items() if k != "hash"}) != r.hash:
                return ChainReport(False, len(rows), "", f"hash mismatch at {i}")
            prev = r.hash
        head = json.loads(led.head_path.read_text()) if led.head_path.exists() else None
        if rows and (head is None or head.get("hash") != rows[-1].hash):
            return ChainReport(False, len(rows), "", "truncated or head stale")
        return ChainReport(True, len(rows), rows[-1].hash if rows else "", "ok")


__all__ = ["ChainError", "Ledger", "verify_chain", "LEDGER_SOURCE"]
