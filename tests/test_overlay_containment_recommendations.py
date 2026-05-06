from core.overlay_containment.recommendations import OverlayContainmentRecommendationPacket


def test_recommendation_hash() -> None:
    h = OverlayContainmentRecommendationPacket.compute_hash("ph", "oh", "hold_observation", "Advisory only.", "info")
    rec = OverlayContainmentRecommendationPacket(recommendation_id="r1", policy_hash="ph", overlay_hash="oh", recommendation_type="hold_observation", recommendation_reason="Advisory only.", advisory_severity="info", deterministic_recommendation_hash=h, status="passed")
    assert rec.authority.runtime_mutation_allowed is False
