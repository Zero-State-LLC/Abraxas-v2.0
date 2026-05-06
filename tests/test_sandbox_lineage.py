import pytest

from core.sandbox.lineage import SandboxLineageNode, SandboxLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n = [SandboxLineageNode(branch_hash="a", generation=0), SandboxLineageNode(branch_hash="a", generation=1)]
    with pytest.raises(ValueError):
        SandboxLineagePacket(lineage_id="l", lineage_depth=2, lineage_nodes=n, deterministic_lineage_hash=SandboxLineagePacket.compute_hash(n))
