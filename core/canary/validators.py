from __future__ import annotations

from core.canary.calibration import CanaryCalibrationPacket
from core.canary.overlays import CanaryOverlayPacket
from core.canary.replay import CanaryReplayPacket
from core.canary.rollback import CanaryRollbackPacket


def validate_canary_overlay(overlay: CanaryOverlayPacket, replay_packet: CanaryReplayPacket, calibration_packet: CanaryCalibrationPacket, rollback_packet: CanaryRollbackPacket, autonomous_promotion_attempted: bool = False) -> dict[str, object]:
    if overlay.overlay_scope not in {"shadow_only", "replay_only", "simulation_only"}:
        return {"status": "failed", "reason": "production scope invalid"}
    if not 0.0 <= overlay.overlay_weight <= 1.0:
        return {"status": "failed", "reason": "invalid overlay weight"}
    if not replay_packet.deterministic_match:
        return {"status": "failed", "reason": "replay mismatch blocks stabilization"}
    if not calibration_packet.rollback_readiness or not rollback_packet.rollback_complete:
        return {"status": "failed", "reason": "rollback readiness required"}
    if autonomous_promotion_attempted:
        return {"status": "failed", "reason": "autonomous promotion attempts fail closed"}
    return {"status": "passed", "reason": "canary overlay validated"}
