from core.proposal_sandbox_evaluation.validators import validate_proposal_sandbox_evaluation

def test_lineage_cycle_fails() -> None:
    out = validate_proposal_sandbox_evaluation("evaluation_recorded", [], True, [], True, False, False, False, False, False)
    assert out["status"] == "failed"
