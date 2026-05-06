from core.overlay_topology.lineage import OverlayTopologyLineageNode, OverlayTopologyLineagePacket

def test_lineage_depth():
 n=OverlayTopologyLineageNode(graph_hash='a',generation=1)
 p=OverlayTopologyLineagePacket(lineage_id='1',lineage_nodes=[n],lineage_depth=1,deterministic_lineage_hash=OverlayTopologyLineagePacket.compute_hash([n]),status='passed')
 assert p.lineage_depth==1
