from core.oracle.normalization import IntakeNormalizationPacket


def test_normalization_hash_deterministic() -> None:
    assert IntakeNormalizationPacket.compute_hash("a", "b", ["x"]) == IntakeNormalizationPacket.compute_hash("a", "b", ["x"])
