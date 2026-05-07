from core.external_action_proposals.validators import validate_external_action_proposals

def test_forbidden_action_rejection() -> None:
    out = validate_external_action_proposals("proposed", "advisory", "deploy", True, [], False, False, False, False, False)
    assert out["status"] == "failed"
