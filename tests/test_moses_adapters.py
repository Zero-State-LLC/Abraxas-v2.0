from __future__ import annotations

from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.signal_graph import SignalGraph
from core.belief_graph.theory_object import TheoryObject
from core.moses.adapters import meaning_packet_from_belief_graph
from core.moses.contracts import MeaningStatus


def _packet(*, claims=(), theories=()) -> BeliefGraphPacket:
    return BeliefGraphPacket(
        claims=claims,
        theories=theories,
        signal_graph=SignalGraph(relationships=()),
        provenance={"fixture": "moses-adapter"},
    )


def test_adapter_preserves_observed_and_inferred_claims_without_promoting() -> None:
    packet = _packet(
        claims=(
            ClaimObject(
                id="c-observed",
                statement="Observed signal",
                provenance={"source": "fixture"},
                confidence=0.9,
                status="OBSERVED",
            ),
            ClaimObject(
                id="c-inferred",
                statement="Possible meaning",
                provenance={"source": "fixture"},
                confidence=0.6,
                status="INFERRED",
            ),
        )
    )
    meaning = meaning_packet_from_belief_graph(
        packet,
        meaning_id="meaning-001",
        semantic_invariants=("preserve-intent",),
    )
    assert meaning.status == MeaningStatus.provisional
    assert meaning.observations[0]["claim_id"] == "c-observed"
    assert meaning.interpretations[0]["claim_id"] == "c-inferred"
    assert meaning.semantic_invariants == ("preserve-intent",)


def test_adapter_fails_closed_to_not_computable_from_upstream_claim() -> None:
    packet = _packet(
        claims=(
            ClaimObject(
                id="c-unknown",
                statement="Insufficient evidence",
                provenance={"source": "fixture"},
                confidence="NOT_COMPUTABLE",
                status="NOT_COMPUTABLE",
            ),
        )
    )
    meaning = meaning_packet_from_belief_graph(packet, meaning_id="meaning-002")
    assert meaning.status == MeaningStatus.not_computable
    assert meaning.uncertainty == ("claim:c-unknown:NOT_COMPUTABLE",)


def test_adapter_marks_explicit_theory_conflict_contradicted() -> None:
    claims = (
        ClaimObject(
            id="c-1",
            statement="Claim one",
            provenance={"source": "fixture"},
            confidence=0.8,
            status="INFERRED",
        ),
        ClaimObject(
            id="c-2",
            statement="Claim two",
            provenance={"source": "fixture"},
            confidence=0.7,
            status="INFERRED",
        ),
    )
    theory = TheoryObject(
        id="t-1",
        supporting_claims=("c-1",),
        conflicting_claims=("c-2",),
    )
    meaning = meaning_packet_from_belief_graph(
        _packet(claims=claims, theories=(theory,)),
        meaning_id="meaning-003",
    )
    assert meaning.status == MeaningStatus.contradicted
    assert "c-2" in meaning.contradictions[0]
