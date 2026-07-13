"""Tests for core/codegen/loop805_token_optimizer.py (HARDENING candidate aebb106eb09750d9)"""

from core.codegen.loop805_token_optimizer import build_loop805_token_optimizer_stub

def test_build_loop805_token_optimizer_stub():
    decision = {
        "token_telemetry": {"estimated_total_tokens": 500000}
    }
    res = build_loop805_token_optimizer_stub(
        timestamp="2026-07-12T00:00:00Z",
        route_decisions=[decision],
        optimizer_names=["token_reduction"],
    )
    assert isinstance(res, dict)
    assert res.get("stub_status") == "TOKEN_OPTIMIZER_STUB_READY_NOT_ENFORCED"
    assert "observed_average_tokens" in res
    assert res.get("enforcement", {}).get("enabled") is False
