"""Seal check: the pilot must refuse when the prereg's sha differs from the sealed value."""
import hashlib

from limit_probe.seal import PREREG, check, main, seal, task_hashes
from limit_probe.tasks import TASKS


def test_task_hashes_match_the_prereg_table():
    text = PREREG.read_text()
    hashes = task_hashes()
    assert set(hashes) == {t.id for t in TASKS}
    for tid, h in hashes.items():
        assert f"| {tid} |" in text and h in text, f"prereg table is stale for {tid}"


def test_seal_refuses_on_mismatch(tmp_path, capsys):
    p = tmp_path / "PREREG.md"
    p.write_text("sealed text\n")
    good = hashlib.sha256(p.read_bytes()).hexdigest()
    assert check(good, p) and main(["--prereg", str(p), "--expect", good]) == 0
    p.write_text("sealed text, edited after sealing\n")
    assert not check(good, p) and main(["--prereg", str(p), "--expect", good]) == 3
    assert "MISMATCH" in capsys.readouterr().err
    assert main(["--prereg", str(tmp_path / "missing.md")]) == 2


def test_seal_covers_definition_files():
    s = seal()
    assert {"prereg", "tasks.py", "sandbox.py", "cli_agent.py", "combined"} <= set(s)
    assert s["prereg"] == hashlib.sha256(PREREG.read_bytes()).hexdigest()
