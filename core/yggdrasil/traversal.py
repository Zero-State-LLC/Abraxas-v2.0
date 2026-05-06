from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.models import YggdrasilRouteGraph


class RuntimeRouteTraversal(BaseModel):
    schema_version: Literal["RuntimeRouteTraversal.v1"] = "RuntimeRouteTraversal.v1"
    traversal_id: str
    pipeline_id: str
    route_graph_hash: str
    visited_nodes: list[str]
    traversed_edges: list[str]
    skipped_nodes: list[str]
    failed_nodes: list[str]
    traversal_order: list[str]
    authority: Authority
    status: Literal["completed", "partial", "failed", "not_computable"]


def traversal_hash(packet: RuntimeRouteTraversal) -> str:
    return canonical_hash(packet.model_dump(mode="json"))


def build_route_traversal(route_graph: YggdrasilRouteGraph) -> RuntimeRouteTraversal:
    nodes = sorted([n.node_id for n in route_graph.nodes])
    edges = sorted([f"{e.source}->{e.target}:{e.edge_type.value}" for e in route_graph.edges])
    body = {
        "pipeline_id": route_graph.pipeline_id,
        "route_graph_hash": canonical_hash(route_graph.model_dump(mode="json")),
        "visited_nodes": nodes,
        "traversed_edges": edges,
        "skipped_nodes": [],
        "failed_nodes": [],
        "traversal_order": nodes,
        "status": "completed",
    }
    traversal_id = canonical_hash(body)
    return RuntimeRouteTraversal(traversal_id=traversal_id, authority=Authority(), **body)
