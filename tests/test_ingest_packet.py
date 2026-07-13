"""Tests for core/ingest/ingest_packet.py (HARDENING candidate a538487115483fd6)"""

from core.ingest.ingest_packet import IngestPacket
from core.ingest.source_record import SourceRecord
from core.belief_graph.claim_object import ClaimObject

def test_ingest_packet_minimal():
    sr = SourceRecord(
        adapter_id="test_adapter",
        source_uri="file://test/data.json",
        source_type="json",
        observed_at="2026-07-12T00:00:00Z",
        content_type="application/json",
        sha256="a" * 64,
        size_bytes=123,
        payload={"key": "value"}
    )
    pkt = IngestPacket(adapter_id="test_adapter", source_record=sr)
    assert pkt.adapter_id == "test_adapter"
    assert pkt.schema_version == "IngestPacket.v1"
    assert len(pkt.claims) == 0

def test_ingest_packet_with_claims():
    sr = SourceRecord(
        adapter_id="a2",
        source_uri="file://test/claims.json",
        source_type="json",
        observed_at="2026-07-12T00:00:00Z",
        content_type="application/json",
        sha256="b" * 64,
        size_bytes=456
    )
    claim = ClaimObject(
        schema_version="ClaimObject.v1",
        id="c1",
        statement="test claim",
        provenance={"source": "test"},
        confidence=0.9,
        status="OBSERVED"
    )
    pkt = IngestPacket(adapter_id="a2", source_record=sr, claims=(claim,))
    assert len(pkt.claims) == 1
    assert pkt.claims[0].id == "c1"
