"""Tests for core/abraxas_spec_stack_belief_graph_schema_audit.py (HARDENING candidate)"""

from core.abraxas_spec_stack_belief_graph_schema_audit import (
    build_abraxas_spec_stack_belief_graph_schema_audit,
    AUDIT_ID,
    DOMAIN,
    SCHEMA_VERSION,
    STATUS,
)


def test_build_audit_returns_valid_packet():
    packet = build_abraxas_spec_stack_belief_graph_schema_audit()
    assert isinstance(packet, dict)
    assert packet.get("schema_version") == SCHEMA_VERSION
    assert packet.get("audit_id") == AUDIT_ID
    assert packet.get("domain") == DOMAIN
    assert packet.get("status") == STATUS
    assert "contract_records" in packet
    assert "findings" in packet
    assert "authority_locks" in packet


def test_audit_has_expected_keys():
    packet = build_abraxas_spec_stack_belief_graph_schema_audit()
    for key in ["contract_summary", "recommended_next_lane", "authority_locks"]:
        assert key in packet
