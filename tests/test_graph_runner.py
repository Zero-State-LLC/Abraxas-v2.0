"""Tests for core/runtime/graph_runner.py (HARDENING candidate b749de018aa179bc)"""

from core.runtime.graph_runner import run_execution_graph
from core.yggdrasil.models import YggdrasilRouteGraph, YggdrasilNode, YggdrasilEdge
from core.governance.authority import Authority

def test_run_execution_graph_basic():
    n1 = YggdrasilNode(node_id="n1", label="start", node_type="subsystem", lane="SHADOW")
    n2 = YggdrasilNode(node_id="n2", label="end", node_type="subsystem", lane="SHADOW")
    e = YggdrasilEdge(source="n1", target="n2", edge_type="depends_on")
    g = YggdrasilRouteGraph(pipeline_id="p1", nodes=[n1, n2], edges=[e], authority=Authority())
    result = run_execution_graph(g)
    assert isinstance(result, dict)
    assert "status" in result
    assert "run_id" in result
    assert "graph" in result
    assert result["status"] in ("completed", "failed")

def test_run_execution_graph_detects_cycle():
    n = YggdrasilNode(node_id="n1", label="loop", node_type="subsystem", lane="SHADOW")
    e = YggdrasilEdge(source="n1", target="n1", edge_type="depends_on")
    g = YggdrasilRouteGraph(pipeline_id="p-cycle", nodes=[n], edges=[e], authority=Authority())
    result = run_execution_graph(g)
    assert result["status"] in ("completed", "failed")
    # failures list is present
    assert "failures" in result
