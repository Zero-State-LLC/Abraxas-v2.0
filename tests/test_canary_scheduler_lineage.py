import pytest
from core.canary_scheduler.lineage import CanaryScheduleLineageNode, CanaryScheduleLineagePacket

def test_cyclic_lineage_fail_closed()->None:
    n=[CanaryScheduleLineageNode(schedule_hash='s',parent_hash='s',generation=1)]
    with pytest.raises(ValueError):
        CanaryScheduleLineagePacket(lineage_id='l',lineage_nodes=n,lineage_depth=1,deterministic_lineage_hash=CanaryScheduleLineagePacket.compute_hash(n),status='passed')
