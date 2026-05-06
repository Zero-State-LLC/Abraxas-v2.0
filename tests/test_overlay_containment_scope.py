from core.overlay_containment.scope import OverlayContainmentScopePacket


def test_scope_score_bounds() -> None:
    s = OverlayContainmentScopePacket(scope_id="s1", affected_overlays=["o1"], affected_routes=[], affected_scheduler_windows=[], affected_promotion_candidates=[], containment_scope_depth=1, scope_score=0.4, status="passed")
    assert 0 <= s.scope_score <= 1
