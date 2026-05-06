from core.brier.scores import BrierScorePacket


def test_deterministic_brier_scoring() -> None:
    assert BrierScorePacket.compute_score(0.7, 1) == BrierScorePacket.compute_score(0.7, 1)
