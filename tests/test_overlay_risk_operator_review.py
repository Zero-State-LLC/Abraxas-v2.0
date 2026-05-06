from core.overlay_risk.operator_review import OperatorOverlayRiskReviewPacket


def test_operator_review_observation_only() -> None:
    p = OperatorOverlayRiskReviewPacket(review_id='1', aggregate_risk_score=0.2, critical_diagnostics=0, pending_actions=[], status='approved')
    assert p.status == 'approved'
