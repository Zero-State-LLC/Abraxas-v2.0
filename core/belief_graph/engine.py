from __future__ import annotations

from typing import Any, Mapping

from core.belief_graph.belief_graph_builder import build_belief_graph_packet
from core.belief_graph.claim_object import ClaimObject


def build_belief_graph_engine_packet(
    claims: list[ClaimObject | Mapping[str, Any]],
) -> dict[str, Any]:
    claim_models = [item if isinstance(item, ClaimObject) else ClaimObject.model_validate(item) for item in claims]
    graph = build_belief_graph_packet(
        claims=claim_models,
        evidence=[],
        theories=[],
        relationships=[],
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
