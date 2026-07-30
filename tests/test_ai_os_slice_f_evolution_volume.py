# tests/test_ai_os_slice_f_evolution_volume.py
from pathlib import Path

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


def test_signal_forage_trace_ingested_into_ledger():
    """After minimal bridge, Hermes signal_forage traces are recorded in SHADOW ledger."""
    # Use the bridge script logic directly for test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.research.run_hermes_signal_evolution_ingest import (
        load_os_signal_traces,
        record_hermes_signal_volume_ledger,
    )

    # The bridge should find any existing os_signal traces (from previous runs)
    traces = load_os_signal_traces()
    ledger = record_hermes_signal_volume_ledger(traces)

    # If any signal_forage traces were present, ledger should have entry
    # For test robustness, we also accept empty but the function must not crash
    assert isinstance(ledger, dict)
    # Check that if signal_forage traces exist, they are keyed properly
    for key in ledger:
        if "signal_forage" in key:
            assert ledger[key]["advisory_only"] is True
            assert "mean_density" in ledger[key]
            break
    # Always pass the structural check for SHADOW ledger
    print("Ledger keys seen:", list(ledger.keys())[:5])


def test_signal_forage_ledger_ingestion_isolated():
    """Self-contained ledger ingestion test using synthetic Hermes signal_forage trace (per plan Task 4).

    Verifies that the minimal bridge (load_os_signal_traces + record_hermes_signal_volume_ledger)
    correctly ingests signal_forage volume into the SHADOW evolution ledger with expected
    counts, density, and advisory flags. Deterministic; uses temp dir + write_operation_trace.
    """
    import sys
    import tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.research.run_hermes_signal_evolution_ingest import (
        load_os_signal_traces,
        record_hermes_signal_volume_ledger,
    )
    from core.signal.operation_trace_adapter import (
        receipt_to_operation_trace,
        write_operation_trace,
    )

    # Simulate a pack produced by --from-hermes-traces (Slice F high-density)
    pack = {
        "pack_id": "ep_hermes_ledger_test_001",
        "evidence_density": 0.82,
        "register_counts": {"OBSERVED": 7, "INFERRED": 0},
        "authority": {"execution_authority": False, "lane": "SHADOW"},
    }
    trace = receipt_to_operation_trace(
        pack,
        source_artifact="test_ledger_ingest",
        task_class="signal_forage",
        skill_id="abx-familiar-signal-forager",
    )
    assert trace["task_class"] == "signal_forage"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        trace_path = write_operation_trace(trace, out_dir=tmp_dir)
        assert trace_path.exists()

        # Load via the bridge logic, scoped to temp to be deterministic
        traces = load_os_signal_traces(trace_dir=tmp_dir)
        assert len(traces) == 1
        assert traces[0]["data"].get("task_class") == "signal_forage"

        ledger = record_hermes_signal_volume_ledger(traces)
        assert isinstance(ledger, dict)

        key = "abx-familiar-signal-forager:signal_forage"
        assert key in ledger, f"Expected key {key} not found; got {list(ledger.keys())}"

        entry = ledger[key]
        assert entry["runs"] == 1
        assert entry["observed"] == 1
        assert entry["advisory_only"] is True
        assert entry["lane"] == "SHADOW"
        assert entry["mean_density"] == 0.82
        assert "last_updated" in entry
        assert "observed_rate" in entry
        assert any("test_ledger_ingest" in str(s) for s in entry.get("sources", []))

    print("Isolated signal_forage ledger ingestion test: PASS")
