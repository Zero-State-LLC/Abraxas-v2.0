from core.ingest.controlled_handoff_eligibility import build_controlled_handoff_eligibility


def test_controlled_handoff_eligible_when_oracle_module_present() -> None:
    packet = build_controlled_handoff_eligibility(
        oracle_signal_module_present=True,
        shadow_receipt_valid=True,
    )
    assert packet["controlled_handoff_eligible"] is True
    assert packet["lane"] == "CONTROLLED"
