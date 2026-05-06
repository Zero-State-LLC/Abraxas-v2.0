import pytest
from core.state.operator_review import OperatorStateReviewPacket


def test_projection_cannot_approve_execution():
    with pytest.raises(ValueError):
        OperatorStateReviewPacket(review_id="r", state_hash="projection:abc", pending_transitions=[], rollback_available=False, stabilization_state="unstable", operator_actions=["approve_execution"])
