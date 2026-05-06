from core.overlay_observability.validators import validate_overlay_observability
from core.overlay_observability.fusion import OverlayObservabilityFusionPacket
from core.overlay_observability.telemetry import OverlayTelemetryPacket
from core.overlay_observability.replay import OverlayObservabilityReplayPacket
from core.overlay_observability.stability import OverlayStabilityPacket

def test_replay_mismatch_invalidates_stability()->None:
    fhash=OverlayObservabilityFusionPacket.compute_hash('c','d','f','b','projection_only')
    fp=OverlayObservabilityFusionPacket(fusion_id='f',canary_hash='c',drift_hash='d',forecast_hash='f',brier_hash='b',fusion_scope='projection_only',fused_overlay_hash=fhash,deterministic_fusion_hash=fhash,status='passed')
    tp=OverlayTelemetryPacket(telemetry_id='t',overlay_hash=fhash,replay_match_count=0,replay_failure_count=1,rollback_count=0,blocked_route_count=0,pending_review_count=0,stability_score=0.2,deterministic_telemetry_hash=OverlayTelemetryPacket.compute_hash(fhash,0,1,0,0,0,0.2),status='passed')
    rp=OverlayObservabilityReplayPacket(replay_id='r',source_fusion_hash=fhash,replay_fusion_hash='x',deterministic_match=False,mismatched_packets=['fusion'],status='failed')
    sp=OverlayStabilityPacket(stability_id='s',fusion_hash=fhash,replay_match_count=0,replay_failure_count=1,rollback_count=0,diagnostic_count=1,stability_score=0.2,stability_state='unstable',status='failed')
    assert validate_overlay_observability(fp,tp,rp,sp)['status']=='failed'
