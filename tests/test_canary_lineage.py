import pytest
from core.canary.lineage import CanaryLineageNode, CanaryLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n = [CanaryLineageNode(overlay_hash="a", parent_hash="a", generation=1)]
    with pytest.raises(ValueError):
        CanaryLineagePacket(lineage_id="l", lineage_nodes=n, lineage_depth=1, deterministic_lineage_hash=CanaryLineagePacket.compute_hash(n), status="passed")
