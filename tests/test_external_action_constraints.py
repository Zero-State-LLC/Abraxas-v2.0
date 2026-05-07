from core.external_action_proposals.constraints import ProposalConstraintPacket

def test_constraint_hash() -> None:
    h = ProposalConstraintPacket.compute_hash("a", ["execute"])
    assert h
