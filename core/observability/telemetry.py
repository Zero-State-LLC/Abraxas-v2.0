from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class ExecutionTelemetryPacket(BaseModel):
    schema_version: Literal["ExecutionTelemetryPacket.v1"] = "ExecutionTelemetryPacket.v1"
    telemetry_id: str
    execution_run_hash: str
    graph_hash: str
    traversal_hash: str
    scheduler_hash: str
    replay_hash: str | None = None
    receipt_chain_hash: str
    executed_node_count: int
    blocked_node_count: int
    failed_node_count: int
    deterministic_match: bool
    authority: Authority
    status: Literal["valid", "failed", "not_computable"]


def build_execution_telemetry_packet(runtime_run: dict, replay_packet: dict | None = None) -> ExecutionTelemetryPacket:
    replay_hash = replay_packet.get("replay_id") if replay_packet else None
    deterministic_match = bool(replay_packet is None or replay_packet.get("status") == "passed")
    scheduler = runtime_run.get("scheduler", {})
    failures = runtime_run.get("failures", [])
    body = {
        "execution_run_hash": runtime_run.get("run_id", ""),
        "graph_hash": runtime_run.get("graph", {}).get("topology_hash", ""),
        "traversal_hash": runtime_run.get("traversal", {}).get("traversal_id", ""),
        "scheduler_hash": scheduler.get("scheduler_id", ""),
        "replay_hash": replay_hash,
        "receipt_chain_hash": runtime_run.get("receipt", {}).get("receipt_id", ""),
        "executed_node_count": len(scheduler.get("execution_sequence", [])),
        "blocked_node_count": len(scheduler.get("blocked_nodes", [])),
        "failed_node_count": len(failures),
        "deterministic_match": deterministic_match,
        "status": "valid" if deterministic_match else "failed",
    }
    t_id = canonical_hash(body)
    return ExecutionTelemetryPacket(telemetry_id=t_id, authority=Authority(), **body)
