from core.sandbox.rollback import SandboxRollbackPacket


def test_rollback_hash_validation() -> None:
    h = SandboxRollbackPacket.compute_hash("b", "p", "r", True)
    p = SandboxRollbackPacket(rollback_id="r", branch_hash="b", rollback_possible=True, rollback_target_hash="p", rollback_reason="r", deterministic_rollback_hash=h)
    assert p.rollback_possible
