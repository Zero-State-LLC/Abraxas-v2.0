from core.overlay_containment.policies import OverlayContainmentPolicyPacket
from core.overlay_containment.recommendations import OverlayContainmentRecommendationPacket
from core.overlay_containment.replay import OverlayContainmentReplayPacket
from core.overlay_containment.validators import validate_overlay_containment


def test_validator_pass() -> None:
    p = OverlayContainmentPolicyPacket(policy_id="p", policy_scope="projection_only", max_aggregate_risk=0.7, max_propagation_depth=0.7, max_coupling_score=0.7, require_rollback_ready=True, block_critical_diagnostics=True, deterministic_policy_hash=OverlayContainmentPolicyPacket.compute_hash("projection_only", 0.7, 0.7, 0.7, True, True), status="passed")
    r = OverlayContainmentRecommendationPacket(recommendation_id="r", policy_hash=p.deterministic_policy_hash, overlay_hash="o", recommendation_type="hold_observation", recommendation_reason="advisory", advisory_severity="info", deterministic_recommendation_hash=OverlayContainmentRecommendationPacket.compute_hash(p.deterministic_policy_hash, "o", "hold_observation", "advisory", "info"), status="passed")
    replay = OverlayContainmentReplayPacket(replay_id="re", source_policy_hash=p.deterministic_policy_hash, replay_policy_hash=p.deterministic_policy_hash, deterministic_match=True, mismatched_components=[], status="passed")
    v = validate_overlay_containment(p, [r], replay, [], False)
    assert v["status"] == "passed"
