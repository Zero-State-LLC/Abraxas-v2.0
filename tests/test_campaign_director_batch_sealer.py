"""Batch sealer tests (Phase 1: validation only, no seal logic yet)."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_seal_evidence_requirements_observed():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    # In real, would require terminal, receipt, ledgers, tests, replay, etc.
    # For Phase 1 just confirm we can reach latest with evidence markers
    assert rec.latest_sealed_batch
    # Would check for batch_terminal_decision etc in full impl
    assert rec.recovery_status in ("VALID", "PARTIAL_RESUMABLE")
