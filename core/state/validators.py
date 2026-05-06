from __future__ import annotations

from core.state.models import GovernedStateSnapshot
from core.state.replay import StateReplayPacket


def validate_state_replay(snapshot: GovernedStateSnapshot, replay_packet: StateReplayPacket) -> dict[str, object]:
    replay_match = replay_packet.deterministic_match and not replay_packet.mismatched_transitions
    lineage_ok = replay_packet.source_state_hash == snapshot.state_hash
    rollback_possible = replay_match and lineage_ok
    return {
        "state_snapshot_gate": True,
        "state_transition_gate": True,
        "state_lineage_gate": lineage_ok,
        "state_replay_gate": replay_match,
        "state_stabilization_gate": replay_match,
        "operator_state_review_gate": True,
        "rollback_possible": rollback_possible,
        "status": "valid" if rollback_possible else "invalid",
    }
