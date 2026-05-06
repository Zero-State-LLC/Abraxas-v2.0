from core.canary.overlays import CanaryOverlayPacket
from core.canary.calibration import CanaryCalibrationPacket
from core.canary.replay import CanaryReplayPacket
from core.canary.rollback import CanaryRollbackPacket
from core.canary.validators import validate_canary_overlay


def _pack(scope: str="shadow_only"):
    ov = CanaryOverlayPacket(overlay_id="x", source_drift_hash="d", source_forecast_hash="f", overlay_scope=scope, overlay_weight=0.2, overlay_duration=1, overlay_generation=1, bounded_influence=True, deterministic_overlay_hash=CanaryOverlayPacket.compute_hash("x","d","f",scope,0.2,1,1,True), status="active")
    cp = CanaryCalibrationPacket(calibration_id="c", overlay_hash=ov.deterministic_overlay_hash, replay_consistency=1, calibration_score=0.9, bounded_influence_score=0.9, rollback_readiness=True, deterministic_calibration_hash=CanaryCalibrationPacket.compute_hash(ov.deterministic_overlay_hash,1,0.9,0.9,True), status="passed")
    rp = CanaryReplayPacket(replay_id="r", overlay_hash=ov.deterministic_overlay_hash, deterministic_match=True, replayed_routes=["r"], mismatched_routes=[], status="passed")
    rb = CanaryRollbackPacket(rollback_id="b", overlay_hash=ov.deterministic_overlay_hash, rollback_reason="x", rollback_generation=1, rollback_complete=True, deterministic_rollback_hash=CanaryRollbackPacket.compute_hash(ov.deterministic_overlay_hash,"x",1,True), status="passed")
    return ov, rp, cp, rb


def test_validator_catches_autonomous_promotion_attempt() -> None:
    ov,rp,cp,rb = _pack()
    assert validate_canary_overlay(ov,rp,cp,rb,autonomous_promotion_attempted=True)["status"] == "failed"


def test_validator_catches_production_scope() -> None:
    ov,rp,cp,rb = _pack("simulation_only")
    assert validate_canary_overlay(ov,rp,cp,rb)["status"] == "passed"
