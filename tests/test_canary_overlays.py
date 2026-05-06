from core.canary.overlays import CanaryOverlayPacket


def test_deterministic_canary_hashing() -> None:
    h = CanaryOverlayPacket.compute_hash("id", "d", "f", "shadow_only", 0.2, 2, 1, True)
    assert h == CanaryOverlayPacket.compute_hash("id", "d", "f", "shadow_only", 0.2, 2, 1, True)


def test_overlay_weight_bounds() -> None:
    try:
        CanaryOverlayPacket(overlay_id="x", source_drift_hash="d", source_forecast_hash="f", overlay_scope="shadow_only", overlay_weight=1.2, overlay_duration=1, overlay_generation=1, bounded_influence=True, deterministic_overlay_hash="bad", status="active")
        assert False
    except ValueError:
        assert True
