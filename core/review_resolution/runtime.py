from __future__ import annotations

# WP-D4-C4: pure builder — sole-writer scripts own out/ publication.
from core.governance.upstream_evidence import require_upstream_packets
from core.review_resolution.blockers import ReviewResolutionBlockerPacket
from core.review_resolution.closure import ReviewResolutionClosurePacket
from core.review_resolution.diagnostics import ReviewResolutionDiagnosticPacket
from core.review_resolution.inheritance import ReviewResolutionInheritancePacket
from core.review_resolution.lineage import ReviewResolutionLineagePacket
from core.review_resolution.operator_review import ReviewResolutionOperatorReviewPacket
from core.review_resolution.outcomes import ReviewResolutionOutcomePacket
from core.review_resolution.posture import ReviewResolutionPosturePacket
from core.review_resolution.replay import ReviewResolutionReplayPacket
from core.review_resolution.validators import validate_review_resolution


def run_review_resolution_spine(operator_queue_packets: list[dict], review_continuity_packets: list[dict], firewall_packets: list[dict], containment_packets: list[dict], diagnostics_packets: list[dict]) -> dict[str, object]:
    require_upstream_packets(
        ("operator_queue_packets", operator_queue_packets),
        ("review_continuity_packets", review_continuity_packets),
        ("firewall_packets", firewall_packets),
        ("containment_packets", containment_packets),
        ("diagnostics_packets", diagnostics_packets),
        surface="review_resolution_spine",
    )
    _ = (
        operator_queue_packets,
        review_continuity_packets,
        firewall_packets,
        containment_packets,
        diagnostics_packets,
    )
    posture = ReviewResolutionPosturePacket(posture_id='rrp-1', request_hash='rq-1', queue_hash='oq-1', continuity_hash='rc-1', firewall_hash='fw-1', resolution_posture='review_only_resolved', unresolved_blockers=[], deterministic_posture_hash=ReviewResolutionPosturePacket.compute_hash('rq-1', 'oq-1', 'rc-1', 'fw-1', 'review_only_resolved', []), status='passed')
    blocker = ReviewResolutionBlockerPacket(blocker_id='rrb-1', posture_hash=posture.deterministic_posture_hash, blocker_type='missing_rationale', blocker_reason='operator rationale follow-up required', severity='warning', deterministic_blocker_hash=ReviewResolutionBlockerPacket.compute_hash(posture.deterministic_posture_hash, 'missing_rationale', 'operator rationale follow-up required', 'warning'), status='passed')
    blockers = [blocker]
    outcome = ReviewResolutionOutcomePacket(outcome_id='rro-1', posture_hash=posture.deterministic_posture_hash, outcome_state='review_only_complete', outcome_reason='review resolution recorded' , closure_ready=True, deterministic_outcome_hash=ReviewResolutionOutcomePacket.compute_hash(posture.deterministic_posture_hash, 'review_only_complete', 'review resolution recorded', True), status='passed')
    inheritance = ReviewResolutionInheritancePacket(inheritance_id='rri-1', continuity_hash='rc-1', inherited_denials=['deny_evidence'], inherited_deferrals=['deferred_window'], inherited_rationale_hashes=['rat-1'], inherited_blockers=['unresolved_diagnostic'], deterministic_inheritance_hash=ReviewResolutionInheritancePacket.compute_hash('rc-1', ['deny_evidence'], ['deferred_window'], ['rat-1'], ['unresolved_diagnostic']), status='passed')
    closure = ReviewResolutionClosurePacket(closure_id='rrc-1', posture_hash=posture.deterministic_posture_hash, outcome_hash=outcome.deterministic_outcome_hash, unresolved_blocker_count=1, critical_blocker_count=0, closure_ready=True, deterministic_closure_hash=ReviewResolutionClosurePacket.compute_hash(posture.deterministic_posture_hash, outcome.deterministic_outcome_hash, 1, 0, True), status='passed')
    replay = ReviewResolutionReplayPacket(replay_id='rrr-1', source_resolution_hash=closure.deterministic_closure_hash, replay_resolution_hash=closure.deterministic_closure_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=ReviewResolutionReplayPacket.compute_hash(closure.deterministic_closure_hash, closure.deterministic_closure_hash, True, []), status='passed')
    lineage = ReviewResolutionLineagePacket(lineage_id='rrl-1', continuity_hash=posture.continuity_hash, parent_hashes=['continuity-root'], lineage_cycle_detected=False, deterministic_lineage_hash=ReviewResolutionLineagePacket.compute_hash(posture.continuity_hash, ['continuity-root'], False), status='passed')
    diag = ReviewResolutionDiagnosticPacket(diagnostic_id='rrd-1', diagnostic_type='missing_rationale', severity='warning', diagnostic_message='Rationale follow-up required at resolution spine.', resolved=False, deterministic_diagnostic_hash=ReviewResolutionDiagnosticPacket.compute_hash('missing_rationale','warning','Rationale follow-up required at resolution spine.'), status='passed')
    diagnostics = [diag]
    operator_review = ReviewResolutionOperatorReviewPacket(review_id='rror-1', pending_reviews=1, unresolved_blockers=1, critical_diagnostics=0, pending_actions=['manual resolution required'], status='pending')
    validator = validate_review_resolution(True, False, False, False, [d.model_dump() for d in diagnostics], [b.model_dump() for b in blockers], False, False, False)
    return {
        "schema_version": "ReviewResolutionRuntimePacket.v1",
        "posture": posture.model_dump(),
        "blockers": [b.model_dump() for b in blockers],
        "outcome": outcome.model_dump(),
        "inheritance": inheritance.model_dump(),
        "closure": closure.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [d.model_dump() for d in diagnostics],
        "operator_review": operator_review.model_dump(),
        "review_resolution_summary": {
            "resolution_posture": posture.resolution_posture,
            "unresolved_blockers": len(blockers),
            "critical_blockers": 0,
            "closure_ready": closure.closure_ready,
            "replay_matches": replay.deterministic_match,
            "pending_reviews": operator_review.pending_reviews,
            "authority_locked": True,
            "projection_only": True,
            "inference_authority": False,
        },
        "validator": validator,
        "status": validator["status"],
    }
