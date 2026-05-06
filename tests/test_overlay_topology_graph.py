from core.overlay_topology.graph import OverlayTopologyGraphPacket

def test_graph_hash():
 h=OverlayTopologyGraphPacket.compute_hash(['a'],[],1,0.0)
 p=OverlayTopologyGraphPacket(topology_graph_id='1',overlay_nodes=['a'],overlay_edges=[],graph_depth=1,graph_density=0.0,deterministic_graph_hash=h,status='passed')
 assert p.deterministic_graph_hash==h
