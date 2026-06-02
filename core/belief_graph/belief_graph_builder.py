from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraph, SignalGraphRelationship
from core.belief_graph.theory_object import TheoryObject


def _claim_model(item: ClaimObject | Mapping[str, Any]) -> ClaimObject:
    return item if isinstance(item, ClaimObject) else ClaimObject.model_validate(item)


def _evidence_model(item: EvidenceObject | Mapping[str, Any]) -> EvidenceObject:
    return item if isinstance(item, EvidenceObject) else EvidenceObject.model_validate(item)


def _theory_model(item: TheoryObject | Mapping[str, Any]) -> TheoryObject:
    return item if isinstance(item, TheoryObject) else TheoryObject.model_validate(item)


def _relationship_model(
    item: SignalGraphRelationship | Mapping[str, Any],
) -> SignalGraphRelationship:
    return (
        item
        if isinstance(item, SignalGraphRelationship)
        else SignalGraphRelationship.model_validate(item)
    )


def build_belief_graph_packet(
    *,
    claims: Sequence[ClaimObject | Mapping[str, Any]],
    evidence: Sequence[EvidenceObject | Mapping[str, Any]],
    theories: Sequence[TheoryObject | Mapping[str, Any]],
    relationships: Sequence[SignalGraphRelationship | Mapping[str, Any]],
    provenance: Mapping[str, Any] | None = None,
) -> BeliefGraphPacket:
    claim_models = tuple(sorted((_claim_model(item) for item in claims), key=lambda item: item.id))
    evidence_models = tuple(
        sorted((_evidence_model(item) for item in evidence), key=lambda item: item.hash)
    )
    theory_models = tuple(
        sorted((_theory_model(item) for item in theories), key=lambda item: item.id)
    )
    relationship_models = tuple(
        sorted(
            (_relationship_model(item) for item in relationships),
            key=lambda item: (
                item.source_type,
                item.source_ref,
                item.target_type,
                item.target_ref,
                item.relationship,
            ),
        )
    )
    signal_graph = SignalGraph(
        relationship_count=len(relationship_models),
        relationships=relationship_models,
    )
    return BeliefGraphPacket(
        claims=claim_models,
        evidence=evidence_models,
        theories=theory_models,
        signal_graph=signal_graph,
        provenance=dict(provenance or {}),
    )
