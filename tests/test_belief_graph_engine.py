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
