from core.observability.replay_metrics import build_replay_telemetry_packet


def test_replay_packet_match_no_mismatch() -> None:
    pkt = build_replay_telemetry_packet({"receipt": {"receipt_id": "r"}}, {"status": "passed", "replay_id": "x"})
    assert pkt.deterministic_match is True
    assert pkt.mismatched_receipts == []
