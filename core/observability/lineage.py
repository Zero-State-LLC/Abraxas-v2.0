from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class LineageTraceNode(BaseModel):
    node_id: str
    node_type: str
    source_hash: str
    parent_hash: str | None = None
    generation: int


class LineageTracePacket(BaseModel):
    schema_version: Literal["LineageTracePacket.v1"] = "LineageTracePacket.v1"
    trace_id: str
    execution_hash: str
    nodes: list[LineageTraceNode]
    lineage_depth: int
    deterministic_chain_hash: str
    authority: Authority
    status: Literal["valid", "failed", "not_computable"]


def build_lineage_trace_packet(runtime_run: dict) -> LineageTracePacket:
    seq = runtime_run.get("scheduler", {}).get("execution_sequence", [])
    nodes: list[LineageTraceNode] = []
    parent = None
    for i, node_id in enumerate(seq):
        node_hash = canonical_hash({"node_id": node_id, "i": i})
        nodes.append(LineageTraceNode(node_id=node_id, node_type="runtime_node", source_hash=node_hash, parent_hash=parent, generation=i))
        parent = node_hash
    chain_hash = canonical_hash([n.model_dump(mode="json") for n in nodes])
    body = {"execution_hash": runtime_run.get("run_id", ""), "nodes": nodes, "lineage_depth": len(nodes), "deterministic_chain_hash": chain_hash, "status": "valid"}
    trace_id = canonical_hash({"execution_hash": body["execution_hash"], "chain_hash": chain_hash})
    return LineageTracePacket(trace_id=trace_id, authority=Authority(), **body)
