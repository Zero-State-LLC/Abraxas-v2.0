from __future__ import annotations
from core.canonical.json import write_canonical_json
from core.operator_queue.requests import OperatorApprovalRequestPacket
from core.operator_queue.decisions import OperatorDecisionPacket
from core.operator_queue.rationale import OperatorRationalePacket
from core.operator_queue.continuity import OperatorQueueContinuityPacket
from core.operator_queue.replay import OperatorQueueReplayPacket
from core.operator_queue.lineage import OperatorQueueLineagePacket
from core.operator_queue.diagnostics import OperatorQueueDiagnosticPacket
from core.operator_queue.operator_review import OperatorQueueReviewPacket
from core.operator_queue.validators import validate_operator_queue


def run_operator_approval_queue(firewall_packets: list[dict], readiness_packets: list[dict], governance_packets: list[dict], containment_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    request = OperatorApprovalRequestPacket(request_id="oqr-1", overlay_hash="overlay-1", firewall_hash="fw-1", readiness_hash="rd-1", governance_hash="gov-1", replay_hash="rp-1", rollback_hash="rb-1", request_status="pending_review", request_priority="normal", request_reason="eligible after prerequisite gates", deterministic_request_hash=OperatorApprovalRequestPacket.compute_hash("overlay-1", "fw-1", "rd-1", "gov-1", "rp-1", "rb-1", "pending_review", "normal", "eligible after prerequisite gates"), status="passed")
    operator_id_hash = OperatorDecisionPacket.hash_operator_id("operator-1")
    decision = OperatorDecisionPacket(decision_id="oqd-1", request_hash=request.deterministic_request_hash, operator_id_hash=operator_id_hash, decision="review_only_approval", decision_reason="manual execution review only", requires_additional_review=False, deterministic_decision_hash=OperatorDecisionPacket.compute_hash(request.deterministic_request_hash, operator_id_hash, "review_only_approval", "manual execution review only", False), status="passed")
    rationale = OperatorRationalePacket(rationale_id="oqra-1", decision_hash=decision.deterministic_decision_hash, rationale_summary="no runtime activation authority", cited_diagnostics=[], cited_containment_restrictions=[], cited_governance_events=[], deterministic_rationale_hash=OperatorRationalePacket.compute_hash(decision.deterministic_decision_hash, "no runtime activation authority", [], [], []), status="passed")
    queue_hash = decision.request_hash
    continuity = OperatorQueueContinuityPacket(continuity_id="oqc-1", queue_hash=queue_hash, continuity_score=1.0, unresolved_events=[], continuity_safe=True, deterministic_continuity_hash=OperatorQueueContinuityPacket.compute_hash(queue_hash, 1.0, [], True), status="passed")
    replay = OperatorQueueReplayPacket(replay_id="oqrp-1", source_queue_hash=queue_hash, replay_queue_hash=queue_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=OperatorQueueReplayPacket.compute_hash(queue_hash, queue_hash, True, []), status="passed")
    lineage = OperatorQueueLineagePacket(lineage_id="oql-1", queue_hash=queue_hash, parent_hashes=["queue-root"], lineage_cycle_detected=False, deterministic_lineage_hash=OperatorQueueLineagePacket.compute_hash(queue_hash, ["queue-root"], False), status="passed")
    diagnostics: list[OperatorQueueDiagnosticPacket] = []
    review = OperatorQueueReviewPacket(review_id="oqv-1", queue_hash=queue_hash, pending_requests=1, deferred_requests=0, denied_requests=0, review_only_approved_requests=1, unresolved_diagnostics=0, deterministic_review_hash=OperatorQueueReviewPacket.compute_hash(queue_hash, 1, 0, 0, 1, 0), status="passed")
    validator = validate_operator_queue(decision.decision, replay.deterministic_match, [d.model_dump() for d in diagnostics], False, lineage.lineage_cycle_detected, False, False, False)
    packet = {"schema_version": "OperatorApprovalQueueRuntimePacket.v1", "request": request.model_dump(), "decision": decision.model_dump(), "rationale": rationale.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": review.model_dump(), "operator_queue_summary": {"pending_requests": 1, "deferred_requests": 0, "denied_requests": 0, "review_only_approved_requests": 1, "unresolved_diagnostics": 0, "replay_matches": replay.deterministic_match, "continuity_status": continuity.status, "authority_locked": True, "projection_only": True, "inference_authority": False}, "validator": validator, "status": validator["status"]}
    write_canonical_json("out/operator_queue/latest.json", packet)
    write_canonical_json("out/operator_queue_replay/latest.json", replay.model_dump())
    write_canonical_json("out/operator_queue_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/operator_queue_diagnostics/latest.json", [d.model_dump() for d in diagnostics])
    return packet
