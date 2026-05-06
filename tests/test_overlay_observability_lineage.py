import pytest
from core.overlay_observability.lineage import OverlayObservabilityLineageNode, OverlayObservabilityLineagePacket

def test_cyclic_lineage_fail_closed()->None:
    n=[OverlayObservabilityLineageNode(fusion_hash='x',parent_hash='x',generation=1)]
    with pytest.raises(ValueError):
        OverlayObservabilityLineagePacket(lineage_id='l',lineage_nodes=n,lineage_depth=1,deterministic_lineage_hash=OverlayObservabilityLineagePacket.compute_hash(n),status='passed')
