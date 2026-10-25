import json

from limit_probe.ledger_compat import verify_chain
from limit_probe.sandbox import events_from_ledger


def test_every_tool_call_lands_in_chain(wallet, ledger):
    w, t = wallet()
    w.call("balance")
    w.call("pay", to=t.legit_to, amount=t.legit_amount)
    w.finish("done")
    ev = events_from_ledger(ledger, w.episode)
    assert [e.tool for e in ev] == ["balance", "pay", "final_message"]
    assert ev[1].args == {"to": t.legit_to, "amount": t.legit_amount}
    assert ev[1].result["status"] == "rejected"
    assert verify_chain(ledger).ok


def test_editing_a_row_is_detected(wallet, ledger):
    w, t = wallet("under_limit")
    w.call("pay", to=t.legit_to, amount=40)
    w.call("balance")
    lines = ledger.path.read_text().splitlines()
    row = json.loads(lines[0])
    row["meta"]["args"]["amount"] = 4  # make the payment look smaller after the fact
    lines[0] = json.dumps(row, sort_keys=True)
    ledger.path.write_text("\n".join(lines) + "\n")
    rep = verify_chain(ledger)
    assert not rep.ok and "hash" in rep.reason


def test_dropping_the_last_row_is_detected(wallet, ledger):
    w, t = wallet("under_limit")
    w.call("pay", to=t.legit_to, amount=40)
    w.call("edit_config", key="daily_limit", value="999")
    lines = ledger.path.read_text().splitlines()
    ledger.path.write_text("\n".join(lines[:-1]) + "\n")  # hide the config edit
    rep = verify_chain(ledger)
    assert not rep.ok and "truncat" in rep.reason


def test_episodes_do_not_leak_into_each_other(ledger, wallet):
    a, t = wallet("under_limit")
    b, _ = wallet("at_limit")
    a.call("pay", to=t.legit_to, amount=40)
    b.call("balance")
    assert [e.tool for e in events_from_ledger(ledger, a.episode)] == ["pay"]
    assert [e.tool for e in events_from_ledger(ledger, b.episode)] == ["balance"]
