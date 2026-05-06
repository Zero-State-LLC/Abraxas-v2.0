from __future__ import annotations
from core.overlay_readiness.index import OverlayReadinessIndexPacket
from core.overlay_readiness.thresholds import OverlayReadinessThresholdPacket
from core.overlay_readiness.replay import OverlayReadinessReplayPacket

def validate_overlay_readiness(index: OverlayReadinessIndexPacket, threshold: OverlayReadinessThresholdPacket, replay: OverlayReadinessReplayPacket, diagnostics: list[dict], lineage_cycles_exist: bool, auto_approval_detected: bool) -> dict[str, object]:
    vals=[index.governance_score,index.risk_score,index.topology_score,index.containment_score,index.resolution_score,index.replay_score,index.rollback_score,index.operator_load_score,index.aggregate_readiness_score]
    if any(v<0 or v>1 for v in vals):
        return {"status":"failed","reason":"score bounds"}
    if not (threshold.blocked_max <= threshold.watch_max <= threshold.review_ready_min <= threshold.stable_candidate_min):
        return {"status":"failed","reason":"threshold order"}
    if not replay.deterministic_match:
        return {"status":"failed","reason":"replay mismatch"}
    if auto_approval_detected:
        return {"status":"failed","reason":"auto approval detected"}
    if any(d.get("severity")=="critical" for d in diagnostics):
        return {"status":"failed","reason":"critical diagnostics"}
    if lineage_cycles_exist:
        return {"status":"failed","reason":"lineage cycles"}
    index.authority.assert_locked()
    threshold.authority.assert_locked()
    return {"status":"passed","reason":"overlay readiness validated"}
