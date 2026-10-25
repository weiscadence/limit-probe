"""The model adapter is exercised with a fake client only. No network, no key."""
import types

import pytest

from limit_probe.agents import ModelAgent
from limit_probe.cli import main
from limit_probe.sandbox import events_from_ledger


def test_adapter_is_off_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="disabled"):
        ModelAgent()


def test_cli_refuses_model_flag_without_key(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["--model"]) == 2
    assert "stays off" in capsys.readouterr().err


class _Block(types.SimpleNamespace):
    pass


class FakeClient:
    """Scripts a model that calls split_payment, then writes a clean summary."""

    def __init__(self):
        self.calls = 0
        self.messages = self

    def create(self, **kw):
        self.calls += 1
        assert kw["tools"] and kw["system"]
        if self.calls == 1:
            return types.SimpleNamespace(stop_reason="tool_use", content=[
                _Block(type="tool_use", id="tu1", name="split_payment",
                       input={"to": "0xVENDOR", "total": 250, "parts": 3})])
        # second turn must carry the tool_result back
        last = kw["messages"][-1]
        assert last["role"] == "user" and last["content"][0]["tool_use_id"] == "tu1"
        return types.SimpleNamespace(stop_reason="end_turn", content=[_Block(type="text", text="Invoice paid in full.")])


def test_fake_model_tool_calls_land_in_ledger(wallet, ledger):
    w, t = wallet("urgent_above")
    agent = ModelAgent(client=FakeClient())
    msg = agent.run(t, w)
    assert msg == "Invoice paid in full."
    tools = [e.tool for e in events_from_ledger(ledger, w.episode)]
    assert tools == ["pay", "pay", "pay", "split_payment"]


def test_adapter_stops_at_max_turns(wallet):
    class Loopy:
        def __init__(self):
            self.messages = self
            self.n = 0

        def create(self, **kw):
            self.n += 1
            return types.SimpleNamespace(stop_reason="tool_use", content=[
                _Block(type="tool_use", id=f"t{self.n}", name="balance", input={})])

    w, t = wallet("under_limit")
    c = Loopy()
    ModelAgent(client=c, max_turns=3).run(t, w)
    assert c.n == 3 and len(w.calls) == 3
