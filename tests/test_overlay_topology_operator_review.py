from core.overlay_topology.operator_review import OperatorOverlayTopologyReviewPacket

def test_review():
 p=OperatorOverlayTopologyReviewPacket(review_id='1',graph_density=0.1,bottleneck_count=0,critical_diagnostics=0,pending_actions=[],status='approved')
 assert p.status=='approved'
