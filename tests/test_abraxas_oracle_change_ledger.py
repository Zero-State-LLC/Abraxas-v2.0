"""Tests for core/abraxas_oracle_change_ledger.py (HARDENING candidate 8993d4faf76813d7)"""

from core.abraxas_oracle_change_ledger import (
    stable_hash,
    load_ledger,
    record_change,
)

def test_stable_hash():
    h = stable_hash({"a": 1, "b": 2})
    assert isinstance(h, str)
    assert len(h) == 16

def test_record_change_roundtrip(tmp_path, monkeypatch):
    import core.abraxas_oracle_change_ledger as mod
    monkeypatch.setattr(mod, "LEDGER_PATH", tmp_path / "change_ledger.v1.json")
    entry = record_change(
        path="core/test.py",
        operation="MODIFY",
        reason="test",
        candidate_requirement="example",
        before_hash=None,
        after_hash="abc123",
    )
    assert entry["operation"] == "MODIFY"
    ledger = load_ledger()
    assert len(ledger) >= 1
    assert ledger[-1]["path"] == "core/test.py"
