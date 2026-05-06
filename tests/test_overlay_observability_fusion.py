from core.overlay_observability.fusion import OverlayObservabilityFusionPacket

def test_deterministic_fusion_hashing() -> None:
    h=OverlayObservabilityFusionPacket.compute_hash('c','d','f','b','projection_only')
    assert h==OverlayObservabilityFusionPacket.compute_hash('c','d','f','b','projection_only')
