import pytest
from core.canary_promotion.lineage import CanaryPromotionLineageNode, CanaryPromotionLineagePacket

def test_cyclic_lineage_fail_closed()->None:
    n=[CanaryPromotionLineageNode(candidate_hash='c',parent_hash='c',generation=1)]
    with pytest.raises(ValueError):
        CanaryPromotionLineagePacket(lineage_id='l',lineage_nodes=n,lineage_depth=1,deterministic_lineage_hash=CanaryPromotionLineagePacket.compute_hash(n),status='passed')
