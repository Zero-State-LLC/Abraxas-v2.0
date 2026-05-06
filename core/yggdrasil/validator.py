"""YGGDRASIL route graph validator."""

from __future__ import annotations

import json
from pathlib import Path

from core.yggdrasil.models import YggdrasilRouteGraph


def load_route_graph(path: str | Path) -> YggdrasilRouteGraph:
    """Load and validate a YGGDRASIL route graph from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return YggdrasilRouteGraph.model_validate(data)


def load_route_graphs(directory: str | Path) -> dict[str, YggdrasilRouteGraph]:
    """Load all route graphs from *directory*; return mapping of pipeline_id -> graph."""
    graphs: dict[str, YggdrasilRouteGraph] = {}
    for p in sorted(Path(directory).glob("*.json")):
        g = load_route_graph(p)
        graphs[g.pipeline_id] = g
    return graphs
