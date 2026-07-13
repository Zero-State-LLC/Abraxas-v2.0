"""Tests for core/abraxas_spec_stack_situation_runtime_schema_audit.py (HARDENING candidate eca455280f92f19d)"""

from core.abraxas_spec_stack_situation_runtime_schema_audit import (
    build_abraxas_spec_stack_situation_runtime_schema_audit,
    SCHEMA_VERSION, AUDIT_ID, DOMAIN, STATUS, EXPECTED_CONTRACTS
)

def test_build_situation_runtime_schema_audit_structure():
    audit = build_abraxas_spec_stack_situation_runtime_schema_audit(".")
    assert audit["schema_version"] == SCHEMA_VERSION
    assert audit["audit_id"] == AUDIT_ID
    assert audit["domain"] == DOMAIN
    assert audit["status"] == STATUS
    assert "contract_records" in audit
    assert "findings" in audit
    assert "governance_envelope" in audit or "authority_locks" in str(audit)

def test_expected_contracts():
    assert len(EXPECTED_CONTRACTS) >= 2
    assert any("operator_narrative_report" in str(c) for c in EXPECTED_CONTRACTS)

def test_governance_and_shadow_gap():
    audit = build_abraxas_spec_stack_situation_runtime_schema_audit(".")
    # Basic presence checks for key fields
    assert "integration_point_id" in audit
    assert audit.get("integration_point_id") == "SITUATION_RUNTIME_ENGINE_001"