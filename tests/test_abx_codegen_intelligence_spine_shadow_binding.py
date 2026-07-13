"""Tests for core/abx_codegen_intelligence_spine_shadow_binding.py (HARDENING candidate e5f21c77eb471c34)"""

from core.abx_codegen_intelligence_spine_shadow_binding import build_abx_codegen_intelligence_spine_shadow_binding_packet

def test_build_binding_structure():
    packet = build_abx_codegen_intelligence_spine_shadow_binding_packet(".")
    assert packet["schema_version"] == "AbxCodegenIntelligenceSpineShadowBinding.v1"
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert "binding_hash" in packet

def test_binding_status_and_wiring():
    packet = build_abx_codegen_intelligence_spine_shadow_binding_packet(".")
    assert packet["status"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_BINDING_EMITTED"
    assert packet["wiring_mode"] == "SHADOW_ADVISORY_ONLY"
    assert "source_harness_hash" in packet
