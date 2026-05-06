import pytest

from core.forecast.operator_review import OperatorForecastReviewPacket


def test_operator_review_authority_safety() -> None:
    with pytest.raises(ValueError):
        OperatorForecastReviewPacket(review_id="r", forecast_hash="f", stabilization_state="stabilizing", calibration_score=0.8, unresolved_bindings=1, pending_actions=["autonomous_promotion"])
