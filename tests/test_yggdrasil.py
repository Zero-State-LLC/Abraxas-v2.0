"""Tests for YGGDRASIL route graph models and validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.governance.authority import Authority
from core.yggdrasil.models import (
    AuthorityBoundary,
    EdgeType,
    NodeType,
    YggdrasilEdge,
    YggdrasilNode,
    YggdrasilRouteGraph,
)
from core.yggdrasil.validator import load_route_graph, load_route_graphs

ROUTES_DIR = Path("contracts/yggdrasil/routes")

TIER1_ROUTE_FILES = [
    "research_intake.route.v1.json",
    "universal_ingest.route.v1.json",
    "pse_forecast.route.v1.json",
    "outcome_brier.route.v1.json",
    "canon_sync.route.v1.json",
    "research_drop_validation.route.v1.json",
    "aal_viz_projection.route.v1.json",
]


@pytest.mark.parametrize("filename", TIER1_ROUTE_FILES)
def test_route_graph_loads(filename: str):
    graph = load_route_graph(ROUTES_DIR / filename)
    assert isinstance(graph, YggdrasilRouteGraph)
    assert graph.schema_version == "YggdrasilRouteGraph.v1"


def test_all_7_route_graphs_present():
    graphs = load_route_graphs(ROUTES_DIR)
    assert len(graphs) == 7


def test_route_graph_validates_edges():
    """Edge source/target must reference real nodes."""
    nodes = [
        YggdrasilNode(node_id="a", node_type=NodeType.pipeline, lane="SHADOW"),
        YggdrasilNode(node_id="b", node_type=NodeType.rune, lane="SHADOW"),
    ]
    edges = [
        YggdrasilEdge(source="a", target="b", edge_type=EdgeType.routes_to),
    ]
    graph = YggdrasilRouteGraph(
        pipeline_id="test",
        nodes=nodes,
        edges=edges,
        authority=Authority(),
    )
    assert graph.pipeline_id == "test"


def test_invalid_edge_source_raises():
    nodes = [
        YggdrasilNode(node_id="a", node_type=NodeType.pipeline, lane="SHADOW"),
    ]
    edges = [
        YggdrasilEdge(source="MISSING", target="a", edge_type=EdgeType.routes_to),
    ]
    with pytest.raises(Exception):
        YggdrasilRouteGraph(
            pipeline_id="test",
            nodes=nodes,
            edges=edges,
            authority=Authority(),
        )


def test_invalid_edge_target_raises():
    nodes = [
        YggdrasilNode(node_id="a", node_type=NodeType.pipeline, lane="SHADOW"),
    ]
    edges = [
        YggdrasilEdge(source="a", target="MISSING", edge_type=EdgeType.routes_to),
    ]
    with pytest.raises(Exception):
        YggdrasilRouteGraph(
            pipeline_id="test",
            nodes=nodes,
            edges=edges,
            authority=Authority(),
        )


def test_lane_boundary_requires_validation():
    """authority_boundary != 'none' must have validation_required=True."""
    with pytest.raises(Exception):
        YggdrasilEdge(
            source="a",
            target="b",
            edge_type=EdgeType.routes_to,
            authority_boundary=AuthorityBoundary.lane_crossing,
            validation_required=False,
        )


def test_no_boundary_no_validation_required_ok():
    edge = YggdrasilEdge(
        source="a",
        target="b",
        edge_type=EdgeType.routes_to,
        authority_boundary=AuthorityBoundary.none,
        validation_required=False,
    )
    assert edge.validation_required is False


def test_empty_nodes_raises():
    with pytest.raises(Exception):
        YggdrasilRouteGraph(
            pipeline_id="test",
            nodes=[],
            edges=[YggdrasilEdge(source="x", target="y", edge_type=EdgeType.routes_to)],
            authority=Authority(),
        )


def test_authority_locked_in_all_route_graphs():
    graphs = load_route_graphs(ROUTES_DIR)
    for _pid, graph in graphs.items():
        graph.authority.assert_locked()
