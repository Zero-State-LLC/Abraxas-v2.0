from core.overlay_observability.validators import validate_overlay_observability
from core.overlay_observability.fusion import OverlayObservabilityFusionPacket
from core.overlay_observability.telemetry import OverlayTelemetryPacket
from core.overlay_observability.replay import OverlayObservabilityReplayPacket
from core.overlay_observability.stability import OverlayStabilityPacket

def _pack():
    h=OverlayObservabilityFusionPacket.compute_hash('c','d','f','b','projection_only')
    return (
        OverlayObservabilityFusionPacket(fusion_id='f',canary_hash='c',drift_hash='d',forecast_hash='f',brier_hash='b',fusion_scope='projection_only',fused_overlay_hash=h,deterministic_fusion_hash=h,status='passed'),
        OverlayTelemetryPacket(telemetry_id='t',overlay_hash=h,replay_match_count=1,replay_failure_count=0,rollback_count=1,blocked_route_count=1,pending_review_count=0,stability_score=0.9,deterministic_telemetry_hash=OverlayTelemetryPacket.compute_hash(h,1,0,1,1,0,0.9),status='passed'),
        OverlayObservabilityReplayPacket(replay_id='r',source_fusion_hash=h,replay_fusion_hash=h,deterministic_match=True,mismatched_packets=[],status='passed'),
        OverlayStabilityPacket(stability_id='s',fusion_hash=h,replay_match_count=1,replay_failure_count=0,rollback_count=1,diagnostic_count=1,stability_score=0.9,stability_state='stable',status='passed')
    )

def test_critical_authority_diagnostic_blocks_validation()->None:
    f,t,r,s=_pack()
    assert validate_overlay_observability(f,t,r,s,critical_authority_diagnostics=1)['status']=='failed'
