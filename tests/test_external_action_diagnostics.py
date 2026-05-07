from core.external_action_proposals.validators import validate_external_action_proposals

def test_critical_diagnostics_fail_closed() -> None:
    out = validate_external_action_proposals("proposed", "advisory", "review_operator", True, [{"severity":"critical", "resolved":False}], False, False, False, False, False)
    assert out["status"] == "failed"
