from core.ingest.auto_ingest_validation_pack import run_12_invariance


def test_auto_ingest_12_run_invariance() -> None:
    result = run_12_invariance()
    assert result["status"] == "PASS_12_OF_12"
    assert result["unique_hash_count"] == 1
