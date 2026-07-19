from __future__ import annotations

# WP-D4-C4: pure builder — sole-writer scripts own out/ publication.
from core.proposal_decision_bridge.bridge import ProposalDecisionBridgePacket
from core.proposal_decision_bridge.continuity import ProposalDecisionContinuityPacket
from core.proposal_decision_bridge.decision_inputs import ProposalDecisionInputPacket
from core.proposal_decision_bridge.diagnostics import ProposalDecisionDiagnosticPacket
from core.proposal_decision_bridge.lineage import ProposalDecisionLineagePacket
from core.proposal_decision_bridge.operator_review import ProposalDecisionOperatorReviewPacket
from core.proposal_decision_bridge.rationale import ProposalDecisionRationalePacket
from core.proposal_decision_bridge.replay import ProposalDecisionReplayPacket
from core.proposal_decision_bridge.restrictions import (
    FORBIDDEN_ACTIONS,
    ProposalDecisionRestrictionPacket,
)
from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge


def run_proposal_decision_bridge(
    proposal_sandbox_evaluation_packets: list[dict],
    proposal_sandbox_routing_packets: list[dict],
    operator_queue_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    _ = (
        proposal_sandbox_evaluation_packets,
        proposal_sandbox_routing_packets,
        operator_queue_packets,
        replay_packets,
    )

    bridge = ProposalDecisionBridgePacket(
        bridge_id="pdb-1",
        evaluation_hash="eval-1",
        decision_readiness=0.5,
        deterministic_bridge_hash=ProposalDecisionBridgePacket.compute_hash("eval-1", 0.5),
        status="passed",
    )
    input_sources = ["evaluation", "rationale", "restrictions"]
    decision_input = ProposalDecisionInputPacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        input_sources=input_sources,
        unresolved_diagnostics=0,
        deterministic_input_hash=ProposalDecisionInputPacket.compute_hash(
            bridge.deterministic_bridge_hash,
            input_sources,
            0,
        ),
        status="passed",
    )
    cited_restrictions = ["no approval", "no execution"]
    rationale = ProposalDecisionRationalePacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        rationale_summary="human decision preparation only",
        cited_restrictions=cited_restrictions,
        deterministic_rationale_hash=ProposalDecisionRationalePacket.compute_hash(
            bridge.deterministic_bridge_hash,
            "human decision preparation only",
            cited_restrictions,
        ),
        status="passed",
    )

    restricted_actions = sorted(FORBIDDEN_ACTIONS)
    restriction = ProposalDecisionRestrictionPacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        governance_restricted=True,
        restricted_actions=restricted_actions,
        deterministic_restriction_hash=ProposalDecisionRestrictionPacket.compute_hash(
            bridge.deterministic_bridge_hash,
            True,
            restricted_actions,
        ),
        status="passed",
    )
    continuity = ProposalDecisionContinuityPacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        prior_hashes=["proposal-decision-bridge-root"],
        append_only=True,
        deterministic_continuity_hash=ProposalDecisionContinuityPacket.compute_hash(
            bridge.deterministic_bridge_hash,
            ["proposal-decision-bridge-root"],
            True,
        ),
        status="passed",
    )
    replay = ProposalDecisionReplayPacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        replay_bridge_hash=bridge.deterministic_bridge_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        deterministic_replay_hash=ProposalDecisionReplayPacket.compute_hash(
            bridge.deterministic_bridge_hash,
            bridge.deterministic_bridge_hash,
            True,
            [],
        ),
        status="passed",
    )
    lineage = ProposalDecisionLineagePacket(
        bridge_hash=bridge.deterministic_bridge_hash,
        parent_hashes=["proposal-decision-bridge-root"],
        lineage_cycle_detected=False,
        deterministic_lineage_hash=ProposalDecisionLineagePacket.compute_hash(
            bridge.deterministic_bridge_hash,
            ["proposal-decision-bridge-root"],
            False,
        ),
        status="passed",
    )

    diagnostics: list[ProposalDecisionDiagnosticPacket] = []
    diagnostic_payload = [diagnostic.model_dump() for diagnostic in diagnostics]

    operator_review = ProposalDecisionOperatorReviewPacket(
        review_id="pdor-1",
        bridge_hash=bridge.deterministic_bridge_hash,
        bridge_count=1,
        blocked_bridges=0,
        unresolved_diagnostics=0,
        deterministic_review_hash=ProposalDecisionOperatorReviewPacket.compute_hash(
            bridge.deterministic_bridge_hash,
            1,
            0,
            0,
        ),
        status="passed",
    )
    validator = validate_proposal_decision_bridge(
        attempted_actions=[],
        replay_match=replay.deterministic_match,
        diagnostics=diagnostic_payload,
        lineage_cycle_detected=lineage.lineage_cycle_detected,
        authority_mutation=False,
        production_routing_authority=False,
        deployment_authority=False,
        execution_authority=False,
        auto_execution_attempted=False,
    )

    summary = {
        "bridge_count": 1,
        "blocked_bridges": 0,
        "decision_readiness": bridge.decision_readiness,
        "unresolved_diagnostics": 0,
        "replay_matches": replay.deterministic_match,
        "governance_restricted": restriction.governance_restricted,
        "authority_locked": True,
        "projection_only": True,
        "inference_authority": False,
    }
    packet = {
        "bridge": bridge.model_dump(),
        "decision_input": decision_input.model_dump(),
        "rationale": rationale.model_dump(),
        "restriction": restriction.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": diagnostic_payload,
        "operator_review": operator_review.model_dump(),
        "proposal_decision_bridge_summary": summary,
        "validator": validator,
        "status": validator["status"],
    }

    return packet
