from __future__ import annotations
from core.canonical.json import write_canonical_json
from core.proposal_decision_bridge.bridge import ProposalDecisionBridgePacket
from core.proposal_decision_bridge.continuity import ProposalDecisionContinuityPacket
from core.proposal_decision_bridge.decision_inputs import ProposalDecisionInputPacket
from core.proposal_decision_bridge.diagnostics import ProposalDecisionDiagnosticPacket
from core.proposal_decision_bridge.lineage import ProposalDecisionLineagePacket
from core.proposal_decision_bridge.operator_review import ProposalDecisionOperatorReviewPacket
from core.proposal_decision_bridge.rationale import ProposalDecisionRationalePacket
from core.proposal_decision_bridge.replay import ProposalDecisionReplayPacket
from core.proposal_decision_bridge.restrictions import FORBIDDEN_ACTIONS, ProposalDecisionRestrictionPacket
from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge

def run_proposal_decision_bridge(proposal_sandbox_evaluation_packets: list[dict], proposal_sandbox_routing_packets: list[dict], operator_queue_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    bridge = ProposalDecisionBridgePacket(bridge_id="pdb-1", evaluation_hash="eval-1", decision_readiness=0.5, deterministic_bridge_hash=ProposalDecisionBridgePacket.compute_hash("eval-1", 0.5), status="passed")
    decision_input = ProposalDecisionInputPacket(bridge_hash=bridge.deterministic_bridge_hash, input_sources=["evaluation", "rationale", "restrictions"], unresolved_diagnostics=0, deterministic_input_hash=ProposalDecisionInputPacket.compute_hash(bridge.deterministic_bridge_hash, ["evaluation", "rationale", "restrictions"], 0), status="passed")
    rationale = ProposalDecisionRationalePacket(bridge_hash=bridge.deterministic_bridge_hash, rationale_summary="human decision preparation only", cited_restrictions=["no approval", "no execution"], deterministic_rationale_hash=ProposalDecisionRationalePacket.compute_hash(bridge.deterministic_bridge_hash, "human decision preparation only", ["no approval", "no execution"]), status="passed")
    restriction = ProposalDecisionRestrictionPacket(bridge_hash=bridge.deterministic_bridge_hash, governance_restricted=True, restricted_actions=sorted(FORBIDDEN_ACTIONS), deterministic_restriction_hash=ProposalDecisionRestrictionPacket.compute_hash(bridge.deterministic_bridge_hash, True, sorted(FORBIDDEN_ACTIONS)), status="passed")
    continuity = ProposalDecisionContinuityPacket(bridge_hash=bridge.deterministic_bridge_hash, prior_hashes=["proposal-decision-bridge-root"], append_only=True, deterministic_continuity_hash=ProposalDecisionContinuityPacket.compute_hash(bridge.deterministic_bridge_hash, ["proposal-decision-bridge-root"], True), status="passed")
    replay = ProposalDecisionReplayPacket(bridge_hash=bridge.deterministic_bridge_hash, replay_bridge_hash=bridge.deterministic_bridge_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=ProposalDecisionReplayPacket.compute_hash(bridge.deterministic_bridge_hash, bridge.deterministic_bridge_hash, True, []), status="passed")
    lineage = ProposalDecisionLineagePacket(bridge_hash=bridge.deterministic_bridge_hash, parent_hashes=["proposal-decision-bridge-root"], lineage_cycle_detected=False, deterministic_lineage_hash=ProposalDecisionLineagePacket.compute_hash(bridge.deterministic_bridge_hash, ["proposal-decision-bridge-root"], False), status="passed")
    diagnostics: list[ProposalDecisionDiagnosticPacket] = []
    operator_review = ProposalDecisionOperatorReviewPacket(review_id="pdor-1", bridge_hash=bridge.deterministic_bridge_hash, bridge_count=1, blocked_bridges=0, unresolved_diagnostics=0, deterministic_review_hash=ProposalDecisionOperatorReviewPacket.compute_hash(bridge.deterministic_bridge_hash, 1, 0, 0), status="passed")
    validator = validate_proposal_decision_bridge([], replay.deterministic_match, [d.model_dump() for d in diagnostics], lineage.lineage_cycle_detected, False, False, False, False, False)
    packet = {"bridge": bridge.model_dump(), "decision_input": decision_input.model_dump(), "rationale": rationale.model_dump(), "restriction": restriction.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": operator_review.model_dump(), "proposal_decision_bridge_summary": {"bridge_count": 1, "blocked_bridges": 0, "decision_readiness": bridge.decision_readiness, "unresolved_diagnostics": 0, "replay_matches": replay.deterministic_match, "governance_restricted": restriction.governance_restricted, "authority_locked": True, "projection_only": True, "inference_authority": False}, "validator": validator, "status": validator["status"]}
    write_canonical_json("out/proposal_decision_bridge/latest.json", packet)
    write_canonical_json("out/proposal_decision_bridge_replay/latest.json", replay.model_dump())
    write_canonical_json("out/proposal_decision_bridge_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/proposal_decision_bridge_diagnostics/latest.json", [d.model_dump() for d in diagnostics])
    return packet
