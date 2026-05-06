from core.forecast.candidates import ForecastCandidatePacket


def test_deterministic_forecast_hashing() -> None:
    assert ForecastCandidatePacket.compute_hash("a", "b", "sandbox", "c") == ForecastCandidatePacket.compute_hash("a", "b", "sandbox", "c")
