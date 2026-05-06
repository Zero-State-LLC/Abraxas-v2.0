from core.overlay_governance.operator_review import OperatorOverlayGovernanceReviewPacket


def test_operator_review_authority_safety() -> None:
    p = OperatorOverlayGovernanceReviewPacket(review_id="1", ledger_hash="h", continuity_score=1.0, critical_diagnostics=0, missing_event_types=[], pending_actions=[], status="approved")
    assert p.authority.runtime_mutation_allowed is False
