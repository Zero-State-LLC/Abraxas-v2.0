"""YGGDRASIL route graph validator."""

from __future__ import annotations

import json
from pathlib import Path

from core.file_cache import read_text_cached
from core.yggdrasil.models import YggdrasilRouteGraph

_ROUTE_GRAPH_CACHE: dict[str, tuple[str, YggdrasilRouteGraph]] = {}


def load_route_graph(path: str | Path) -> YggdrasilRouteGraph:
    """Load and validate a YGGDRASIL route graph from a JSON file."""
    target = Path(path)
    cache_key = target.resolve().as_posix()
    text = read_text_cached(target)
    cached = _ROUTE_GRAPH_CACHE.get(cache_key)
    if cached is not None and cached[0] == text:
        return cached[1].model_copy(deep=True)
    graph = YggdrasilRouteGraph.model_validate(json.loads(text))
    _ROUTE_GRAPH_CACHE[cache_key] = (text, graph)
    return graph.model_copy(deep=True)


def load_route_graphs(directory: str | Path) -> dict[str, YggdrasilRouteGraph]:
    """Load all route graphs from *directory*; return mapping of pipeline_id -> graph."""
    graphs: dict[str, YggdrasilRouteGraph] = {}
    for p in sorted(Path(directory).glob("*.json")):
        g = load_route_graph(p)
        graphs[g.pipeline_id] = g
    return graphs
