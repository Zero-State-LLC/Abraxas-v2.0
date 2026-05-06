from core.overlay_containment.policies import OverlayContainmentPolicyPacket


def test_policy_hash_and_bounds() -> None:
    h = OverlayContainmentPolicyPacket.compute_hash("projection_only", 0.7, 0.6, 0.5, True, True)
    p = OverlayContainmentPolicyPacket(policy_id="p1", policy_scope="projection_only", max_aggregate_risk=0.7, max_propagation_depth=0.6, max_coupling_score=0.5, require_rollback_ready=True, block_critical_diagnostics=True, deterministic_policy_hash=h, status="passed")
    assert p.policy_scope == "projection_only"
