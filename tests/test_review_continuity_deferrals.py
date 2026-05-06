from core.review_continuity.deferrals import ReviewDeferralPacket

def test_deferral_hash():
    h=ReviewDeferralPacket.compute_hash('c','r','x')
    p=ReviewDeferralPacket(deferral_id='1',chain_hash='c',deferral_reason='r',deferral_code='x',deterministic_deferral_hash=h,status='passed')
    assert p.deterministic_deferral_hash==h
