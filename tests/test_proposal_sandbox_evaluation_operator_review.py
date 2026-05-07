from core.proposal_sandbox_evaluation.runtime import run_proposal_sandbox_evaluation

def test_operator_review_exists() -> None:
    p = run_proposal_sandbox_evaluation([], [], [], [])
    assert p["operator_review"]["evaluation_count"] == 1
