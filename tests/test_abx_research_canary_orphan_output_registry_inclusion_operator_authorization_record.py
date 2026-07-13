"""Tests for core/abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record.py (HARDENING candidate d6ccde561f88f7c4)"""

from core.abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record import build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record

def test_build_record_structure():
    packet = build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(".")
    assert packet["schema_version"] == "AbxResearchCanaryOrphanOutputRegistryInclusionOperatorAuthorizationRecord.v1"
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert "status" in packet
    assert packet["authorization_scope"] == "ORPHAN_OUTPUT_REGISTRY_INCLUSION_BRANCH_A4B_ONLY"

def test_status_logic():
    packet = build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(".")
    assert packet["status"] in (
        "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_EMITTED",
        "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_BLOCKED",
    )
