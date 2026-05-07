from core.proposal_sandbox_routing.constraints import FORBIDDEN_RESTRICTED_ACTIONS

def test_restricted_actions_set() -> None:
    assert "execute" in FORBIDDEN_RESTRICTED_ACTIONS
