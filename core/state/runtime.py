from __future__ import annotations

# WP-D batch2: pure builder — publication via sole-writer scripts only.
import hashlib

from core.observability.telemetry_hash import resolve_telemetry_hash
from core.state.lineage import StateLineageNode, StateLineagePacket
from core.state.models import GovernedStateSnapshot
from core.state.operator_review import OperatorStateReviewPacket
from core.state.rollback import StateRollbackPacket
from core.state.stabilization import StateStabilizationPacket
from core.state.transitions import StateTransitionPacket


def run_state_engine(
    execution_packet: dict,
    replay_packet: dict,
    telemetry_packet: dict,
    topology_packet: dict,
) -> dict:
    # out/telemetry/latest.json is ExecutionTelemetryPacket (telemetry_id), not
    # a top-level telemetry_hash. Resolve fail-closed so distinct telemetry
    # cannot collapse into "" / "unknown".
    telemetry_hash = resolve_telemetry_hash(telemetry_packet)
    state_hash = hashlib.sha256(
        f"{execution_packet.get('execution_hash', '')}|{topology_packet.get('topology_hash', '')}|{telemetry_hash}".encode()
    ).hexdigest()
    snapshot = GovernedStateSnapshot(
        snapshot_id=f"snapshot:{state_hash[:12]}",
        pipeline_id=execution_packet.get("pipeline_id", "unknown"),
        state_hash=state_hash,
        execution_hash=execution_packet.get("execution_hash", "unknown"),
        replay_hash=replay_packet.get("replay_hash"),
        topology_hash=topology_packet.get("topology_hash", "unknown"),
        telemetry_hash=telemetry_hash,
        stabilization_state="stabilizing",
        status="ok",
    )
    transition = StateTransitionPacket(
        transition_id=f"transition:{state_hash[:8]}", source_state_hash=execution_packet.get("prev_state_hash", "root"),
        target_state_hash=state_hash, triggering_execution_hash=snapshot.execution_hash, transition_type="replay_update",
        deterministic_transition_hash=StateTransitionPacket.compute_hash(execution_packet.get("prev_state_hash", "root"), state_hash, snapshot.execution_hash, "replay_update"), status="applied"
    )
    lineage_nodes = [
        StateLineageNode(state_hash=execution_packet.get("prev_state_hash", "root"), parent_hash=None, generation=0),
        StateLineageNode(state_hash=state_hash, parent_hash=execution_packet.get("prev_state_hash", "root"), generation=1, transition_hash=transition.deterministic_transition_hash),
    ]
    lineage = StateLineagePacket(lineage_id=f"lineage:{state_hash[:12]}", lineage_depth=2, lineage_nodes=lineage_nodes, deterministic_lineage_hash=StateLineagePacket.compute_hash(lineage_nodes), status="ok")
    stabilization = StateStabilizationPacket(stabilization_id=f"stab:{state_hash[:12]}", state_hash=state_hash, replay_match_count=1, replay_failure_count=0, stabilization_window=5, stabilization_state="stabilizing", status="ok")
    review = OperatorStateReviewPacket(review_id=f"review:{state_hash[:12]}", state_hash=state_hash, pending_transitions=[transition.transition_id], rollback_available=True, stabilization_state=stabilization.stabilization_state, operator_actions=["review_pending"], status="pending")
    rollback = StateRollbackPacket(rollback_id=f"rollback:{state_hash[:12]}", source_state_hash=state_hash, target_state_hash=execution_packet.get("prev_state_hash", "root"), rollback_reason="operator_requested", rollback_possible=True, deterministic_rollback_hash=StateRollbackPacket.compute_hash(state_hash, execution_packet.get("prev_state_hash", "root"), "operator_requested", True), status="ready")
    out = {"snapshot": snapshot.model_dump(), "transition": transition.model_dump(), "lineage": lineage.model_dump(), "stabilization": stabilization.model_dump(), "review": review.model_dump(), "rollback": rollback.model_dump()}
    return out
