from __future__ import annotations

from collections import defaultdict, deque
from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.runtime import ExecutionGraph, detect_cycles


class DeterministicGraphScheduler(BaseModel):
    schema_version: Literal["DeterministicGraphScheduler.v1"] = "DeterministicGraphScheduler.v1"
    scheduler_id: str
    graph_hash: str
    scheduled_nodes: list[str]
    skipped_nodes: list[str]
    blocked_nodes: list[str]
    execution_sequence: list[str]
    authority: Authority
    status: Literal["completed", "failed", "not_computable"]


def scheduler_hash(packet: DeterministicGraphScheduler) -> str:
    return canonical_hash(packet.model_dump(mode="json"))


def schedule_execution_graph(graph: ExecutionGraph) -> DeterministicGraphScheduler:
    if detect_cycles(graph):
        body = {
            "graph_hash": graph.topology_hash,
            "scheduled_nodes": [],
            "skipped_nodes": [],
            "blocked_nodes": sorted([n.node_id for n in graph.nodes]),
            "execution_sequence": [],
            "status": "failed",
        }
        return DeterministicGraphScheduler(scheduler_id=canonical_hash(body), authority=Authority(), **body)

    indeg = {n.node_id: len(n.dependencies) for n in graph.nodes}
    children: dict[str, list[str]] = defaultdict(list)
    for n in graph.nodes:
        for d in n.dependencies:
            children[d].append(n.node_id)
    q = deque(sorted([n for n, d in indeg.items() if d == 0]))
    seq: list[str] = []
    while q:
        cur = q.popleft()
        seq.append(cur)
        for nxt in sorted(children[cur]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)

    body = {
        "graph_hash": graph.topology_hash,
        "scheduled_nodes": seq,
        "skipped_nodes": [],
        "blocked_nodes": [],
        "execution_sequence": seq,
        "status": "completed",
    }
    return DeterministicGraphScheduler(scheduler_id=canonical_hash(body), authority=Authority(), **body)
