from core.canary_promotion.operator_review import OperatorCanaryPromotionReviewPacket

def test_operator_review_authority_safety()->None:
    p=OperatorCanaryPromotionReviewPacket(review_id='r',candidate_hash='c',eligibility_status=True,denial_reasons=[],replay_failures=0,critical_diagnostics=0,pending_actions=[],status='approved')
    assert p.authority.promotion_allowed is False
