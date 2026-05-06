from core.state.rollback import StateRollbackPacket


def test_rollback_hash():
    h = StateRollbackPacket.compute_hash("a", "b", "r", True)
    p = StateRollbackPacket(rollback_id="r1", source_state_hash="a", target_state_hash="b", rollback_reason="r", rollback_possible=True, deterministic_rollback_hash=h)
    assert p.rollback_possible
