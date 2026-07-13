"""Tests for core/belief_graph/belief_graph_builder.py (HARDENING candidate 964e5aa2bfb65277)"""

from core.belief_graph.belief_graph_builder import build_belief_graph_packet

def test_build_belief_graph_packet_exists_and_callable():
    assert callable(build_belief_graph_packet)

def test_build_with_empty_inputs():
    # Should not crash on empty (implementation sorts and wraps)
    pkt = build_belief_graph_packet(
        claims=[],
        evidence=[],
        theories=[],
        relationships=[],
    )
    assert pkt is not None
