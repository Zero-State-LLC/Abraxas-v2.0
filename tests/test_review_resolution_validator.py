from core.review_resolution.validators import validate_review_resolution

def test_validator_fails_closed_on_critical_blocker():
    v = validate_review_resolution(True, False, False, False, [], [{'severity':'critical'}], False, False, False)
    assert v['status'] == 'failed'
