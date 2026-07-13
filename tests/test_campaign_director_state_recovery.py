"""Tests for Campaign Director state recovery (Phase 1).

Deterministic replay: same artifacts -> same recovery output and hashes.
"""

from pathlib import Path
import pytest

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.models import CampaignRecoveryResult


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_recovery_produces_valid_structure():
    result = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    assert isinstance(result, CampaignRecoveryResult)
    assert result.campaign_id == "ABRAXAS_STRUCTURAL_ENGINEERING_CAMPAIGN_001"
    assert result.latest_sealed_batch.startswith("structural_batch_")
    assert isinstance(result.next_cycles, list) and len(result.next_cycles) >= 1
    assert result.protected_state is not None
    assert result.recovery_status in ("VALID", "PARTIAL_RESUMABLE", "NOT_COMPUTABLE")


def test_protected_state_contract():
    result = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    ps = result.protected_state
    assert ps.policy_reference_count == 3
    # In current artifacts should be all false
    assert not ps.authority_expanded
    assert not ps.canon_mutated


def test_deterministic_replay():
    """Run twice, hashes and key fields identical."""
    r1 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    r2 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    assert r1.recovery_hash == r2.recovery_hash
    assert r1.latest_sealed_batch == r2.latest_sealed_batch
    assert r1.latest_completed_cycle == r2.latest_completed_cycle
    assert r1.next_batch == r2.next_batch
    assert r1.continuous_execution_eligible == r2.continuous_execution_eligible


def test_recovery_includes_oracle_reference():
    result = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    # May be None if no fresh oracle at test time, but field present
    assert hasattr(result, "oracle_primary_id")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])