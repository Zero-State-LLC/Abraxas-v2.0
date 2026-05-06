import pytest
from core.state.transitions import StateTransitionPacket


def test_transition_hash_stable():
    h = StateTransitionPacket.compute_hash("a", "b", "e", "replay_update")
    p = StateTransitionPacket(transition_id="t", source_state_hash="a", target_state_hash="b", triggering_execution_hash="e", transition_type="replay_update", deterministic_transition_hash=h)
    assert p.deterministic_transition_hash == h


def test_source_target_must_differ():
    h = StateTransitionPacket.compute_hash("a", "a", "e", "replay_update")
    with pytest.raises(ValueError):
        StateTransitionPacket(transition_id="t", source_state_hash="a", target_state_hash="a", triggering_execution_hash="e", transition_type="replay_update", deterministic_transition_hash=h)
