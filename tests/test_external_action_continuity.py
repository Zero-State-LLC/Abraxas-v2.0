from core.external_action_proposals.continuity import ExternalActionProposalContinuityPacket

def test_continuity_hash() -> None:
    assert ExternalActionProposalContinuityPacket.compute_hash("a", [], True)
