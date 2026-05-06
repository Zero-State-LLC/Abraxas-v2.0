from core.overlay_containment.operator_review import OperatorOverlayContainmentReviewPacket


def test_operator_review_packet() -> None:
    p = OperatorOverlayContainmentReviewPacket(review_id="r", pending_reviews=1, critical_diagnostics=0, recommendation_count=2, pending_actions=["review"], status="pending")
    assert p.status == "pending"
