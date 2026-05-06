from core.canary_promotion.candidates import CanaryPromotionCandidatePacket

def test_deterministic_candidate_hashing()->None:
    h=CanaryPromotionCandidatePacket.compute_hash('o','s','ob',0.9,1.0,True,True,'review_only')
    assert h==CanaryPromotionCandidatePacket.compute_hash('o','s','ob',0.9,1.0,True,True,'review_only')
