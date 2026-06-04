from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class GraphReplayPacket(BaseModel):
    schema_version: Literal["GraphReplayPacket.v1"] = "GraphReplayPacket.v1"
    replay_id: str
    source_graph_hash: str
    replay_graph_hash: str
    traversal_match: bool
    scheduler_match: bool
    receipt_match: bool
    mismatched_nodes: list[str]
    mismatched_edges: list[str]
    authority: Authority
    status: Literal["passed", "failed", "not_computable"]


def graph_replay_hash(packet: GraphReplayPacket) -> str:
    return canonical_hash(packet.model_dump(mode="json"))


def build_graph_replay_packet(source_run: dict[str, Any], replay_run: dict[str, Any]) -> GraphReplayPacket:
    source_graph_hash = source_run["graph"]["topology_hash"]
    replay_graph_hash = replay_run["graph"]["topology_hash"]
    traversal_match = source_run["traversal"]["traversal_id"] == replay_run["traversal"]["traversal_id"]
    scheduler_match = source_run["scheduler"]["scheduler_id"] == replay_run["scheduler"]["scheduler_id"]
    receipt_match = source_run["receipt"]["receipt_id"] == replay_run["receipt"]["receipt_id"]
    mismatched_nodes = [] if traversal_match else sorted(set(source_run["traversal"]["traversal_order"]) ^ set(replay_run["traversal"]["traversal_order"]))
    mismatched_edges = []
    status: Literal["passed", "failed", "not_computable"] = "passed" if (traversal_match and scheduler_match and receipt_match and source_graph_hash == replay_graph_hash) else "failed"
    body = {
        "source_graph_hash": source_graph_hash,
        "replay_graph_hash": replay_graph_hash,
        "traversal_match": traversal_match,
        "scheduler_match": scheduler_match,
        "receipt_match": receipt_match,
        "mismatched_nodes": mismatched_nodes,
        "mismatched_edges": mismatched_edges,
        "status": status,
    }
    return GraphReplayPacket(replay_id=canonical_hash(body), authority=Authority(), **body)
