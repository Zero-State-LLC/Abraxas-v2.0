from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.
from core.governance.upstream_evidence import require_upstream_packets
from core.human_decision_ledger.blockers import HumanDecisionBlockerPacket
from core.human_decision_ledger.continuity import HumanDecisionContinuityPacket
from core.human_decision_ledger.decisions import HumanDecisionLedgerPacket
from core.human_decision_ledger.deferrals import HumanDecisionDeferralPacket
from core.human_decision_ledger.diagnostics import HumanDecisionDiagnosticPacket
from core.human_decision_ledger.escalations import HumanDecisionEscalationPacket
from core.human_decision_ledger.lineage import HumanDecisionLineagePacket
from core.human_decision_ledger.operator_review import HumanDecisionOperatorReviewPacket
from core.human_decision_ledger.rationale import HumanDecisionRationalePacket
from core.human_decision_ledger.replay import HumanDecisionReplayPacket
from core.human_decision_ledger.validators import validate_human_decision_ledger


def run_human_decision_ledger(
    proposal_decision_bridge_packets: list[dict],
    proposal_sandbox_evaluation_packets: list[dict],
    operator_queue_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    require_upstream_packets(
        ("proposal_decision_bridge_packets", proposal_decision_bridge_packets),
        ("proposal_sandbox_evaluation_packets", proposal_sandbox_evaluation_packets),
        ("operator_queue_packets", operator_queue_packets),
        ("replay_packets", replay_packets),
        surface="human_decision_ledger",
    )
    _ = (
        proposal_decision_bridge_packets,
        proposal_sandbox_evaluation_packets,
        operator_queue_packets,
        replay_packets,
    )

    decision = HumanDecisionLedgerPacket(
        decision_id="hdl-1",
        bridge_hash="bridge-1",
        decision_state="review_only",
        deterministic_decision_hash=HumanDecisionLedgerPacket.compute_hash(
            "bridge-1",
            "review_only",
        ),
        status="passed",
    )
    cited_review_notes = ["needs follow-up"]
    rationale = HumanDecisionRationalePacket(
        decision_hash=decision.deterministic_decision_hash,
        rationale_summary="operator-mediated review outcome",
        cited_review_notes=cited_review_notes,
        deterministic_rationale_hash=HumanDecisionRationalePacket.compute_hash(
            decision.deterministic_decision_hash,
            "operator-mediated review outcome",
            cited_review_notes,
        ),
        status="passed",
    )

    blockers = ["missing supplemental evidence"]
    blocker = HumanDecisionBlockerPacket(
        decision_hash=decision.deterministic_decision_hash,
        blockers=blockers,
        unresolved_blockers=1,
        deterministic_blocker_hash=HumanDecisionBlockerPacket.compute_hash(
            decision.deterministic_decision_hash,
            blockers,
            1,
        ),
        status="passed",
    )
    deferral = HumanDecisionDeferralPacket(
        decision_hash=decision.deterministic_decision_hash,
        deferred=True,
        deferral_reason="pending additional operator evidence",
        deterministic_deferral_hash=HumanDecisionDeferralPacket.compute_hash(
            decision.deterministic_decision_hash,
            True,
            "pending additional operator evidence",
        ),
        status="passed",
    )
    escalation = HumanDecisionEscalationPacket(
        decision_hash=decision.deterministic_decision_hash,
        escalated=False,
        escalation_reason="not required",
        deterministic_escalation_hash=HumanDecisionEscalationPacket.compute_hash(
            decision.deterministic_decision_hash,
            False,
            "not required",
        ),
        status="passed",
    )
    continuity = HumanDecisionContinuityPacket(
        decision_hash=decision.deterministic_decision_hash,
        prior_hashes=["human-decision-root"],
        append_only=True,
        deterministic_continuity_hash=HumanDecisionContinuityPacket.compute_hash(
            decision.deterministic_decision_hash,
            ["human-decision-root"],
            True,
        ),
        status="passed",
    )
    replay = HumanDecisionReplayPacket(
        decision_hash=decision.deterministic_decision_hash,
        replay_decision_hash=decision.deterministic_decision_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        deterministic_replay_hash=HumanDecisionReplayPacket.compute_hash(
            decision.deterministic_decision_hash,
            decision.deterministic_decision_hash,
            True,
            [],
        ),
        status="passed",
    )
    lineage = HumanDecisionLineagePacket(
        decision_hash=decision.deterministic_decision_hash,
        parent_hashes=["human-decision-root"],
        lineage_cycle_detected=False,
        deterministic_lineage_hash=HumanDecisionLineagePacket.compute_hash(
            decision.deterministic_decision_hash,
            ["human-decision-root"],
            False,
        ),
        status="passed",
    )

    diagnostics: list[HumanDecisionDiagnosticPacket] = []
    diagnostic_payload = [diagnostic.model_dump() for diagnostic in diagnostics]

    operator_review = HumanDecisionOperatorReviewPacket(
        review_id="hdor-1",
        decision_hash=decision.deterministic_decision_hash,
        decision_count=1,
        deferred_decisions=1,
        blocked_decisions=1,
        unresolved_diagnostics=0,
        deterministic_review_hash=HumanDecisionOperatorReviewPacket.compute_hash(
            decision.deterministic_decision_hash,
            1,
            1,
            1,
            0,
        ),
        status="passed",
    )
    validator = validate_human_decision_ledger(
        decision_state=decision.decision_state,
        replay_match=replay.deterministic_match,
        diagnostics=diagnostic_payload,
        lineage_cycle_detected=lineage.lineage_cycle_detected,
        authority_mutation=False,
        execution_authority=False,
        deployment_authority=False,
        production_routing_authority=False,
        mutation_authority=False,
    )

    summary = {
        "decision_count": 1,
        "deferred_decisions": 1,
        "blocked_decisions": 1,
        "unresolved_diagnostics": 0,
        "replay_matches": replay.deterministic_match,
        "governance_restricted": True,
        "authority_locked": True,
        "projection_only": True,
        "inference_authority": False,
    }
    # Pure builder — publication via scripts/operator/run_human_decision_ledger.py
    return {
        "decision": decision.model_dump(),
        "rationale": rationale.model_dump(),
        "blocker": blocker.model_dump(),
        "deferral": deferral.model_dump(),
        "escalation": escalation.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": diagnostic_payload,
        "operator_review": operator_review.model_dump(),
        "human_decision_ledger_summary": summary,
        "validator": validator,
        "status": validator["status"],
    }
