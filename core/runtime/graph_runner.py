from __future__ import annotations

from typing import Any

# WP-D4-C4: pure builder — sole-writer scripts own out/ publication.
from core.canonical.json import canonical_hash
from core.governance.authority import Authority
from core.yggdrasil.cache import build_route_cache
from core.yggdrasil.failures import RouteFailurePacket, build_route_failure_packet
from core.yggdrasil.models import YggdrasilRouteGraph
from core.yggdrasil.receipts import build_yggdrasil_execution_receipt
from core.yggdrasil.runtime import build_execution_graph, detect_cycles, validate_runtime_lane_boundaries
from core.yggdrasil.scheduler import schedule_execution_graph
from core.yggdrasil.traversal import build_route_traversal


def run_execution_graph(route_graph: YggdrasilRouteGraph) -> dict[str, Any]:
    graph = build_execution_graph(route_graph)
    failures: list[RouteFailurePacket] = []
    if detect_cycles(graph):
        failures.append(build_route_failure_packet(graph_hash=graph.topology_hash, failure_type="cycle_detected", status="not_computable"))
    boundaries_ok, boundary_failures = validate_runtime_lane_boundaries(graph)
    failures.extend(boundary_failures)
    scheduler = schedule_execution_graph(graph)
    traversal = build_route_traversal(route_graph)
    cache = build_route_cache(graph, traversal)
    receipt = build_yggdrasil_execution_receipt(graph, traversal, scheduler, cache)
    status = "completed" if not failures and boundaries_ok and scheduler.status == "completed" else "failed"
    return {
        "schema_version": "YggdrasilRuntimeRun.v1",
        "run_id": canonical_hash({"graph": graph.topology_hash, "traversal": traversal.traversal_id, "scheduler": scheduler.scheduler_id}),
        "pipeline_id": route_graph.pipeline_id,
        "route_graph": route_graph.model_dump(mode="json"),
        "graph": graph.model_dump(mode="json"),
        "traversal": traversal.model_dump(mode="json"),
        "scheduler": scheduler.model_dump(mode="json"),
        "cache": cache.model_dump(mode="json"),
        "receipt": receipt.model_dump(mode="json"),
        "failures": [f.model_dump(mode="json") for f in failures],
        "authority": Authority().model_dump(),
        "status": status,
    }
