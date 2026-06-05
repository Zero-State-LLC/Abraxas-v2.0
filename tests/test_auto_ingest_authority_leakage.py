from core.ingest.auto_ingest_validation_pack import authority_leakage_scan, load_current_stack


def test_auto_ingest_authority_leakage() -> None:
    result = authority_leakage_scan(load_current_stack())
    assert result["status"] == "PASS_NO_FORBIDDEN_FIELDS"
    assert result["findings"] == []
