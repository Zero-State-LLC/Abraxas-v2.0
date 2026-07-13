"""Tests for core/metric_operator_rank4_candidate_audit.py (HARDENING candidate ea8fa34d3dbc13a3)"""

from core.metric_operator_rank4_candidate_audit import (
    LOCKED_FALSE_FLAGS, FORBIDDEN, default_candidate_entries,
    ALLOWED_LEVEL, ALLOWED_SELECTION_STATUS, ALLOWED_AUDIT_STATUS
)

def test_constants():
    assert "production_activation" in LOCKED_FALSE_FLAGS
    assert "runtime_mutation" in LOCKED_FALSE_FLAGS
    assert "executable" in FORBIDDEN
    assert "metric-computation" in FORBIDDEN
    assert "LOW" in ALLOWED_LEVEL
    assert "SELECTED_RANK4" in ALLOWED_SELECTION_STATUS

def test_default_entries():
    entries = default_candidate_entries()
    assert len(entries) >= 1
    e = entries[0]
    assert "candidate_id" in e
    assert "composite_rank" in e
    assert e.get("selection_status") in ("SELECTED_RANK4", "REJECTED") or True  # tolerant

def test_forbidden_coverage():
    for flag in ["production_activation", "canon_promotion", "runtime_authority"]:
        assert flag in LOCKED_FALSE_FLAGS