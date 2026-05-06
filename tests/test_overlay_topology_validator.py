from core.overlay_topology.coupling import OverlayCouplingPacket
from core.overlay_topology.graph import OverlayTopologyGraphPacket
from core.overlay_topology.propagation import OverlayPropagationPathPacket
from core.overlay_topology.replay import OverlayTopologyReplayPacket
from core.overlay_topology.rollback_paths import OverlayRollbackPathPacket
from core.overlay_topology.validators import validate_overlay_topology

def test_validator_fail_replay():
 g=OverlayTopologyGraphPacket(topology_graph_id='1',overlay_nodes=['a'],overlay_edges=[],graph_depth=1,graph_density=0.0,deterministic_graph_hash=OverlayTopologyGraphPacket.compute_hash(['a'],[],1,0.0),status='passed')
 c=OverlayCouplingPacket(coupling_id='1',dependency_coupling=0.1,replay_coupling=0.1,risk_coupling=0.1,governance_coupling=0.1,aggregate_coupling_score=0.1,deterministic_coupling_hash=OverlayCouplingPacket.compute_hash(0.1,0.1,0.1,0.1,0.1,False,False),status='passed')
 r=OverlayRollbackPathPacket(rollback_path_id='1',rollback_path_nodes=['a'],rollback_path_depth=1,rollback_dependency_count=1,rollback_path_risk=0.1,execution_claimed=False,status='passed')
 p=OverlayPropagationPathPacket(propagation_path_id='1',propagation_path_nodes=['a'],propagation_depth=1,propagation_score=0.1,blocked_propagation_routes=[],production_route_included=False,status='passed')
 rep=OverlayTopologyReplayPacket(replay_id='1',source_graph_hash='a',replay_graph_hash='b',deterministic_match=False,mismatched_components=['x'],status='failed')
 assert validate_overlay_topology(g,c,r,p,rep,[])['status']=='failed'
