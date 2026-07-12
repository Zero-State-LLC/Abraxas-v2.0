"""Tests for core/yggdrasil/failures.py (HARDENING candidate 20447f34e3916d5f)"""

from core.yggdrasil.failures import RouteFailurePacket, FailureType
from core.governance.authority import Authority


def test_failure_packet():
    pkt = RouteFailurePacket(
        failure_id="f-001",
        graph_hash="abc123",
        node_id="node-1",
        failure_type="cycle_detected",
        severity="high",
        authority=Authority()
    )
    assert pkt.schema_version == "RouteFailurePacket.v1"
    assert pkt.failure_type == "cycle_detected"
    assert pkt.severity == "high"


def test_failure_types():
    assert "cycle_detected" in FailureType.__args__
    assert "replay_mismatch" in FailureType.__args__
