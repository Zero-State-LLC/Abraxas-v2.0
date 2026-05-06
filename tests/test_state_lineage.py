import pytest
from core.state.lineage import StateLineageNode, StateLineagePacket


def test_cyclic_lineage_fail_closed():
    nodes = [StateLineageNode(state_hash="a", parent_hash="b", generation=0), StateLineageNode(state_hash="b", parent_hash="a", generation=1)]
    with pytest.raises(ValueError):
        StateLineagePacket(lineage_id="l1", lineage_depth=2, lineage_nodes=nodes, deterministic_lineage_hash=StateLineagePacket.compute_hash(nodes))
