"""Tests for core/codegen/loop805_observability.py (HARDENING candidate abf44a5577af86d0)"""

from core.codegen.loop805_observability import build_spine_route_decision

def test_build_spine_route_decision():
    res = build_spine_route_decision(
        timestamp="2026-07-12T00:00:00Z",
        tool_name="/spine/query",
        intent="test-intent",
        evidence_paths=["out/repo_intel/repo_intel_receipt.v1.json"],
        estimated_input_tokens=1000,
        estimated_output_tokens=500,
    )
    assert isinstance(res, dict)
    assert res.get("tool_name") == "/spine/query"
    assert "token_telemetry" in res
    assert "authority_locks" in res
    assert res.get("valid_for_execution") is False
