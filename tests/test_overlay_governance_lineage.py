import pytest

from core.overlay_governance.lineage import OverlayGovernanceLineageNode, OverlayGovernanceLineagePacket


def test_lineage_cycle_fail_closed() -> None:
    node = OverlayGovernanceLineageNode(ledger_hash="a", parent_hash="a", generation=1)
    with pytest.raises(ValueError):
        OverlayGovernanceLineagePacket(lineage_id="1", lineage_nodes=[node], lineage_depth=1, deterministic_lineage_hash=OverlayGovernanceLineagePacket.compute_hash([node]), status="failed")
