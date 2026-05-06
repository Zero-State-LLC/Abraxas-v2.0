from core.canary.operator_review import OperatorCanaryReviewPacket


def test_operator_authority_safety() -> None:
    p = OperatorCanaryReviewPacket(review_id="r", overlay_hash="o", calibration_score=0.8, replay_failures=0, rollback_readiness=True, pending_actions=[], status="approved")
    assert p.authority.promotion_allowed is False
