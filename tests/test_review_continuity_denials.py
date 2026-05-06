from core.review_continuity.denials import ReviewDenialPacket

def test_denial_hash():
    h=ReviewDenialPacket.compute_hash('c','r','x')
    p=ReviewDenialPacket(denial_id='1',chain_hash='c',denial_reason='r',denial_code='x',deterministic_denial_hash=h,status='passed')
    assert p.deterministic_denial_hash==h
