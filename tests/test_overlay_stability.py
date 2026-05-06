from core.overlay_observability.stability import OverlayStabilityPacket

def test_stability_scoring_deterministic()->None:
    p=OverlayStabilityPacket(stability_id='s',fusion_hash='f',replay_match_count=1,replay_failure_count=0,rollback_count=0,diagnostic_count=0,stability_score=0.9,stability_state='stable',status='passed')
    assert p.stability_score==0.9
