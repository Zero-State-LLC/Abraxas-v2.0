from __future__ import annotations

# WP-D batch2: pure builder — publication via sole-writer scripts only.

import hashlib

from core.sandbox.branches import SandboxBranchPacket
from core.sandbox.convergence import SandboxConvergencePacket
from core.sandbox.lineage import SandboxLineageNode, SandboxLineagePacket
from core.sandbox.mutations import SandboxMutationProposal
from core.sandbox.operator_review import OperatorSandboxReviewPacket
from core.sandbox.replay import SandboxReplayPacket
from core.sandbox.rollback import SandboxRollbackPacket
from core.sandbox.stabilization import SandboxStabilizationPacket

def run_adaptive_sandbox(state_snapshot: dict, replay_packet: dict, topology_packet: dict, observability_packet: dict) -> dict:
    parent_hash = state_snapshot.get("state_hash", "unknown")
    topology_hash = topology_packet.get("topology_hash", "unknown")
    branch_hash = SandboxBranchPacket.compute_hash(parent_hash, topology_hash, 1)
    sandbox_state_hash = hashlib.sha256(f"sandbox|{branch_hash}".encode()).hexdigest()
    branch = SandboxBranchPacket(branch_id=f"branch:{branch_hash[:12]}", parent_state_hash=parent_hash, sandbox_state_hash=sandbox_state_hash, branch_generation=1, topology_hash=topology_hash, replay_hash=replay_packet.get("replay_hash"), branch_status="active")
    payload_hash = hashlib.sha256(observability_packet.get("telemetry_hash", "unknown").encode()).hexdigest()
    proposal = SandboxMutationProposal(proposal_id=f"proposal:{branch_hash[:12]}", branch_hash=branch_hash, mutation_type="stabilization_adjustment", mutation_payload_hash=payload_hash, deterministic_mutation_hash=SandboxMutationProposal.compute_hash(branch_hash, "stabilization_adjustment", payload_hash))
    replay = SandboxReplayPacket(replay_id=f"replay:{branch_hash[:12]}", branch_hash=branch_hash, deterministic_match=True, replayed_mutations=[proposal.proposal_id], mismatched_mutations=[])
    nodes = [SandboxLineageNode(branch_hash=parent_hash, generation=0), SandboxLineageNode(branch_hash=branch_hash, parent_hash=parent_hash, generation=1, proposal_hash=proposal.deterministic_mutation_hash)]
    lineage = SandboxLineagePacket(lineage_id=f"lineage:{branch_hash[:12]}", lineage_depth=2, lineage_nodes=nodes, deterministic_lineage_hash=SandboxLineagePacket.compute_hash(nodes), status="ok")
    convergence = SandboxConvergencePacket(convergence_id=f"convergence:{branch_hash[:12]}", branch_hash=branch_hash, compared_runs=1, deterministic_replays=1, divergence_events=0, convergence_score=SandboxConvergencePacket.compute_score(1, 1, 0))
    stabilization = SandboxStabilizationPacket(stabilization_id=f"stabilization:{branch_hash[:12]}", branch_hash=branch_hash, replay_match_count=1, replay_failure_count=0, stabilization_window=3, convergence_score=convergence.convergence_score, stabilization_state="stable")
    rollback = SandboxRollbackPacket(rollback_id=f"rollback:{branch_hash[:12]}", branch_hash=branch_hash, rollback_possible=True, rollback_target_hash=parent_hash, rollback_reason="operator_requested", deterministic_rollback_hash=SandboxRollbackPacket.compute_hash(branch_hash, parent_hash, "operator_requested", True))
    review = OperatorSandboxReviewPacket(review_id=f"review:{branch_hash[:12]}", branch_hash=branch_hash, pending_mutations=[proposal.proposal_id], stabilization_state=stabilization.stabilization_state, rollback_available=rollback.rollback_possible, convergence_score=convergence.convergence_score, operator_actions=["review_pending"])
    packet = {"branch": branch.model_dump(), "proposal": proposal.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "stabilization": stabilization.model_dump(), "convergence": convergence.model_dump(), "review": review.model_dump(), "rollback": rollback.model_dump()}
    return packet
