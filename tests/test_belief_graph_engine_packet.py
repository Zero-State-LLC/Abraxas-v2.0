"""Phase 2 harness: BeliefGraphEnginePacket advisory emitter."""

from __future__ import annotations

from core.belief_graph import build_belief_graph_engine_packet
from core.canonical.json import canonical_dumps


def _claims():
    return [
        {
            "id": "claim-001",
            "statement": "Harness dry-run claim remains advisory.",
            "provenance": {"lane": "shadow"},
            "evidence_refs": ("ev-001",),
            "confidence": 0.5,
            "status": "OBSERVED",
        }
    ]


def _evidence():
    return [
        {
            "source": "phase2_harness",
            "provenance": {"lane": "shadow"},
            "timestamp": "2026-07-23T00:00:00Z",
            "evidence_type": "TEXT",
            "hash": "ev-001",
        }
    ]


def test_engine_packet_emits_advisory_envelope() -> None:
    packet = build_belief_graph_engine_packet(
        _claims(),
        evidence=_evidence(),
        theories=(),
        relationships=(),
    )
    assert packet["schema_version"] == "BeliefGraphEnginePacket.v1"
    assert packet["status"] == "BELIEF_GRAPH_ENGINE_PACKET_EMITTED"
    assert packet["claim_count"] == 1
    assert packet["advisory_only"] is True
    assert packet["execution_authority"] is False
    assert packet["truth_assignment"] is False
    assert "graph" in packet
    assert packet["graph"]["TRUTH_ASSIGNMENT"] is False
    assert packet["graph"]["EXECUTION_AUTHORITY"] is False


def test_engine_packet_is_deterministic() -> None:
    first = build_belief_graph_engine_packet(_claims(), evidence=_evidence())
    second = build_belief_graph_engine_packet(_claims(), evidence=_evidence())
    assert canonical_dumps(first) == canonical_dumps(second)
