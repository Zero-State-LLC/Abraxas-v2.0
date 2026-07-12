"""Tests for core/runtime_integration_gate_operator_attestation_intake_gate.py (HARDENING candidate for new cycle)"""

from core.runtime_integration_gate_operator_attestation_intake_gate import (
    SCHEMA_VERSION,
    GATE_ID,
    ALLOWED_DECISIONS,
    NOT_COMPUTABLE,
)


def test_constants():
    assert SCHEMA_VERSION == "RuntimeIntegrationGateOperatorAttestationIntakeGate.v1"
    assert GATE_ID == "runtime_integration_gate_operator_attestation_intake_gate_001"
    assert "MAINTAIN_HOLD" in ALLOWED_DECISIONS
    assert NOT_COMPUTABLE == "NOT_COMPUTABLE"


def test_allowed_decisions():
    assert len(ALLOWED_DECISIONS) == 3
