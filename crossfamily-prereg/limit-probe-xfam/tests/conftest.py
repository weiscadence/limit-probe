import pytest

from limit_probe.ledger_compat import Ledger
from limit_probe.sandbox import Wallet
from limit_probe.tasks import LIMIT, task_by_id


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "events.jsonl")


@pytest.fixture
def wallet(ledger):
    n = [0]

    def make(task_id="urgent_above", **kw):
        t = task_by_id(task_id)
        n[0] += 1  # episode ids must be unique within a ledger or episodes merge
        return Wallet(ledger, f"test{n[0]}/{task_id}", invoices=dict(t.invoices), limit=LIMIT, **kw), t
    return make
