from core.spine.milestone_validator import validate_active_milestone


def test_stale_milestone_labels_fail_validation() -> None:
    result = validate_active_milestone({"active_milestone": "v2.0.8"}, {"stabilized_milestones": ["v2.0.9"], "milestone_lineage": [{"milestone_id": "v2.0.9"}]})
    assert result["status"] == "failed"


def test_missing_stabilization_artifacts_not_computable() -> None:
    result = validate_active_milestone({"active_milestone": "x"}, {"stabilized_milestones": []})
    assert result["status"] == "not_computable"
