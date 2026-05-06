from core.drift.proposals import WeightDriftProposalPacket


def test_deterministic_drift_proposal_hashing() -> None:
    assert WeightDriftProposalPacket.compute_hash("a", "b", 0.1, 0.6) == WeightDriftProposalPacket.compute_hash("a", "b", 0.1, 0.6)
