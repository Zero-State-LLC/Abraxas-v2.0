from core.overlay_topology.propagation import OverlayPropagationPathPacket

def test_propagation_no_prod_route():
 p=OverlayPropagationPathPacket(propagation_path_id='1',propagation_path_nodes=['a'],propagation_depth=1,propagation_score=0.2,blocked_propagation_routes=[],production_route_included=False,status='passed')
 assert not p.production_route_included
