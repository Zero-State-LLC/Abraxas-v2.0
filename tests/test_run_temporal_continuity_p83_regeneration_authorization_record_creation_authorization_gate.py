"""Tests for temporal continuity P83 regeneration authorization record creation authorization gate (candidate ff3d654f5a8aca6f)"""

from core.temporal_continuity_p83_regeneration_authorization_gate import (
    _GATE_STATUSES,
    _ELIGIBILITY_REASON_ORDER,
    _DENIAL_REASON_ORDER,
)

def test_gate_statuses():
    assert "P83_REGENERATION_AUTHORIZATION_ELIGIBLE" in _GATE_STATUSES
    assert "P83_REGENERATION_AUTHORIZATION_DENIED" in _GATE_STATUSES
    assert "NOT_COMPUTABLE" in _GATE_STATUSES

def test_eligibility_reasons_ordered():
    assert "P88_EXECUTION_PLAN_READY" in _ELIGIBILITY_REASON_ORDER
    assert len(_ELIGIBILITY_REASON_ORDER) > 0

def test_denial_reasons():
    assert "P88_SOURCE_MISSING" in _DENIAL_REASON_ORDER
    assert len(_DENIAL_REASON_ORDER) > 0
