from core.overlay_observability.operator_review import OperatorOverlayReviewPacket

def test_operator_review_authority_safety()->None:
    p=OperatorOverlayReviewPacket(review_id='r',fusion_hash='f',diagnostic_count=1,critical_diagnostics=0,stability_state='stable',pending_actions=[],status='approved')
    assert p.authority.runtime_mutation_allowed is False
