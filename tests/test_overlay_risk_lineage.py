import pytest
from core.overlay_risk.lineage import OverlayRiskLineageNode, OverlayRiskLineagePacket


def test_lineage_cycle_fails() -> None:
    node = OverlayRiskLineageNode(risk_hash='x', parent_hash='x', generation=1)
    with pytest.raises(ValueError):
        OverlayRiskLineagePacket(lineage_id='1', lineage_nodes=[node], lineage_depth=1, deterministic_lineage_hash=OverlayRiskLineagePacket.compute_hash([node]), status='failed')
