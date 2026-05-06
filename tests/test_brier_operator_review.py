import pytest

from core.brier.operator_review import OperatorBrierReviewPacket


def test_operator_review_authority_safety() -> None:
    with pytest.raises(ValueError):
        OperatorBrierReviewPacket(review_id="r", ledger_hash="l", reliability_score=0.7, replay_failures=0, pending_actions=["autonomous_reliability_mutation"])
