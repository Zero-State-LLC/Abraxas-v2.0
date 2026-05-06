import pytest

from core.oracle.lineage import IntakeLineageNode, IntakeLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n=[IntakeLineageNode(intake_hash="a", generation=0), IntakeLineageNode(intake_hash="a", generation=1)]
    with pytest.raises(ValueError):
        IntakeLineagePacket(lineage_id="l", lineage_depth=2, lineage_nodes=n, deterministic_lineage_hash=IntakeLineagePacket.compute_hash(n))
