from core.yggdrasil.cache import build_route_cache, validate_route_cache
from core.yggdrasil.runtime import build_execution_graph
from core.yggdrasil.traversal import build_route_traversal
from core.yggdrasil.validator import load_route_graph


def test_route_cache_validates() -> None:
    rg = load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json")
    graph = build_execution_graph(rg)
    traversal = build_route_traversal(rg)
    cache = build_route_cache(graph, traversal)
    assert validate_route_cache(cache, graph)
