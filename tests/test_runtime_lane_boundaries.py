from core.governance.authority import Authority
from core.yggdrasil.models import (
    AuthorityBoundary,
    EdgeType,
    NodeType,
    YggdrasilEdge,
    YggdrasilNode,
    YggdrasilRouteGraph,
)
from core.yggdrasil.runtime import build_execution_graph, validate_runtime_lane_boundaries
from core.yggdrasil.validator import load_route_graph


def test_lane_boundary_validation_callable() -> None:
    graph = build_execution_graph(load_route_graph("contracts/yggdrasil/routes/research_intake.route.v1.json"))
    ok, failures = validate_runtime_lane_boundaries(graph)
    assert isinstance(ok, bool)
    assert isinstance(failures, list)


def test_projection_authority_boundary_is_preserved_for_validation() -> None:
    route_graph = YggdrasilRouteGraph(
        pipeline_id="projection_boundary_regression",
        nodes=[
            YggdrasilNode(node_id="projection.node", node_type=NodeType.pipeline, lane="PROJECTION"),
            YggdrasilNode(node_id="shadow.node", node_type=NodeType.pipeline, lane="SHADOW"),
        ],
        edges=[
            YggdrasilEdge(
                source="projection.node",
                target="shadow.node",
                edge_type=EdgeType.routes_to,
                authority_boundary=AuthorityBoundary.runtime_boundary,
                validation_required=True,
            )
        ],
        authority=Authority(),
    )

    graph = build_execution_graph(route_graph)
    target = {node.node_id: node for node in graph.nodes}["shadow.node"]
    ok, failures = validate_runtime_lane_boundaries(graph)

    assert target.authority_boundary == "runtime_boundary"
    assert ok is False
    assert [failure.failure_type for failure in failures] == ["invalid_lane_crossing"]
