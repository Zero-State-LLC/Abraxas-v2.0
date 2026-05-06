import pytest

from core.drift.operator_review import OperatorDriftReviewPacket


def test_operator_review_authority_safety() -> None:
    with pytest.raises(ValueError):
        OperatorDriftReviewPacket(review_id="r", overlay_hash="o", calibration_score=0.9, drift_confidence=0.9, replay_failures=0, pending_actions=["autonomous_weight_mutation"])
