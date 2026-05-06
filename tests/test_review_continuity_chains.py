from core.review_continuity.chains import ReviewContinuityChainPacket

def test_chain_hash():
    h=ReviewContinuityChainPacket.compute_hash('r',['a'],['b'],['c'],['d'],'pending_continuity')
    p=ReviewContinuityChainPacket(chain_id='1',originating_request_hash='r',linked_review_hashes=['a'],linked_rationale_hashes=['b'],linked_governance_hashes=['c'],linked_firewall_hashes=['d'],chain_status='pending_continuity',deterministic_chain_hash=h,status='passed')
    assert p.deterministic_chain_hash==h
