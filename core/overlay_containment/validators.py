from __future__ import annotations
from core.overlay_containment.policies import OverlayContainmentPolicyPacket
from core.overlay_containment.recommendations import OverlayContainmentRecommendationPacket
from core.overlay_containment.replay import OverlayContainmentReplayPacket


def validate_overlay_containment(
    policy: OverlayContainmentPolicyPacket,
    recommendations: list[OverlayContainmentRecommendationPacket],
    replay: OverlayContainmentReplayPacket,
    diagnostics: list[dict],
    lineage_cycles_exist: bool,
) -> dict[str, object]:
    if "production" in policy.policy_scope:
        return {"status": "failed", "reason": "production scope"}
    if not (0 <= policy.max_aggregate_risk <= 1 and 0 <= policy.max_propagation_depth <= 1 and 0 <= policy.max_coupling_score <= 1):
        return {"status": "failed", "reason": "thresholds"}
    if replay.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch"}
    if lineage_cycles_exist:
        return {"status": "failed", "reason": "lineage cycle"}
    if any(d.get("severity") == "critical" for d in diagnostics):
        return {"status": "failed", "reason": "critical diagnostics"}
    for rec in recommendations:
        if "enforce" in rec.recommendation_reason.lower():
            return {"status": "failed", "reason": "enforcement recommendation"}
        rec.authority.assert_locked()
    policy.authority.assert_locked()
    return {"status": "passed", "reason": "overlay containment validated"}
