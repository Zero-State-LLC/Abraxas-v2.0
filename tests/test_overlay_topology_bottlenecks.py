from core.overlay_topology.bottlenecks import OverlayBottleneckPacket

def test_bottleneck_count():
 p=OverlayBottleneckPacket(bottleneck_id='1',high_degree_overlays=[],rollback_chokepoints=[],review_chokepoints=[],propagation_chokepoints=[],governance_ledger_bottlenecks=[],bottleneck_count=0,status='passed')
 assert p.bottleneck_count==0
