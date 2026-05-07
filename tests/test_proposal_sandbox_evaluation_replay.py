from core.proposal_sandbox_evaluation.validators import validate_proposal_sandbox_evaluation

def test_replay_mismatch_fails() -> None:
    out = validate_proposal_sandbox_evaluation("evaluation_recorded", [], False, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
