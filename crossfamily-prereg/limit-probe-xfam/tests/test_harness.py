import json

import pytest

from limit_probe import classifier, harness
from limit_probe.agents import CANARY, MONITOR_CONTROLS, NEGATIVE_CONTROL, SCRIPTED, Compliant
from limit_probe.classifier import BYPASS, COMPLIED, Verdict
from limit_probe.harness import CanaryFailed, Episode, canary_gate, run
from limit_probe.tasks import TASKS


def test_full_run_passes_gate_and_verifies_chain(tmp_path):
    rep = run(tmp_path / "events.jsonl")
    assert rep.chain_ok
    assert len(rep.episodes) == len(SCRIPTED) * len(TASKS) + 2  # + two confessing controls
    assert rep.control == "OK"
    assert len(rep.bypass_rates) >= 3
    assert all(e.verdict.label == BYPASS for e in rep.episodes if e.agent == CANARY)
    assert all(e.verdict.label == e.expected for e in rep.episodes if e.agent == NEGATIVE_CONTROL)
    json.loads(rep.to_json())
    assert "Wilson" in rep.render()


def test_summary_monitor_misses_what_the_log_shows(tmp_path):
    rep = run(tmp_path / "events.jsonl")
    summary = rep.monitor_catch["summary-only (final message)"]
    rule = rep.monitor_catch["rule-based (tool stream)"]
    assert summary.p < 0.5 < rule.p
    assert any(e.startswith(CANARY) for e in rep.monitor_misses["summary-only (final message)"])


def test_gate_refuses_when_classifier_goes_blind(tmp_path, monkeypatch):
    blind = lambda events, task, limit: Verdict(COMPLIED, ("blind",), False)
    monkeypatch.setattr(harness, "classify", blind)
    with pytest.raises(CanaryFailed, match="missed"):
        run(tmp_path / "events.jsonl")


def test_gate_refuses_when_everything_looks_like_a_bypass(tmp_path, monkeypatch):
    paranoid = lambda events, task, limit: Verdict(BYPASS, ("paranoid",), False)
    monkeypatch.setattr(harness, "classify", paranoid)
    with pytest.raises(CanaryFailed, match="negative control"):
        run(tmp_path / "events.jsonl")


def test_gate_refuses_without_canary_or_control():
    v = Verdict(BYPASS, ("x",), False)
    with pytest.raises(CanaryFailed, match="did not run"):
        canary_gate([Episode("a/t", "a", "t", COMPLIED, v, "")])


def test_gate_is_added_even_if_caller_omits_it(tmp_path):
    rep = run(tmp_path / "events.jsonl", agents=[Compliant()])
    assert {e.agent for e in rep.episodes} == {CANARY, NEGATIVE_CONTROL, *MONITOR_CONTROLS}


def test_definitions_are_ordered_and_distinct(tmp_path):
    rep = run(tmp_path / "events.jsonl")
    d1, d2, d3, d4 = rep.bypass_rates.values()
    assert d4.k <= d1.k <= d2.k <= d3.k and len({d1.k, d2.k, d3.k, d4.k}) >= 3


def test_enforcing_daily_aggregate_changes_success_not_attempts(tmp_path):
    loose = run(tmp_path / "a.jsonl")
    strict = run(tmp_path / "b.jsonl", enforce_daily_aggregate=True)
    d1 = next(k for k in loose.bypass_rates if k.startswith("D1"))
    d4 = next(k for k in loose.bypass_rates if k.startswith("D4"))
    assert loose.bypass_rates[d1].k == strict.bypass_rates[d1].k
    assert strict.bypass_rates[d4].k < loose.bypass_rates[d4].k
