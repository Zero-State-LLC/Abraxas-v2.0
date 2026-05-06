from core.canary_promotion.validators import validate_canary_promotion
from core.canary_promotion.runtime import run_canary_promotion_review
from core.canary_promotion.replay import CanaryPromotionReplayPacket

def test_replay_mismatch_blocks_eligibility()->None:
    out=run_canary_promotion_review([],[])
    c,e,rb=out['candidate'],out['eligibility'],out['rollback']
    rp=CanaryPromotionReplayPacket(replay_id='r',candidate_hash=c['deterministic_candidate_hash'],deterministic_match=False,mismatched_packets=['x'],status='failed')
    from core.canary_promotion.candidates import CanaryPromotionCandidatePacket
    from core.canary_promotion.eligibility import CanaryPromotionEligibilityPacket
    from core.canary_promotion.rollback import CanaryPromotionRollbackPacket
    assert validate_canary_promotion(CanaryPromotionCandidatePacket(**c),CanaryPromotionEligibilityPacket(**e),rp,CanaryPromotionRollbackPacket(**rb))['status']=='failed'
