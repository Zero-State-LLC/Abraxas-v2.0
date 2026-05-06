from __future__ import annotations

from core.drift.calibration import DriftCalibrationPacket
from core.drift.replay import DriftReplayPacket


def validate_weight_drift(overlay: dict, replay_packet: DriftReplayPacket, calibration_packet: DriftCalibrationPacket) -> dict[str, object]:
    production_attempt = "production_mutation" in overlay.get("pending_actions", [])
    gates = [
        {"gate": "drift_replay_gate", "passed": replay_packet.deterministic_match, "reason": "replay mismatch invalidates stabilization"},
        {"gate": "weight_overlay_gate", "passed": 0 <= overlay.get("overlay_weight", -1) <= 1, "reason": "invalid overlay weights fail closed"},
        {"gate": "drift_calibration_gate", "passed": 0 <= calibration_packet.calibration_score <= 1, "reason": "calibration valid"},
        {"gate": "drift_stabilization_gate", "passed": not replay_packet.mismatched_overlays, "reason": "unresolved mismatches block stable state"},
        {"gate": "drift_operator_review_gate", "passed": not production_attempt, "reason": "production mutation attempts fail closed"},
    ]
    return {"status": "doctrine_compliant" if all(g["passed"] for g in gates) else "repair_required", "gate_results": gates}
