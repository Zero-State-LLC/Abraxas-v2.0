from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.belief_graph.belief_graph_builder import build_belief_graph_packet
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraphRelationship
from core.belief_graph.theory_object import TheoryObject


def build_belief_graph_engine_packet(
    claims: list[ClaimObject | Mapping[str, Any]],
    *,
    evidence: Sequence[EvidenceObject | Mapping[str, Any]] = (),
    theories: Sequence[TheoryObject | Mapping[str, Any]] = (),
    relationships: Sequence[SignalGraphRelationship | Mapping[str, Any]] = (),
) -> dict[str, Any]:
    claim_models = [item if isinstance(item, ClaimObject) else ClaimObject.model_validate(item) for item in claims]
    graph = build_belief_graph_packet(
        claims=claim_models,
        evidence=evidence,
        theories=theories,
        relationships=relationships,
    )
    return {
        "schema_version": "BeliefGraphEnginePacket.v1",
        "status": "BELIEF_GRAPH_ENGINE_PACKET_EMITTED",
        "claim_count": len(claim_models),
        "graph": graph.model_dump(mode="json"),
        "advisory_only": True,
        "execution_authority": False,
        "truth_assignment": False,
    }
