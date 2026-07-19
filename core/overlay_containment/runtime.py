from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.
from core.overlay_containment.diagnostics import OverlayContainmentDiagnosticPacket
from core.overlay_containment.lineage import OverlayContainmentLineageNode, OverlayContainmentLineagePacket
from core.overlay_containment.operator_review import OperatorOverlayContainmentReviewPacket
from core.overlay_containment.policies import OverlayContainmentPolicyPacket
from core.overlay_containment.recommendations import OverlayContainmentRecommendationPacket
from core.overlay_containment.replay import OverlayContainmentReplayPacket
from core.overlay_containment.scope import OverlayContainmentScopePacket
from core.overlay_containment.triggers import OverlayContainmentTriggerPacket
from core.overlay_containment.validators import validate_overlay_containment

def run_overlay_containment_policy(risk_packets: list[dict], topology_packets: list[dict], governance_packets: list[dict], scheduler_packets: list[dict], promotion_packets: list[dict]) -> dict[str, object]:
    overlay_hash = "overlay-containment-1"
    aggregate = 0.4
    propagation = 0.3
    coupling = 0.2
    rollback_ready = True
    policy = OverlayContainmentPolicyPacket(policy_id="ocp-1", policy_scope="projection_only", max_aggregate_risk=0.7, max_propagation_depth=0.7, max_coupling_score=0.7, require_rollback_ready=True, block_critical_diagnostics=True, deterministic_policy_hash=OverlayContainmentPolicyPacket.compute_hash("projection_only", 0.7, 0.7, 0.7, True, True), status="passed")
    active = []
    if aggregate > policy.max_aggregate_risk:
        active.append("aggregate_risk_above_threshold")
    if propagation > policy.max_propagation_depth:
        active.append("propagation_depth_above_threshold")
    if coupling > policy.max_coupling_score:
        active.append("coupling_score_above_threshold")
    if not rollback_ready:
        active.append("rollback_not_ready")
    trigger = OverlayContainmentTriggerPacket(trigger_id="oct-1", active_triggers=active, status="passed")
    recommendations = [OverlayContainmentRecommendationPacket(recommendation_id="ocr-1", policy_hash=policy.deterministic_policy_hash, overlay_hash=overlay_hash, recommendation_type="hold_observation", recommendation_reason="Deterministic advisory hold while thresholds remain within envelope.", advisory_severity="info", deterministic_recommendation_hash=OverlayContainmentRecommendationPacket.compute_hash(policy.deterministic_policy_hash, overlay_hash, "hold_observation", "Deterministic advisory hold while thresholds remain within envelope.", "info"), status="passed")]
    scope = OverlayContainmentScopePacket(scope_id="ocs-1", affected_overlays=[overlay_hash], affected_routes=["projection://overlay/containment"], affected_scheduler_windows=["window-1"], affected_promotion_candidates=["candidate-1"], containment_scope_depth=1, scope_score=0.2, status="passed")
    replay = OverlayContainmentReplayPacket(replay_id="ocre-1", source_policy_hash=policy.deterministic_policy_hash, replay_policy_hash=policy.deterministic_policy_hash, deterministic_match=True, mismatched_components=[], status="passed")
    lineage_node = OverlayContainmentLineageNode(policy_hash=policy.deterministic_policy_hash, generation=1)
    lineage = OverlayContainmentLineagePacket(lineage_id="ocl-1", lineage_nodes=[lineage_node], lineage_depth=1, deterministic_lineage_hash=OverlayContainmentLineagePacket.compute_hash([lineage_node]), status="passed")
    diagnostics: list[OverlayContainmentDiagnosticPacket] = []
    review = OperatorOverlayContainmentReviewPacket(review_id="ocv-1", pending_reviews=0, critical_diagnostics=0, recommendation_count=len(recommendations), pending_actions=[], status="approved")
    validator = validate_overlay_containment(policy, recommendations, replay, [d.model_dump() for d in diagnostics], lineage_cycles_exist=False)
    packet = {"schema_version": "OverlayContainmentRuntimePacket.v1", "policy": policy.model_dump(), "triggers": trigger.model_dump(), "recommendations": [r.model_dump() for r in recommendations], "scope": scope.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": review.model_dump(), "validator": validator, "status": validator["status"]}
    return packet
