from core.proposal_sandbox_evaluation.restrictions import FORBIDDEN_ACTIONS

def test_forbidden_action_set() -> None:
    assert "execute" in FORBIDDEN_ACTIONS
