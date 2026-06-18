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
