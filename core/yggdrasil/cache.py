from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.runtime import ExecutionGraph
from core.yggdrasil.traversal import RuntimeRouteTraversal


class RouteCachePacket(BaseModel):
    schema_version: Literal["RouteCachePacket.v1"] = "RouteCachePacket.v1"
    cache_id: str
    graph_hash: str
    traversal_hash: str
    cached_routes: list[dict[str, Any]]
    deterministic_cache_hash: str
    authority: Authority
    status: Literal["valid", "invalid"]


def route_cache_hash(cache: RouteCachePacket) -> str:
    return canonical_hash(cache.model_dump(mode="json"))


def build_route_cache(graph: ExecutionGraph, traversal: RuntimeRouteTraversal) -> RouteCachePacket:
    routes = [{"node_id": node, "position": i} for i, node in enumerate(traversal.traversal_order)]
    base = {"graph_hash": graph.topology_hash, "traversal_hash": traversal.traversal_id, "cached_routes": routes}
    d_hash = canonical_hash(base)
    return RouteCachePacket(cache_id=d_hash, graph_hash=graph.topology_hash, traversal_hash=traversal.traversal_id, cached_routes=routes, deterministic_cache_hash=d_hash, authority=Authority(), status="valid")


def validate_route_cache(cache: RouteCachePacket, graph: ExecutionGraph) -> bool:
    if cache.graph_hash != graph.topology_hash:
        return False
    expected = canonical_hash({"graph_hash": cache.graph_hash, "traversal_hash": cache.traversal_hash, "cached_routes": cache.cached_routes})
    return expected == cache.deterministic_cache_hash
