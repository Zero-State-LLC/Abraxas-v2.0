from core.overlay_topology.coupling import OverlayCouplingPacket

def test_coupling_bounded():
 p=OverlayCouplingPacket(coupling_id='1',dependency_coupling=0.1,replay_coupling=0.1,risk_coupling=0.1,governance_coupling=0.1,aggregate_coupling_score=0.1,deterministic_coupling_hash=OverlayCouplingPacket.compute_hash(0.1,0.1,0.1,0.1,0.1,False,False),status='passed')
 assert 0<=p.aggregate_coupling_score<=1
