"""limit-probe: do agents with a wallet tool try to step outside a hard limit, and do monitors notice."""
from .harness import CanaryFailed, Report, run

__all__ = ["CanaryFailed", "Report", "run"]
