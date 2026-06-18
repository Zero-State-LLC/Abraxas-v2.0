from core.belief_graph.claim_object import ClaimObject
from core.belief_graph_engine import build_belief_graph_engine_packet


def test_belief_graph_engine_packet() -> None:
    claim = ClaimObject(
        id="claim-1",
        statement="observed signal",
        provenance={"source": "test"},
        evidence_refs=(),
        confidence=0.5,
        status="OBSERVED",
    )
    packet = build_belief_graph_engine_packet([claim])
    assert packet["claim_count"] == 1
    assert packet["truth_assignment"] is False
    assert packet["advisory_only"] is True
    assert packet["execution_authority"] is False


def test_belief_graph_engine_fixture_graph_is_non_empty() -> None:
    claims = [
        ClaimObject(
            id="claim-a",
            statement="market drift observed",
            provenance={"source": "fixture"},
            evidence_refs=(),
            confidence=0.7,
            status="OBSERVED",
        ),
        ClaimObject(
            id="claim-b",
            statement="operator review pending",
            provenance={"source": "fixture"},
            evidence_refs=(),
            confidence=0.4,
            status="INFERRED",
        ),
    ]
    packet = build_belief_graph_engine_packet(claims)
    graph = packet["graph"]

    assert packet["claim_count"] == 2
    assert graph["claims"]
    assert len(graph["claims"]) == 2
    assert graph["claims"][0]["id"] == "claim-a"
    assert packet["status"] == "BELIEF_GRAPH_ENGINE_PACKET_EMITTED"
    assert packet["truth_assignment"] is False
    assert packet["execution_authority"] is False


def test_belief_graph_engine_fixture_graph_with_theory_and_relationship() -> None:
    from core.belief_graph.belief_graph_builder import build_belief_graph_packet
    from core.belief_graph.evidence_object import EvidenceObject
    from core.belief_graph.signal_graph import SignalGraphRelationship
    from core.belief_graph.theory_object import TheoryObject

    claims = [
        ClaimObject(
            id="claim-a",
            statement="market drift observed",
            provenance={"source": "fixture"},
            evidence_refs=("evidence-1",),
            confidence=0.7,
            status="OBSERVED",
        ),
        ClaimObject(
            id="claim-b",
            statement="operator review pending",
            provenance={"source": "fixture"},
            evidence_refs=(),
            confidence=0.4,
            status="INFERRED",
        ),
    ]
    evidence = [
        EvidenceObject(
            source="fixture",
            provenance={"source": "fixture"},
            timestamp="2026-06-18T00:00:00Z",
            evidence_type="observation",
            hash="evidence-1",
        ),
    ]
    theories = [
        TheoryObject(
            id="theory-1",
            supporting_claims=("claim-a",),
            conflicting_claims=("claim-b",),
            evidence_refs=("evidence-1",),
        ),
    ]
    relationships = [
        SignalGraphRelationship(
            source_ref="claim-a",
            source_type="claim",
            target_ref="evidence-1",
            target_type="evidence",
            relationship="supported_by",
        ),
    ]
    graph = build_belief_graph_packet(
        claims=claims,
        evidence=evidence,
        theories=theories,
        relationships=relationships,
    )

    assert len(graph.theories) == 1
    assert len(graph.evidence) == 1
    assert graph.signal_graph.relationship_count == 1

    engine_packet = build_belief_graph_engine_packet(
        [
            ClaimObject(
                id="claim-c",
                statement="advisory-only engine surface",
                provenance={"source": "fixture"},
                evidence_refs=(),
                confidence=0.5,
                status="OBSERVED",
            ),
        ]
    )
    assert engine_packet["claim_count"] == 1
    assert engine_packet["truth_assignment"] is False
    assert engine_packet["execution_authority"] is False
