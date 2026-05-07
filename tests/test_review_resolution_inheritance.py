from core.review_resolution.inheritance import ReviewResolutionInheritancePacket

def test_inheritance_packet():
    h = ReviewResolutionInheritancePacket.compute_hash('c',['d'],['f'],['r'],['b'])
    i = ReviewResolutionInheritancePacket(inheritance_id='1', continuity_hash='c', inherited_denials=['d'], inherited_deferrals=['f'], inherited_rationale_hashes=['r'], inherited_blockers=['b'], deterministic_inheritance_hash=h, status='passed')
    assert i.continuity_hash == 'c'
