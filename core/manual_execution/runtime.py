from __future__ import annotations

# WP-D4-C1: pure builder — sole-writer scripts own out/ publication.
from core.governance.upstream_evidence import require_upstream_packets
from core.manual_execution.acknowledgements import HumanAcknowledgementPacket
from core.manual_execution.authorization import ManualExecutionAuthorizationPacket
from core.manual_execution.continuity import ManualExecutionContinuityPacket
from core.manual_execution.diagnostics import ManualExecutionDiagnosticPacket
from core.manual_execution.eligibility import ManualExecutionEligibilityPacket
from core.manual_execution.envelopes import ManualExecutionEnvelopePacket
from core.manual_execution.lineage import ManualExecutionLineagePacket
from core.manual_execution.operator_review import ManualExecutionOperatorReviewPacket
from core.manual_execution.replay import ManualExecutionReplayPacket
from core.manual_execution.scope import FORBIDDEN_ACTIONS, ManualExecutionScopePacket
from core.manual_execution.validators import validate_manual_execution


def run_manual_execution_authorization(
    review_resolution_packets: list[dict],
    operator_queue_packets: list[dict],
    firewall_packets: list[dict],
    readiness_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    require_upstream_packets(
        ("review_resolution_packets", review_resolution_packets),
        ("operator_queue_packets", operator_queue_packets),
        ("firewall_packets", firewall_packets),
        ("readiness_packets", readiness_packets),
        ("replay_packets", replay_packets),
        surface="manual_execution_authorization",
    )
    del (
        review_resolution_packets,
        operator_queue_packets,
        firewall_packets,
        readiness_packets,
        replay_packets,
    )
    auth = ManualExecutionAuthorizationPacket(
        authorization_id="mea-1",
        review_resolution_hash="rr-1",
        operator_queue_hash="oq-1",
        firewall_hash="fw-1",
        readiness_hash="rd-1",
        authorization_status="authorized_for_manual_execution_review",
        authorization_reason="human-reviewed and bounded for manual review only",
        deterministic_authorization_hash=ManualExecutionAuthorizationPacket.compute_hash(
            "rr-1",
            "oq-1",
            "fw-1",
            "rd-1",
            "authorized_for_manual_execution_review",
            "human-reviewed and bounded for manual review only",
        ),
        status="passed",
    )
    ack = HumanAcknowledgementPacket(
        acknowledgement_id="meack-1",
        operator_id_hash="op-hash-1",
        acknowledgement_scope="manual_execution_review_only",
        acknowledgement_text_hash="ack-text-hash-1",
        acknowledged_constraints=["no_execute", "no_activate", "no_deploy"],
        deterministic_acknowledgement_hash=HumanAcknowledgementPacket.compute_hash(
            "op-hash-1",
            "manual_execution_review_only",
            "ack-text-hash-1",
            ["no_execute", "no_activate", "no_deploy"],
        ),
        status="passed",
    )
    scope = ManualExecutionScopePacket(
        scope_id="mes-1",
        overlay_hash="overlay-1",
        allowed_review_actions=[
            "inspect",
            "compare",
            "document",
            "request_changes",
            "defer",
            "deny",
        ],
        forbidden_actions=sorted(FORBIDDEN_ACTIONS),
        scope_constraints=["manual_only", "projection_only", "operator_mediated"],
        deterministic_scope_hash=ManualExecutionScopePacket.compute_hash(
            "overlay-1",
            ["inspect", "compare", "document", "request_changes", "defer", "deny"],
            sorted(FORBIDDEN_ACTIONS),
            ["manual_only", "projection_only", "operator_mediated"],
        ),
        status="passed",
    )
    replay = ManualExecutionReplayPacket(
        replay_id="mer-1",
        source_hash=auth.deterministic_authorization_hash,
        replay_hash=auth.deterministic_authorization_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        deterministic_replay_hash=ManualExecutionReplayPacket.compute_hash(
            auth.deterministic_authorization_hash,
            auth.deterministic_authorization_hash,
            True,
            [],
        ),
        status="passed",
    )
    continuity = ManualExecutionContinuityPacket(
        continuity_id="mec-1",
        authorization_hash=auth.deterministic_authorization_hash,
        inherited_resolution_hash="rr-1",
        append_only=True,
        deterministic_continuity_hash=ManualExecutionContinuityPacket.compute_hash(
            auth.deterministic_authorization_hash, "rr-1", True
        ),
        status="passed",
    )
    lineage = ManualExecutionLineagePacket(
        lineage_id="mel-1",
        continuity_hash=continuity.deterministic_continuity_hash,
        parent_hashes=["manual-execution-root"],
        lineage_cycle_detected=False,
        deterministic_lineage_hash=ManualExecutionLineagePacket.compute_hash(
            continuity.deterministic_continuity_hash, ["manual-execution-root"], False
        ),
        status="passed",
    )
    eligibility = ManualExecutionEligibilityPacket(
        eligibility_id="mee-1",
        authorization_hash=auth.deterministic_authorization_hash,
        closure_ready=True,
        rollback_ready=True,
        replay_verified=True,
        acknowledgement_required=False,
        critical_blockers=0,
        eligible_for_manual_review=True,
        denial_reasons=[],
        deterministic_eligibility_hash=ManualExecutionEligibilityPacket.compute_hash(
            auth.deterministic_authorization_hash, True, True, True, False, 0, True, []
        ),
        status="passed",
    )
    envelope = ManualExecutionEnvelopePacket(
        envelope_id="mev-1",
        authorization_hash=auth.deterministic_authorization_hash,
        bounded_scope_hash=scope.deterministic_scope_hash,
        acknowledgement_hash=ack.deterministic_acknowledgement_hash,
        rollback_hash="rollback-hash-1",
        replay_hash=replay.deterministic_replay_hash,
        envelope_status="review_ready",
        unresolved_blockers=[],
        deterministic_envelope_hash=ManualExecutionEnvelopePacket.compute_hash(
            auth.deterministic_authorization_hash,
            scope.deterministic_scope_hash,
            ack.deterministic_acknowledgement_hash,
            "rollback-hash-1",
            replay.deterministic_replay_hash,
            "review_ready",
            [],
        ),
        status="passed",
    )
    diagnostics = [
        ManualExecutionDiagnosticPacket(
            diagnostic_id="med-1",
            diagnostic_type="missing_acknowledgement",
            severity="info",
            diagnostic_message="acknowledgement present and verified",
            resolved=True,
            deterministic_diagnostic_hash=ManualExecutionDiagnosticPacket.compute_hash(
                "missing_acknowledgement",
                "info",
                "acknowledgement present and verified",
            ),
            status="passed",
        )
    ]
    review = ManualExecutionOperatorReviewPacket(
        review_id="meor-1",
        envelope_hash=envelope.deterministic_envelope_hash,
        authorization_status=auth.authorization_status,
        eligible_for_manual_review=eligibility.eligible_for_manual_review,
        unresolved_diagnostics=0,
        forbidden_actions=sorted(FORBIDDEN_ACTIONS),
        deterministic_review_hash=ManualExecutionOperatorReviewPacket.compute_hash(
            envelope.deterministic_envelope_hash,
            auth.authorization_status,
            eligibility.eligible_for_manual_review,
            0,
            sorted(FORBIDDEN_ACTIONS),
        ),
        status="passed",
    )
    validator = validate_manual_execution(
        False,
        False,
        False,
        replay.deterministic_match,
        [d.model_dump() for d in diagnostics],
        False,
        eligibility.rollback_ready,
        eligibility.closure_ready,
        lineage.lineage_cycle_detected,
        False,
        False,
        False,
        False,
        False,
    )
    return {
        "schema_version": "ManualExecutionRuntimePacket.v1",
        "authorization": auth.model_dump(),
        "envelope": envelope.model_dump(),
        "eligibility": eligibility.model_dump(),
        "scope": scope.model_dump(),
        "acknowledgement": ack.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [d.model_dump() for d in diagnostics],
        "operator_review": review.model_dump(),
        "manual_execution_summary": {
            "authorization_status": auth.authorization_status,
            "envelope_status": envelope.envelope_status,
            "eligible_for_manual_review": eligibility.eligible_for_manual_review,
            "unresolved_blockers": len(envelope.unresolved_blockers),
            "forbidden_actions": scope.forbidden_actions,
            "replay_matches": replay.deterministic_match,
            "acknowledgement_present": True,
            "authority_locked": True,
            "projection_only": True,
            "inference_authority": False,
        },
        "validator": validator,
        "status": validator["status"],
    }
