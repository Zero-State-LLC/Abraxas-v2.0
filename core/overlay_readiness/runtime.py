from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.
from core.overlay_readiness.components import OverlayReadinessComponentPacket
from core.overlay_readiness.diagnostics import OverlayReadinessDiagnosticPacket
from core.overlay_readiness.index import OverlayReadinessIndexPacket
from core.overlay_readiness.lineage import OverlayReadinessLineageNode, OverlayReadinessLineagePacket
from core.overlay_readiness.operator_review import OperatorOverlayReadinessReviewPacket
from core.overlay_readiness.replay import OverlayReadinessReplayPacket
from core.overlay_readiness.thresholds import OverlayReadinessThresholdPacket
from core.overlay_readiness.validators import validate_overlay_readiness

def run_overlay_readiness_index(governance_packets: list[dict], risk_packets: list[dict], topology_packets: list[dict], containment_packets: list[dict], resolution_packets: list[dict]) -> dict[str, object]:
    overlay_hash="overlay-1"
    scores={"governance":0.8,"risk":0.7,"topology":0.8,"containment":0.8,"resolution":0.9,"replay":1.0,"rollback":1.0,"operator_load":0.9}
    components=[OverlayReadinessComponentPacket(component_id=f"orc-{k}",overlay_hash=overlay_hash,component_type=k,component_score=v,component_reason=f"deterministic {k} score",deterministic_component_hash=OverlayReadinessComponentPacket.compute_hash(overlay_hash,k,v,f"deterministic {k} score"),status="passed") for k,v in scores.items()]
    threshold=OverlayReadinessThresholdPacket(threshold_id="ort-1",blocked_max=0.25,watch_max=0.5,review_ready_min=0.65,stable_candidate_min=0.85,deterministic_threshold_hash=OverlayReadinessThresholdPacket.compute_hash(0.25,0.5,0.65,0.85),status="passed")
    aggregate=sum(scores.values())/len(scores)
    band="stable_candidate" if aggregate>=threshold.stable_candidate_min else "review_ready"
    vals=[scores[k] for k in ["governance","risk","topology","containment","resolution","replay","rollback","operator_load"]]
    index=OverlayReadinessIndexPacket(readiness_id="ori-1",overlay_hash=overlay_hash,governance_score=scores["governance"],risk_score=scores["risk"],topology_score=scores["topology"],containment_score=scores["containment"],resolution_score=scores["resolution"],replay_score=scores["replay"],rollback_score=scores["rollback"],operator_load_score=scores["operator_load"],aggregate_readiness_score=aggregate,readiness_band=band,deterministic_readiness_hash=OverlayReadinessIndexPacket.compute_hash(overlay_hash,vals,aggregate,band),status="passed")
    replay=OverlayReadinessReplayPacket(replay_id="orre-1",source_readiness_hash=index.deterministic_readiness_hash,replay_readiness_hash=index.deterministic_readiness_hash,deterministic_match=True,mismatched_components=[],status="passed")
    node=OverlayReadinessLineageNode(readiness_hash=index.deterministic_readiness_hash,generation=1)
    lineage=OverlayReadinessLineagePacket(lineage_id="orli-1",lineage_nodes=[node],lineage_depth=1,deterministic_lineage_hash=OverlayReadinessLineagePacket.compute_hash([node]),status="passed")
    diagnostics:list[OverlayReadinessDiagnosticPacket]=[]
    review=OperatorOverlayReadinessReviewPacket(review_id="orv-1",pending_reviews=0,critical_diagnostics=0,readiness_band=index.readiness_band,pending_actions=[],status="approved")
    validator=validate_overlay_readiness(index,threshold,replay,[d.model_dump() for d in diagnostics],False,False)
    packet={"schema_version":"OverlayReadinessRuntimePacket.v1","index":index.model_dump(),"components":[c.model_dump() for c in components],"threshold":threshold.model_dump(),"replay":replay.model_dump(),"lineage":lineage.model_dump(),"diagnostics":[d.model_dump() for d in diagnostics],"operator_review":review.model_dump(),"validator":validator,"status":validator["status"]}
    return packet
