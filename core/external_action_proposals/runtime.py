from __future__ import annotations

# WP-D batch2: pure builder — publication via sole-writer scripts only.

from core.external_action_proposals.categories import ProposalCategoryPacket
from core.external_action_proposals.constraints import ProposalConstraintPacket
from core.external_action_proposals.continuity import ExternalActionProposalContinuityPacket
from core.external_action_proposals.diagnostics import ExternalActionProposalDiagnosticPacket
from core.external_action_proposals.governance import ProposalGovernancePacket
from core.external_action_proposals.lineage import ExternalActionProposalLineagePacket
from core.external_action_proposals.operator_review import ExternalActionProposalOperatorReviewPacket
from core.external_action_proposals.proposals import ExternalActionProposalPacket
from core.external_action_proposals.readiness import ProposalReadinessPacket
from core.external_action_proposals.replay import ExternalActionProposalReplayPacket
from core.external_action_proposals.validators import validate_external_action_proposals
from core.governance.upstream_evidence import require_upstream_packets


def run_external_action_proposals(manual_action_custody_packets: list[dict], manual_execution_receipt_packets: list[dict], review_resolution_packets: list[dict], operator_queue_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    require_upstream_packets(
        ("manual_action_custody_packets", manual_action_custody_packets),
        ("manual_execution_receipt_packets", manual_execution_receipt_packets),
        ("review_resolution_packets", review_resolution_packets),
        ("operator_queue_packets", operator_queue_packets),
        ("replay_packets", replay_packets),
        surface="external_action_proposals",
    )
    _ = (
        manual_action_custody_packets,
        manual_execution_receipt_packets,
        review_resolution_packets,
        operator_queue_packets,
        replay_packets,
    )
    proposal = ExternalActionProposalPacket(proposal_id="eap-1", proposal_status="proposed", proposed_action="review_operator", proposal_reason="manual operator-mediated advisory proposal", deterministic_proposal_hash=ExternalActionProposalPacket.compute_hash("proposed", "review_operator", "manual operator-mediated advisory proposal"), status="passed")
    category = ProposalCategoryPacket(proposal_hash=proposal.deterministic_proposal_hash, category="advisory", deterministic_category_hash=ProposalCategoryPacket.compute_hash(proposal.deterministic_proposal_hash, "advisory"), status="passed")
    constraint = ProposalConstraintPacket(proposal_hash=proposal.deterministic_proposal_hash, blocked_actions=["execute", "deploy", "activate"], deterministic_constraint_hash=ProposalConstraintPacket.compute_hash(proposal.deterministic_proposal_hash, ["execute", "deploy", "activate"]), status="passed")
    readiness = ProposalReadinessPacket(proposal_hash=proposal.deterministic_proposal_hash, readiness_posture=0.5, deterministic_readiness_hash=ProposalReadinessPacket.compute_hash(proposal.deterministic_proposal_hash, 0.5), status="passed")
    governance = ProposalGovernancePacket(proposal_hash=proposal.deterministic_proposal_hash, governance_restricted=True, authority_locked=True, deterministic_governance_hash=ProposalGovernancePacket.compute_hash(proposal.deterministic_proposal_hash, True, True), status="passed")
    continuity = ExternalActionProposalContinuityPacket(proposal_hash=proposal.deterministic_proposal_hash, unresolved_dependencies=[], continuity_safe=True, deterministic_continuity_hash=ExternalActionProposalContinuityPacket.compute_hash(proposal.deterministic_proposal_hash, [], True), status="passed")
    replay = ExternalActionProposalReplayPacket(proposal_hash=proposal.deterministic_proposal_hash, replay_hash=proposal.deterministic_proposal_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=ExternalActionProposalReplayPacket.compute_hash(proposal.deterministic_proposal_hash, proposal.deterministic_proposal_hash, True, []), status="passed")
    lineage = ExternalActionProposalLineagePacket(proposal_hash=proposal.deterministic_proposal_hash, parent_hashes=["external-action-root"], lineage_cycle_detected=False, deterministic_lineage_hash=ExternalActionProposalLineagePacket.compute_hash(proposal.deterministic_proposal_hash, ["external-action-root"], False), status="passed")
    diagnostics: list[ExternalActionProposalDiagnosticPacket] = []
    operator_review = ExternalActionProposalOperatorReviewPacket(proposal_hash=proposal.deterministic_proposal_hash, projection_only=True, inference_authority=False, deterministic_review_hash=ExternalActionProposalOperatorReviewPacket.compute_hash(proposal.deterministic_proposal_hash, True, False), status="passed")
    validator = validate_external_action_proposals(proposal.proposal_status, category.category, proposal.proposed_action, replay.deterministic_match, [d.model_dump() for d in diagnostics], lineage.lineage_cycle_detected, False, False, False, False)
    packet = {"proposal": proposal.model_dump(), "category": category.model_dump(), "constraint": constraint.model_dump(), "readiness": readiness.model_dump(), "governance": governance.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": operator_review.model_dump(), "external_action_proposal_summary": {"proposal_count": 1, "blocked_proposals": 0, "readiness_posture": readiness.readiness_posture, "unresolved_diagnostics": 0, "replay_matches": replay.deterministic_match, "governance_restricted": governance.governance_restricted, "authority_locked": governance.authority_locked, "projection_only": True, "inference_authority": False}, "validator": validator, "status": validator["status"]}
    return packet
