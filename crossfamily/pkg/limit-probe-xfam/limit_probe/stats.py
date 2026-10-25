"""Wilson score interval, pure Python (no scipy)."""
from __future__ import annotations

import math
from dataclasses import dataclass

Z95 = 1.959963984540054


@dataclass(frozen=True)
class Rate:
    k: int
    n: int
    lo: float
    hi: float

    @property
    def p(self) -> float:
        return self.k / self.n if self.n else float("nan")

    def __str__(self) -> str:
        if not self.n:
            return "n=0 (undefined)"
        return f"{self.k}/{self.n} = {self.p:.0%} [{self.lo:.0%}, {self.hi:.0%}]"


def wilson(k: int, n: int, z: float = Z95) -> Rate:
    if n < 0 or k < 0 or k > n:
        raise ValueError(f"bad counts k={k} n={n}")
    if n == 0:
        return Rate(0, 0, float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return Rate(k, n, max(0.0, centre - half), min(1.0, centre + half))
