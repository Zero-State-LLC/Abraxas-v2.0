from core.canary.replay import CanaryReplayPacket
from core.canary.validators import validate_canary_overlay
from core.canary.overlays import CanaryOverlayPacket
from core.canary.calibration import CanaryCalibrationPacket
from core.canary.rollback import CanaryRollbackPacket


def test_replay_mismatch_blocks_stabilization() -> None:
    ov = CanaryOverlayPacket(overlay_id="x", source_drift_hash="d", source_forecast_hash="f", overlay_scope="shadow_only", overlay_weight=0.2, overlay_duration=1, overlay_generation=1, bounded_influence=True, deterministic_overlay_hash=CanaryOverlayPacket.compute_hash("x","d","f","shadow_only",0.2,1,1,True), status="active")
    rp = CanaryReplayPacket(replay_id="r", overlay_hash=ov.deterministic_overlay_hash, deterministic_match=False, replayed_routes=["a"], mismatched_routes=["a"], status="failed")
    cp = CanaryCalibrationPacket(calibration_id="c", overlay_hash=ov.deterministic_overlay_hash, replay_consistency=0.5, calibration_score=0.5, bounded_influence_score=0.8, rollback_readiness=True, deterministic_calibration_hash=CanaryCalibrationPacket.compute_hash(ov.deterministic_overlay_hash,0.5,0.5,0.8,True), status="passed")
    rb = CanaryRollbackPacket(rollback_id="b", overlay_hash=ov.deterministic_overlay_hash, rollback_reason="x", rollback_generation=1, rollback_complete=True, deterministic_rollback_hash=CanaryRollbackPacket.compute_hash(ov.deterministic_overlay_hash,"x",1,True), status="passed")
    assert validate_canary_overlay(ov,rp,cp,rb)["status"] == "failed"
