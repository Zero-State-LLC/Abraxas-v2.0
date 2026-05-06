from core.canary_scheduler.policies import CanaryPolicyPacket

def test_deterministic_policy_hashing()->None:
    h=CanaryPolicyPacket.compute_hash('shadow_only',0.3,0.7,1,True,False)
    assert h==CanaryPolicyPacket.compute_hash('shadow_only',0.3,0.7,1,True,False)
