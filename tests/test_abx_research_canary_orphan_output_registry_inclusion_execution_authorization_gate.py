"""Tests for core/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate.py (HARDENING candidate d274c15bf37fbd15)"""

from core.abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate import (
    build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate,
    render_markdown,
)

def test_build_gate_structure():
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(".")
    assert packet["schema_version"] == "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionAuthorizationGate.v1"
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["authorization_gate_only"] is True
    assert packet["operator_authorization_required"] is True
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["registry_mutation_performed"] is False
    assert "authorization_gate_hash" in packet

def test_render_markdown():
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(".")
    lines = render_markdown(packet)
    assert any("status" in line for line in lines)
    assert any("recommended_next_lane" in line for line in lines)

def test_status_logic():
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(".")
    assert packet["status"] in (
        "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR",
        "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_BLOCKED",
    )
