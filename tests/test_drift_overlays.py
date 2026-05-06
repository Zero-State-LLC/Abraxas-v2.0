import pytest

from core.drift.overlays import WeightOverlayPacket


def test_overlay_weight_bounds() -> None:
    with pytest.raises(ValueError):
        WeightOverlayPacket(overlay_id="o", proposal_hash="p", overlay_generation=1, overlay_weight=1.2, deterministic_overlay_hash="x")
