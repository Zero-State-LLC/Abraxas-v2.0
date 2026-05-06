import pytest

from core.drift.lineage import DriftLineageNode, DriftLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n=[DriftLineageNode(overlay_hash="a", generation=0), DriftLineageNode(overlay_hash="a", generation=1)]
    with pytest.raises(ValueError):
        DriftLineagePacket(lineage_id="l", lineage_depth=2, lineage_nodes=n, deterministic_lineage_hash=DriftLineagePacket.compute_hash(n))
