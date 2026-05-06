import pytest

from core.oracle.operator_review import OperatorIntakeReviewPacket


def test_operator_review_authority_safety() -> None:
    with pytest.raises(ValueError):
        OperatorIntakeReviewPacket(review_id="r", intake_hash="h", pending_conflicts=[], stabilization_state="stable", replay_status="matched", operator_actions=["execute_production"])
