from core.oracle_signal import (
    build_oracle_signal_processing_packet,
    normalize_candidate_signal,
    physical_implementation_authorized,
)


def test_normalize_candidate_signal_requires_shadow_status() -> None:
    candidate = {
        "schema_version": "OracleCandidateSignalPacket.v1",
        "signal_id": "a" * 64,
        "signal_status": "CANDIDATE_SHADOW_ONLY",
        "payload_ref": "SOURCE_URI_ONLY_NO_FETCH",
        "source_ref": {
            "queue_entry_id": "b" * 64,
            "source_pull_receipt_id": "c" * 64,
            "source_uri": "file:///example",
        },
        "signal_hash": "d" * 64,
    }
    normalized = normalize_candidate_signal(candidate)
    assert normalized["execution_authority"] is False


def test_build_oracle_signal_processing_packet_emits_hash() -> None:
    packet = build_oracle_signal_processing_packet(source_root=".")
    assert packet["schema_version"] == "OracleSignalModule.v1"
    assert packet["packet_hash"]


def test_build_oracle_signal_processing_packet_consumes_authorization_record() -> None:
    packet = build_oracle_signal_processing_packet(source_root=".")
    assert "physical_implementation_authorized" in packet
    assert "source_authorization_record_hash" in packet
    assert packet["source_authorization_record_path"].endswith(
        "oracle_signal_physical_implementation_authorization_record_001.latest.json"
    )
    if physical_implementation_authorized("."):
        assert packet["status"] == (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_SHADOW_PROCESSING_PACKET_EMITTED"
        )
        assert packet["physical_implementation_authorized"] is True
        assert packet["source_authorization_record_hash"] != "NOT_COMPUTABLE"
        assert packet["execution_authority"] is False
        assert packet["valid_for_execution"] is False
    else:
        assert packet["status"] == "ORACLE_SIGNAL_PROCESSING_PACKET_EMITTED"
        assert packet["physical_implementation_authorized"] is False
