from core.brier.reliability import ReliabilityAggregatePacket
from core.brier.replay import BrierReplayPacket
from core.brier.validators import validate_brier_ledger


def test_validator_catches_invalid_probabilities() -> None:
    replay = BrierReplayPacket(replay_id="r", ledger_hash="l", deterministic_match=True, replayed_scores=[], mismatched_scores=[])
    reliability = ReliabilityAggregatePacket(reliability_id="x", forecast_hashes=["f"], average_brier=0.1, calibration_average=0.8, reliability_score=0.9, deterministic_reliability_hash=ReliabilityAggregatePacket.compute_hash(["f"], 0.1, 0.8, 0.9))
    result = validate_brier_ledger({"expected_probability": 1.2}, replay, reliability)
    assert result["status"] == "repair_required"
