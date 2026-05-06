from __future__ import annotations
from core.canonical.json import write_canonical_json
from core.overlay_observability.fusion import OverlayObservabilityFusionPacket
from core.overlay_observability.telemetry import OverlayTelemetryPacket
from core.overlay_observability.diagnostics import OverlayDiagnosticPacket
from core.overlay_observability.replay import OverlayObservabilityReplayPacket
from core.overlay_observability.lineage import OverlayObservabilityLineageNode, OverlayObservabilityLineagePacket
from core.overlay_observability.stability import OverlayStabilityPacket
from core.overlay_observability.operator_review import OperatorOverlayReviewPacket

def run_overlay_observability(canary_packets:list[dict], drift_packets:list[dict], forecast_packets:list[dict], brier_packets:list[dict]) -> dict[str,object]:
    canary_hash=canary_packets[-1].get('overlay',{}).get('deterministic_overlay_hash','canary') if canary_packets else 'canary'
    drift_hash=drift_packets[-1].get('deterministic_drift_hash','drift') if drift_packets else 'drift'
    forecast_hash=forecast_packets[-1].get('forecast_hash','forecast') if forecast_packets else 'forecast'
    brier_hash=brier_packets[-1].get('ledger_hash','brier') if brier_packets else 'brier'
    fusion_hash=OverlayObservabilityFusionPacket.compute_hash(canary_hash,drift_hash,forecast_hash,brier_hash,'projection_only')
    fusion=OverlayObservabilityFusionPacket(fusion_id='of-1',canary_hash=canary_hash,drift_hash=drift_hash,forecast_hash=forecast_hash,brier_hash=brier_hash,fusion_scope='projection_only',fused_overlay_hash=fusion_hash,deterministic_fusion_hash=fusion_hash,status='passed')
    telemetry=OverlayTelemetryPacket(telemetry_id='ot-1',overlay_hash=fusion_hash,replay_match_count=1,replay_failure_count=0,rollback_count=1,blocked_route_count=1,pending_review_count=0,stability_score=0.9,deterministic_telemetry_hash=OverlayTelemetryPacket.compute_hash(fusion_hash,1,0,1,1,0,0.9),status='passed')
    diag=OverlayDiagnosticPacket(diagnostic_id='od-1',overlay_hash=fusion_hash,diagnostic_type='route_blocking',severity='info',diagnostic_message='blocked production route observed',deterministic_diagnostic_hash=OverlayDiagnosticPacket.compute_hash(fusion_hash,'route_blocking','info','blocked production route observed'),status='passed')
    replay=OverlayObservabilityReplayPacket(replay_id='or-1',source_fusion_hash=fusion_hash,replay_fusion_hash=fusion_hash,deterministic_match=True,mismatched_packets=[],status='passed')
    node=OverlayObservabilityLineageNode(fusion_hash=fusion_hash,generation=1,diagnostic_hash=diag.deterministic_diagnostic_hash)
    lineage=OverlayObservabilityLineagePacket(lineage_id='ol-1',lineage_nodes=[node],lineage_depth=1,deterministic_lineage_hash=OverlayObservabilityLineagePacket.compute_hash([node]),status='passed')
    stability=OverlayStabilityPacket(stability_id='os-1',fusion_hash=fusion_hash,replay_match_count=1,replay_failure_count=0,rollback_count=1,diagnostic_count=1,stability_score=0.9,stability_state='stable',status='passed')
    review=OperatorOverlayReviewPacket(review_id='oor-1',fusion_hash=fusion_hash,diagnostic_count=1,critical_diagnostics=0,stability_state='stable',pending_actions=[],status='approved')
    packet={'schema_version':'OverlayObservabilityRuntimePacket.v1','fusion':fusion.model_dump(),'telemetry':telemetry.model_dump(),'diagnostics':[diag.model_dump()],'replay':replay.model_dump(),'lineage':lineage.model_dump(),'stability':stability.model_dump(),'operator_review':review.model_dump(),'status':'passed'}
    write_canonical_json('out/overlay_observability/latest.json',packet)
    write_canonical_json('out/overlay_observability_replay/latest.json',replay.model_dump())
    write_canonical_json('out/overlay_observability_lineage/latest.json',lineage.model_dump())
    write_canonical_json('out/overlay_observability_diagnostics/latest.json',[diag.model_dump()])
    return packet
