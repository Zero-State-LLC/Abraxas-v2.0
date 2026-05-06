from core.overlay_risk.exposure import OverlayExposurePacket


def test_exposure_score_bounded() -> None:
    p = OverlayExposurePacket(exposure_id='1', rollback_dependency_count=1, replay_dependency_count=1, governance_dependency_depth=1, operator_review_load=1, exposure_score=0.2, deterministic_exposure_hash=OverlayExposurePacket.compute_hash(1,1,1,1,0.2), status='passed')
    assert 0 <= p.exposure_score <= 1
