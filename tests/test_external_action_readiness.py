import pytest
from core.external_action_proposals.readiness import ProposalReadinessPacket

def test_readiness_bounds() -> None:
    with pytest.raises(ValueError):
        ProposalReadinessPacket(proposal_hash="a", readiness_posture=1.2, deterministic_readiness_hash="x", status="failed")
