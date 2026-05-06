from core.canary_scheduler.operator_review import OperatorCanaryScheduleReviewPacket

def test_operator_review_authority_safety()->None:
    p=OperatorCanaryScheduleReviewPacket(review_id='r',schedule_hash='s',eligibility_status=True,blocked_reasons=[],replay_failures=0,pending_actions=[],status='approved')
    assert p.authority.promotion_allowed is False
