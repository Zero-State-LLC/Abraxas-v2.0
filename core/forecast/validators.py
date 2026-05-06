from __future__ import annotations

from core.forecast.calibration import ForecastCalibrationPacket
from core.forecast.replay import ForecastReplayPacket


def validate_forecast_candidate(forecast: dict, replay_packet: ForecastReplayPacket, calibration_packet: ForecastCalibrationPacket) -> dict[str, object]:
    unresolved = int(forecast.get("unresolved_bindings", 0))
    autonomous = "autonomous_promotion" in forecast.get("pending_actions", [])
    gates = [
        {"gate": "forecast_replay_gate", "passed": replay_packet.deterministic_match, "reason": "replay mismatch invalidates stabilization"},
        {"gate": "forecast_calibration_gate", "passed": calibration_packet.calibration_score >= 0.6, "reason": "calibration below threshold blocks stabilization"},
        {"gate": "forecast_outcome_binding_gate", "passed": unresolved == 0, "reason": "unresolved outcome bindings block promotion"},
        {"gate": "forecast_operator_review_gate", "passed": not autonomous, "reason": "autonomous promotion attempted"},
    ]
    return {"status": "doctrine_compliant" if all(g["passed"] for g in gates) else "repair_required", "gate_results": gates}
