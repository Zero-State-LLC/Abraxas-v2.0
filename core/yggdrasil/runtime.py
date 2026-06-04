from __future__ import annotations

from collections import defaultdict, deque
from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.failures import RouteFailurePacket, build_route_failure_packet
from core.yggdrasil.models import YggdrasilRouteGraph


class ExecutionGraphNode(BaseModel):
    node_id: str
    node_type: str
    execution_order: int
    dependencies: list[str]
    lane: str
    authority_boundary: str


class ExecutionGraphEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    edge_type: str
    validation_required: bool
    runtime_gate_required: bool


class ExecutionGraph(BaseModel):
    schema_version: Literal["ExecutionGraph.v1"] = "ExecutionGraph.v1"
    graph_id: str
    pipeline_id: str
    nodes: list[ExecutionGraphNode]
    edges: list[ExecutionGraphEdge]
    authority: Authority
    topology_hash: str
    status: Literal["completed", "failed", "not_computable"]


def execution_graph_hash(graph: ExecutionGraph) -> str:
    return canonical_hash(graph.model_dump(mode="json"))


def detect_cycles(graph: ExecutionGraph) -> bool:
    deps = {n.node_id: set(n.dependencies) for n in graph.nodes}
    indeg = {n.node_id: len(deps[n.node_id]) for n in graph.nodes}
    rev: dict[str, list[str]] = defaultdict(list)
    for n in graph.nodes:
        for d in n.dependencies:
            rev[d].append(n.node_id)
    q = deque(sorted([n for n, d in indeg.items() if d == 0]))
    visited = 0
    while q:
        cur = q.popleft()
        visited += 1
        for nxt in sorted(rev[cur]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return visited != len(graph.nodes)


def validate_runtime_lane_boundaries(graph: ExecutionGraph) -> tuple[bool, list[RouteFailurePacket]]:
    failures: list[RouteFailurePacket] = []
    by_id = {n.node_id: n for n in graph.nodes}
    for edge in graph.edges:
        src = by_id[edge.source]
        tgt = by_id[edge.target]
        if src.lane != tgt.lane and not edge.runtime_gate_required:
            failures.append(build_route_failure_packet(graph_hash=graph.topology_hash, edge_id=edge.edge_id, failure_type="invalid_runtime_gate"))
        if src.lane == "SHADOW" and tgt.lane == "FORECAST":
            failures.append(build_route_failure_packet(graph_hash=graph.topology_hash, edge_id=edge.edge_id, failure_type="invalid_lane_crossing", status="not_computable"))
        if src.lane == "PROJECTION" and tgt.authority_boundary != "none":
            failures.append(build_route_failure_packet(graph_hash=graph.topology_hash, edge_id=edge.edge_id, failure_type="invalid_lane_crossing"))
    return (len(failures) == 0, failures)


def build_execution_graph(route_graph: YggdrasilRouteGraph) -> ExecutionGraph:
    node_ids = {n.node_id for n in route_graph.nodes}
    deps: dict[str, list[str]] = {n.node_id: [] for n in route_graph.nodes}
    boundary_by_target: dict[str, set[str]] = {n.node_id: set() for n in route_graph.nodes}
    edges: list[ExecutionGraphEdge] = []
    for e in sorted(route_graph.edges, key=lambda x: (x.source, x.target, x.edge_type.value)):
        if e.source not in node_ids or e.target not in node_ids:
            status = "not_computable"
        deps[e.target].append(e.source)
        if e.authority_boundary.value != "none":
            boundary_by_target[e.target].add(e.authority_boundary.value)
        edges.append(ExecutionGraphEdge(edge_id=f"{e.source}->{e.target}:{e.edge_type.value}", source=e.source, target=e.target, edge_type=e.edge_type.value, validation_required=e.validation_required, runtime_gate_required=e.validation_required))
    nodes_sorted = sorted(route_graph.nodes, key=lambda n: n.node_id)
    nodes: list[ExecutionGraphNode] = []
    for idx, node in enumerate(nodes_sorted):
        boundaries = sorted(boundary_by_target[node.node_id])
        authority_boundary = boundaries[0] if boundaries else "none"
        nodes.append(ExecutionGraphNode(node_id=node.node_id, node_type=node.node_type.value, execution_order=idx, dependencies=sorted(deps[node.node_id]), lane=node.lane, authority_boundary=authority_boundary))
    graph_id = canonical_hash({"pipeline_id": route_graph.pipeline_id, "nodes": [n.node_id for n in nodes], "edges": [e.edge_id for e in edges]})
    status: Literal["completed", "failed", "not_computable"] = "completed"
    graph = ExecutionGraph(graph_id=graph_id, pipeline_id=route_graph.pipeline_id, nodes=nodes, edges=edges, authority=Authority(), topology_hash="", status=status)
    topology_hash = execution_graph_hash(graph)
    graph = graph.model_copy(update={"topology_hash": topology_hash})
    if detect_cycles(graph):
        graph = graph.model_copy(update={"status": "failed"})
    return graph
