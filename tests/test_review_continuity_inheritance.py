from core.review_continuity.inheritance import ReviewRationaleInheritancePacket

def test_inheritance_hash():
    h=ReviewRationaleInheritancePacket.compute_hash('p',['c'],[],[],['g'])
    p=ReviewRationaleInheritancePacket(inheritance_id='1',parent_rationale_hash='p',inherited_constraints=['c'],inherited_denials=[],inherited_deferrals=[],inherited_governance_flags=['g'],deterministic_inheritance_hash=h,status='passed')
    assert p.deterministic_inheritance_hash==h
