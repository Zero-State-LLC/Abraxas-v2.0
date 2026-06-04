from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority

FailureType = Literal[
    "cycle_detected",
    "invalid_lane_crossing",
    "unknown_node",
    "missing_dependency",
    "blocked_execution",
    "invalid_runtime_gate",
    "replay_mismatch",
    "cache_invalidated",
]


class RouteFailurePacket(BaseModel):
    schema_version: Literal["RouteFailurePacket.v1"] = "RouteFailurePacket.v1"
    failure_id: str
    graph_hash: str
    node_id: str | None = None
    edge_id: str | None = None
    failure_type: FailureType
    severity: Literal["low", "medium", "high", "critical"] = "high"
    authority: Authority
    status: Literal["failed", "not_computable"] = "failed"
    recommended_next_state: str = "hold"

    model_config = {"frozen": True}


def build_route_failure_packet(
    *,
    graph_hash: str,
    failure_type: FailureType,
    node_id: str | None = None,
    edge_id: str | None = None,
    severity: Literal["low", "medium", "high", "critical"] = "high",
    status: Literal["failed", "not_computable"] = "failed",
    recommended_next_state: str = "hold",
) -> RouteFailurePacket:
    body = {
        "graph_hash": graph_hash,
        "node_id": node_id,
        "edge_id": edge_id,
        "failure_type": failure_type,
        "severity": severity,
        "status": status,
        "recommended_next_state": recommended_next_state,
    }
    failure_id = canonical_hash(body)
    return RouteFailurePacket(failure_id=failure_id, authority=Authority(), **body)
