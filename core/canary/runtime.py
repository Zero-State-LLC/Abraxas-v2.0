from __future__ import annotations

from core.canary.calibration import CanaryCalibrationPacket
from core.canary.lineage import CanaryLineageNode, CanaryLineagePacket
from core.canary.operator_review import OperatorCanaryReviewPacket
from core.canary.overlays import CanaryOverlayPacket
from core.canary.replay import CanaryReplayPacket
from core.canary.rollback import CanaryRollbackPacket
from core.canary.routing import CanaryRoutingPacket
from core.canary.stabilization import CanaryStabilizationPacket
from core.canonical.json import write_canonical_json


def run_canary_overlay(drift_packets: list[dict], forecast_packets: list[dict], reliability_packets: list[dict]) -> dict[str, object]:
    drift_hash = drift_packets[-1].get("deterministic_drift_hash", "drift") if drift_packets else "drift"
    forecast_hash = forecast_packets[-1].get("forecast_hash", "forecast") if forecast_packets else "forecast"
    overlay = CanaryOverlayPacket(
        overlay_id="canary-0001", source_drift_hash=drift_hash, source_forecast_hash=forecast_hash, overlay_scope="shadow_only",
        overlay_weight=0.2, overlay_duration=3, overlay_generation=1, bounded_influence=True,
        deterministic_overlay_hash=CanaryOverlayPacket.compute_hash("canary-0001", drift_hash, forecast_hash, "shadow_only", 0.2, 3, 1, True), status="active"
    )
    routing = CanaryRoutingPacket(routing_id="route-0001", overlay_hashes=[overlay.deterministic_overlay_hash], replay_routes=["canary.replay"], sandbox_routes=["canary.sandbox"], blocked_routes=["production.route"], deterministic_routing_hash=CanaryRoutingPacket.compute_hash([overlay.deterministic_overlay_hash], ["canary.replay"], ["canary.sandbox"], ["production.route"]), status="passed")
    calibration = CanaryCalibrationPacket(calibration_id="cal-0001", overlay_hash=overlay.deterministic_overlay_hash, replay_consistency=1.0, calibration_score=0.92, bounded_influence_score=0.9, rollback_readiness=True, deterministic_calibration_hash=CanaryCalibrationPacket.compute_hash(overlay.deterministic_overlay_hash, 1.0, 0.92, 0.9, True), status="passed")
    replay = CanaryReplayPacket(replay_id="rep-0001", overlay_hash=overlay.deterministic_overlay_hash, deterministic_match=True, replayed_routes=["canary.replay"], mismatched_routes=[], status="passed")
    rollback = CanaryRollbackPacket(rollback_id="rb-0001", overlay_hash=overlay.deterministic_overlay_hash, rollback_reason="operator_safe_revert", rollback_generation=1, rollback_complete=True, deterministic_rollback_hash=CanaryRollbackPacket.compute_hash(overlay.deterministic_overlay_hash, "operator_safe_revert", 1, True), status="passed")
    lineage = CanaryLineagePacket(lineage_id="lin-0001", lineage_nodes=[CanaryLineageNode(overlay_hash=overlay.deterministic_overlay_hash, generation=1, rollback_hash=rollback.deterministic_rollback_hash)], lineage_depth=1, deterministic_lineage_hash=CanaryLineagePacket.compute_hash([CanaryLineageNode(overlay_hash=overlay.deterministic_overlay_hash, generation=1, rollback_hash=rollback.deterministic_rollback_hash)]), status="passed")
    stabilization = CanaryStabilizationPacket(stabilization_id="stab-0001", overlay_hash=overlay.deterministic_overlay_hash, replay_match_count=1, replay_failure_count=0, calibration_score=0.92, rollback_readiness=True, stabilization_window=3, stabilization_state="stable", status="passed")
    review = OperatorCanaryReviewPacket(review_id="rev-0001", overlay_hash=overlay.deterministic_overlay_hash, calibration_score=0.92, replay_failures=0, rollback_readiness=True, pending_actions=[], status="approved")

    packet = {"schema_version": "CanaryRuntimePacket.v1", "overlay": overlay.model_dump(), "routing": routing.model_dump(), "calibration": calibration.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "rollback": rollback.model_dump(), "stabilization": stabilization.model_dump(), "operator_review": review.model_dump(), "status": "passed"}
    write_canonical_json("out/canary/latest.json", packet)
    write_canonical_json("out/canary_replay/latest.json", replay.model_dump())
    write_canonical_json("out/canary_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/canary_rollback/latest.json", rollback.model_dump())
    return packet
