"""Tests for core/yggdrasil/traversal.py (HARDENING candidate f454e9339689fce4)"""

from core.yggdrasil.traversal import RuntimeRouteTraversal, traversal_hash, build_route_traversal
from core.yggdrasil.models import YggdrasilRouteGraph, YggdrasilNode, YggdrasilEdge, NodeType, EdgeType
from core.governance.authority import Authority

def _minimal_graph(pipeline_id: str = "p1") -> YggdrasilRouteGraph:
    nodes = [
        YggdrasilNode(node_id="n1", node_type=NodeType.subsystem, lane="default"),
        YggdrasilNode(node_id="n2", node_type=NodeType.subsystem, lane="default"),
    ]
    edges = [YggdrasilEdge(source="n1", target="n2", edge_type=EdgeType.depends_on)]
    return YggdrasilRouteGraph(pipeline_id=pipeline_id, nodes=nodes, edges=edges, authority=Authority())

def test_build_route_traversal_basic():
    graph = _minimal_graph()
    trav = build_route_traversal(graph)
    assert trav.schema_version == "RuntimeRouteTraversal.v1"
    assert trav.pipeline_id == "p1"
    assert "n1" in trav.visited_nodes
    assert any("n1->n2" in e for e in trav.traversed_edges)
    assert trav.status == "completed"

def test_traversal_hash_stable():
    graph = _minimal_graph("p-stable")
    trav = build_route_traversal(graph)
    h1 = traversal_hash(trav)
    h2 = traversal_hash(trav)
    assert h1 == h2
    assert len(h1) > 10

def test_authority_present():
    graph = _minimal_graph("p-auth")
    trav = build_route_traversal(graph)
    assert trav.authority is not None
    # Authority should be locked (all flags false)
    trav.authority.assert_locked()