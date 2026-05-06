from core.yggdrasil.runtime import build_execution_graph, validate_runtime_lane_boundaries
from core.yggdrasil.validator import load_route_graph


def test_lane_boundary_validation_callable() -> None:
    graph = build_execution_graph(load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json"))
    ok, failures = validate_runtime_lane_boundaries(graph)
    assert isinstance(ok, bool)
    assert isinstance(failures, list)
