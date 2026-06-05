from core.ingest.auto_ingest_validation_pack import build_auto_ingest_validation_pack


def test_auto_ingest_full_stack_replay() -> None:
    packet = build_auto_ingest_validation_pack()
    assert packet["evidence"]["full_stack_replay"]["status"] == "PASS"
    assert packet["check_results"]["schema_validation"] == "PASS"
