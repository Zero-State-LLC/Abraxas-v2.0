from core.overlay_risk.saturation import OverlayGovernanceSaturationPacket


def test_saturation_bounded() -> None:
    p = OverlayGovernanceSaturationPacket(saturation_id='1', pending_review_count=0, governance_backlog=0, unresolved_diagnostics=0, overlay_density=0.2, review_saturation_pressure=0.1, saturation_score=0.1, deterministic_saturation_hash=OverlayGovernanceSaturationPacket.compute_hash(0,0,0,0.2,0.1,0.1), status='passed')
    assert 0 <= p.saturation_score <= 1
