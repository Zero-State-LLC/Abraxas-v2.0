"""Tests for core/governance/signal_forager_brier_hook.py (GOVERNANCE candidate c851e1d4b8a255fa)"""

from core.governance.signal_forager_brier_hook import (
    emit_signal_forager_brier_hook,
    build_signal_forager_brier_contract,
    build_signal_forager_live_runtime_contract,
)

def test_emit_hook():
    hook = emit_signal_forager_brier_hook(
        claim_id="test_claim",
        forecast_probability=0.5,
    )
    assert isinstance(hook, dict)
    assert "claim_id" in hook or "provenance" in hook

def test_build_contract():
    contract = build_signal_forager_brier_contract()
    assert isinstance(contract, dict)
    assert contract.get("contract_id") == "v2_governance_signal_forager_brier_hook_001"
    assert contract.get("resolution_allowed") is False
    assert contract.get("promotion_authorized") is False

def test_live_runtime_contract():
    contract = build_signal_forager_live_runtime_contract()
    assert isinstance(contract, dict)
    assert "telemetry_hooks" in contract
