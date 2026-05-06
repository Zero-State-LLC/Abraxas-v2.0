import pytest

from core.brier.stabilization import BrierStabilizationPacket


def test_unresolved_mismatches_block_promotion() -> None:
    with pytest.raises(ValueError):
        BrierStabilizationPacket(stabilization_id="s", ledger_hash="l", replay_match_count=1, replay_failure_count=1, reliability_score=0.7, stabilization_window=3, stabilization_state="stable")
