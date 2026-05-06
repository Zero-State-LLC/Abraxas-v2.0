import pytest

from core.sandbox.operator_review import OperatorSandboxReviewPacket


def test_operator_review_authority_safety() -> None:
    with pytest.raises(ValueError):
        OperatorSandboxReviewPacket(review_id="r", branch_hash="b", pending_mutations=[], stabilization_state="stable", rollback_available=True, convergence_score=1.0, operator_actions=["execute_production"])
