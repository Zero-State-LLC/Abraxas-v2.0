from core.oracle_signal import build_oracle_signal_processing_packet, normalize_candidate_signal


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
