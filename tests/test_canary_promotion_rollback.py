from core.canary_promotion.rollback import CanaryPromotionRollbackPacket

def test_rollback_deterministic()->None:
    h=CanaryPromotionRollbackPacket.compute_hash('c','r',True)
    assert h
