from core.overlay_topology.rollback_paths import OverlayRollbackPathPacket

def test_rollback_simulation_only():
 p=OverlayRollbackPathPacket(rollback_path_id='1',rollback_path_nodes=['a'],rollback_path_depth=1,rollback_dependency_count=1,rollback_path_risk=0.2,execution_claimed=False,status='passed')
 assert not p.execution_claimed
