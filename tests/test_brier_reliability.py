from core.brier.reliability import ReliabilityAggregatePacket


def test_reliability_aggregation_deterministic() -> None:
    h1 = ReliabilityAggregatePacket.compute_hash(["f"], 0.2, 0.8, 0.8)
    h2 = ReliabilityAggregatePacket.compute_hash(["f"], 0.2, 0.8, 0.8)
    assert h1 == h2
