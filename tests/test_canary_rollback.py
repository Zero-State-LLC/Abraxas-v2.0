from core.canary.rollback import CanaryRollbackPacket


def test_rollback_deterministic() -> None:
    h = CanaryRollbackPacket.compute_hash("o","r",1,True)
    p = CanaryRollbackPacket(rollback_id="r", overlay_hash="o", rollback_reason="r", rollback_generation=1, rollback_complete=True, deterministic_rollback_hash=h, status="passed")
    assert p.deterministic_rollback_hash == h
