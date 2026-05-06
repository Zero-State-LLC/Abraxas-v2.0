from core.drift.reliability import DriftReliabilityPacket


def test_reliability_aggregation_deterministic() -> None:
    assert DriftReliabilityPacket.compute_hash(["x"], 0.8, 0.2, 0.9) == DriftReliabilityPacket.compute_hash(["x"], 0.8, 0.2, 0.9)
