from core.operator_queue.validators import validate_operator_queue

def test_validator_passes():
    result = validate_operator_queue("deny", True, [], False, False, False, False, False)
    assert result["status"] == "passed"
