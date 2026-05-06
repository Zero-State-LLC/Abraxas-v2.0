from core.overlay_topology.adjacency import OverlayAdjacencyPacket

def test_adjacency():
 p=OverlayAdjacencyPacket(adjacency_id='1',adjacent_overlays=0,shared_dependencies=0,shared_rollback_paths=0,shared_governance_events=0,adjacency_score=0.0,deterministic_adjacency_hash=OverlayAdjacencyPacket.compute_hash(0,0,0,0,0.0),status='passed')
 assert p.adjacency_score==0
