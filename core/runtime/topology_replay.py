from __future__ import annotations

from typing import Any

# TD Wave 1: pure builder — sole-writer scripts own out/ publication.
from core.runtime.graph_runner import run_execution_graph
from core.yggdrasil.models import YggdrasilRouteGraph
from core.yggdrasil.replay import build_graph_replay_packet


def replay_execution_graph(runtime_run: dict[str, Any]) -> dict[str, Any]:
    route_graph = YggdrasilRouteGraph.model_validate(runtime_run["route_graph"])
    replay_run = run_execution_graph(route_graph)
    packet = build_graph_replay_packet(runtime_run, replay_run)
    return packet.model_dump(mode="json")
