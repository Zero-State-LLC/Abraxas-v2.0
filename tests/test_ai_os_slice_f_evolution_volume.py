# tests/test_ai_os_slice_f_evolution_volume.py
import json
from pathlib import Path
import pytest

from core.signal.operation_trace_adapter import receipt_to_operation_trace

def test_signal_forage_trace_has_correct_task_class():
    """Hermes volume traces must carry task_class=signal_forage for evolution ledger."""
    # Simulate a pack produced by --from-hermes-traces
    pack = {
        "pack_id": "ep_hermes_test_001",
        "evidence_density": 0.82,
        "register_counts": {"OBSERVED": 7, "INFERRED": 0},
        "authority": {"execution_authority": False, "lane": "SHADOW"},
    }
    trace = receipt_to_operation_trace(
        pack,
        source_artifact="test",
        task_class="signal_forage",
        skill_id="abx-familiar-signal-forager",
    )
    assert trace["task_class"] == "signal_forage"
    assert trace["skill_id"] == "abx-familiar-signal-forager"
    assert trace["advisory_only"] is True
    assert "authority" in trace

def test_evolution_ledger_would_see_signal_forage():
    """Placeholder: evolution ledger ingestion should accept signal_forage traces."""
    # This will fail until Task 4 wires ledger handling
    pytest.fail("evolution ledger does not yet index task_class=signal_forage from Hermes volume")
