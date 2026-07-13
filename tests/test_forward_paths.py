"""Tests for core/codegen/forward_paths.py (HARDENING candidate 6cce252458f35f88)"""

from core.codegen.forward_paths import (
    FORWARD_PATHS_SCHEMA_VERSION,
    DEFAULT_FORWARD_PATHS,
    build_forward_paths_receipt,
)

def test_schema_version():
    assert FORWARD_PATHS_SCHEMA_VERSION == "AbxCodegenForwardPathsSelector.v1"

def test_default_forward_paths_structure():
    assert isinstance(DEFAULT_FORWARD_PATHS, tuple)
    assert len(DEFAULT_FORWARD_PATHS) >= 4
    lanes = [p["lane"] for p in DEFAULT_FORWARD_PATHS]
    assert "v2_1_roadmap_planning" in lanes
    assert "hollersports_schema_generation" in lanes

def test_build_forward_paths_receipt():
    receipt = build_forward_paths_receipt(
        timestamp="2026-07-12T00:00:00",
        source_phase_receipts=["spine-v1"],
        provenance={"source": "test"},
    )
    assert receipt["schema_version"] == FORWARD_PATHS_SCHEMA_VERSION
    assert receipt["receipt_status"] == "FORWARD_PATHS_SELECTOR_READY_ADVISORY_ONLY"
    assert receipt["authority_locks"]["advisory_only"] is True
    assert receipt["valid_for_execution"] is False
    assert "canonical_hash" in receipt
    assert isinstance(receipt["operator_selectable_lanes"], list)
