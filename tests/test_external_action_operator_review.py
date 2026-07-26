from core.external_action_proposals.runtime import run_external_action_proposals


def _stub() -> list[dict]:
    return [{"evidence": "e1"}]


def test_operator_review_projection_only() -> None:
    packet = run_external_action_proposals(_stub(), _stub(), _stub(), _stub(), _stub())
    assert packet["operator_review"]["projection_only"] is True
    assert packet["operator_review"]["inference_authority"] is False
