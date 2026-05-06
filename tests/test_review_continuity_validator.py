from core.review_continuity.validators import validate_review_continuity

def test_review_continuity_validator_passes():
    r=validate_review_continuity(True,False,False,[],False,False,False,False)
    assert r['status']=='passed'
