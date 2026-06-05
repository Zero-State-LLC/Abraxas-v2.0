from core.ingest.auto_ingest_validation_pack import validate_empty_queue_behavior


def test_auto_ingest_empty_inputs() -> None:
    result = validate_empty_queue_behavior()
    assert result["status"] == "PASS"
    assert result["candidate_status"] == "NOT_COMPUTABLE_CROSS_DOMAIN_EVIDENCE_REQUIRED"
