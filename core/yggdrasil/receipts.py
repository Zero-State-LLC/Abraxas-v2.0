from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.cache import RouteCachePacket
from core.yggdrasil.runtime import ExecutionGraph
from core.yggdrasil.scheduler import DeterministicGraphScheduler, scheduler_hash
from core.yggdrasil.traversal import RuntimeRouteTraversal, traversal_hash


class YggdrasilExecutionReceipt(BaseModel):
    schema_version: Literal["YggdrasilExecutionReceipt.v1"] = "YggdrasilExecutionReceipt.v1"
    receipt_id: str
    graph_hash: str
    traversal_hash: str
    scheduler_hash: str
    execution_run_hash: str | None = None
    replay_hash: str | None = None
    cache_hash: str | None = None
    authority: Authority
    status: Literal["valid", "failed", "not_computable"]


def receipt_hash(receipt: YggdrasilExecutionReceipt) -> str:
    return canonical_hash(receipt.model_dump(mode="json"))


def build_yggdrasil_execution_receipt(graph: ExecutionGraph, traversal: RuntimeRouteTraversal, scheduler: DeterministicGraphScheduler, cache: RouteCachePacket | None = None) -> YggdrasilExecutionReceipt:
    g_hash = graph.topology_hash
    t_hash = traversal_hash(traversal)
    s_hash = scheduler_hash(scheduler)
    c_hash = cache.deterministic_cache_hash if cache else None
    status: Literal["valid", "failed", "not_computable"] = "valid" if g_hash else "not_computable"
    body = {"graph_hash": g_hash, "traversal_hash": t_hash, "scheduler_hash": s_hash, "cache_hash": c_hash, "status": status}
    rid = canonical_hash(body)
    return YggdrasilExecutionReceipt(receipt_id=rid, authority=Authority(), **body)
