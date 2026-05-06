import pytest

from core.forecast.replay import ForecastReplayPacket


def test_replay_mismatch_invalidates_stabilization() -> None:
    with pytest.raises(ValueError):
        ForecastReplayPacket(replay_id="r", forecast_hash="f", deterministic_match=True, replayed_probabilities=[], mismatched_probabilities=["m"])
