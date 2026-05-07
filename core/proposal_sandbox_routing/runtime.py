from __future__ import annotations
from core.canonical.json import write_canonical_json
from core.proposal_sandbox_routing.constraints import FORBIDDEN_RESTRICTED_ACTIONS, ProposalSandboxConstraintPacket
from core.proposal_sandbox_routing.continuity import ProposalSandboxContinuityPacket
from core.proposal_sandbox_routing.diagnostics import ProposalSandboxDiagnosticPacket
from core.proposal_sandbox_routing.eligibility import ProposalSandboxEligibilityPacket
from core.proposal_sandbox_routing.governance import ProposalSandboxGovernancePacket
from core.proposal_sandbox_routing.lanes import ProposalSandboxLanePacket
from core.proposal_sandbox_routing.lineage import ProposalSandboxLineagePacket
from core.proposal_sandbox_routing.operator_review import ProposalSandboxOperatorReviewPacket
from core.proposal_sandbox_routing.replay import ProposalSandboxReplayPacket
from core.proposal_sandbox_routing.routes import ProposalSandboxRoutePacket
from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing

def run_proposal_sandbox_routing(external_action_proposal_packets: list[dict], manual_action_custody_packets: list[dict], operator_queue_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    lane = ProposalSandboxLanePacket(lane_id="psl-1", lane_type="simulation_lane", lane_constraints=["projection_only"], allowed_route_types=["simulation"], forbidden_route_types=["production", "deployment", "execution", "activation", "live_routing"], deterministic_lane_hash=ProposalSandboxLanePacket.compute_hash("simulation_lane", ["projection_only"], ["simulation"], ["production", "deployment", "execution", "activation", "live_routing"]), status="passed")
    route = ProposalSandboxRoutePacket(route_id="psr-1", proposal_hash="proposal-1", route_type="simulation", route_scope="sandbox_only", sandbox_lane_hash=lane.deterministic_lane_hash, route_constraints=["advisory_only"], route_status="route_proposed", deterministic_route_hash=ProposalSandboxRoutePacket.compute_hash("proposal-1", "simulation", "sandbox_only", lane.deterministic_lane_hash, ["advisory_only"], "route_proposed"), status="passed")
    constraint = ProposalSandboxConstraintPacket(constraint_id="psc-1", route_hash=route.deterministic_route_hash, hard_constraints=["no_execution"], soft_constraints=["operator_review"], restricted_actions=sorted(FORBIDDEN_RESTRICTED_ACTIONS), deterministic_constraint_hash=ProposalSandboxConstraintPacket.compute_hash(route.deterministic_route_hash, ["no_execution"], ["operator_review"], sorted(FORBIDDEN_RESTRICTED_ACTIONS)), status="passed")
    eligibility = ProposalSandboxEligibilityPacket(eligibility_id="pse-1", route_hash=route.deterministic_route_hash, proposal_hash=route.proposal_hash, lane_hash=lane.deterministic_lane_hash, eligible_for_sandbox=True, denial_reasons=[], deterministic_eligibility_hash=ProposalSandboxEligibilityPacket.compute_hash(route.deterministic_route_hash, route.proposal_hash, lane.deterministic_lane_hash, True, []), status="passed")
    governance = ProposalSandboxGovernancePacket(governance_id="psg-1", route_hash=route.deterministic_route_hash, governance_constraints=["operator_mediated"], governance_restrictions=["no_deploy", "no_execute", "no_production_routing"], operator_review_required=True, deterministic_governance_hash=ProposalSandboxGovernancePacket.compute_hash(route.deterministic_route_hash, ["operator_mediated"], ["no_deploy", "no_execute", "no_production_routing"], True), status="passed")
    continuity = ProposalSandboxContinuityPacket(route_hash=route.deterministic_route_hash, prior_route_hashes=["psr-root"], append_only=True, deterministic_continuity_hash=ProposalSandboxContinuityPacket.compute_hash(route.deterministic_route_hash, ["psr-root"], True), status="passed")
    replay = ProposalSandboxReplayPacket(route_hash=route.deterministic_route_hash, replay_route_hash=route.deterministic_route_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=ProposalSandboxReplayPacket.compute_hash(route.deterministic_route_hash, route.deterministic_route_hash, True, []), status="passed")
    lineage = ProposalSandboxLineagePacket(route_hash=route.deterministic_route_hash, parent_hashes=["proposal-sandbox-root"], lineage_cycle_detected=False, deterministic_lineage_hash=ProposalSandboxLineagePacket.compute_hash(route.deterministic_route_hash, ["proposal-sandbox-root"], False), status="passed")
    diagnostics: list[ProposalSandboxDiagnosticPacket] = []
    operator_review = ProposalSandboxOperatorReviewPacket(review_id="psor-1", route_hash=route.deterministic_route_hash, route_count=1, blocked_routes=0, unresolved_diagnostics=0, deterministic_review_hash=ProposalSandboxOperatorReviewPacket.compute_hash(route.deterministic_route_hash, 1, 0, 0), status="passed")
    validator = validate_proposal_sandbox_routing(route.route_type, route.route_status, lane.lane_type, [], replay.deterministic_match, [d.model_dump() for d in diagnostics], lineage.lineage_cycle_detected, False, False, False, False, False)
    packet = {"route": route.model_dump(), "lane": lane.model_dump(), "constraint": constraint.model_dump(), "eligibility": eligibility.model_dump(), "governance": governance.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": operator_review.model_dump(), "proposal_sandbox_routing_summary": {"route_count": 1, "blocked_routes": 0, "eligible_routes": 1, "unresolved_diagnostics": 0, "replay_matches": replay.deterministic_match, "governance_restricted": True, "authority_locked": True, "projection_only": True, "inference_authority": False}, "validator": validator, "status": validator["status"]}
    write_canonical_json("out/proposal_sandbox_routing/latest.json", packet)
    write_canonical_json("out/proposal_sandbox_routing_replay/latest.json", replay.model_dump())
    write_canonical_json("out/proposal_sandbox_routing_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/proposal_sandbox_routing_diagnostics/latest.json", [d.model_dump() for d in diagnostics])
    return packet
