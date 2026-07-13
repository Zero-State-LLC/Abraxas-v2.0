"""Tests for core/abraxas_spec_stack_codegen_spine_schema_audit.py (HARDENING candidate e119615baf9e2848)"""

from core.abraxas_spec_stack_codegen_spine_schema_audit import (
    SCHEMA_VERSION, AUDIT_ID, DOMAIN, EXPECTED_CONTRACTS, _shadow_binding_validation_ok
)
from core.abraxas_spec_stack_schema_audit_common import contract_summary, gap_finding

def test_constants():
    assert SCHEMA_VERSION == "AbraxasSpecStackCodegenSpineSchemaAudit.v1"
    assert AUDIT_ID == "abraxas_spec_stack_codegen_spine_schema_audit_001"
    assert DOMAIN == "codegen_spine"
    assert len(EXPECTED_CONTRACTS) > 0

def test_contract_summary():
    records = [
        {"contract_id": "c1", "repo_observed": True, "schema_parse_ok": True},
        {"contract_id": "c2", "repo_observed": False, "schema_parse_ok": True},
    ]
    summary = contract_summary(records)
    assert isinstance(summary, dict)
    assert "repo_observed_count" in summary

def test_gap_finding(tmp_path):
    gaps = gap_finding(finding_id="f1", repo_path="nonexistent.py", repo_root=tmp_path)
    assert isinstance(gaps, dict)
    assert "finding_status" in gaps

def test_shadow_binding_validation(tmp_path):
    # minimal test - function handles missing files gracefully
    result = _shadow_binding_validation_ok(tmp_path)
    assert result is False
