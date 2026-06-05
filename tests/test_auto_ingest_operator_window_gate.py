from core.ingest.auto_ingest_validation_pack import validate_scheduler_gates


def test_auto_ingest_operator_window_gate() -> None:
    result = validate_scheduler_gates()
    assert result["status"] == "PASS"
    assert result["operator_window_decision"] == "SKIP_OPERATOR_WINDOW_REQUIRED"
    assert result["cooldown_decision"] == "SKIP_COOLDOWN_ACTIVE"
