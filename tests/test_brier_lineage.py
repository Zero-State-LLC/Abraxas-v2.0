import pytest

from core.brier.lineage import BrierLineageNode, BrierLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n=[BrierLineageNode(score_hash="a", generation=0), BrierLineageNode(score_hash="a", generation=1)]
    with pytest.raises(ValueError):
        BrierLineagePacket(lineage_id="l", lineage_depth=2, lineage_nodes=n, deterministic_lineage_hash=BrierLineagePacket.compute_hash(n))
