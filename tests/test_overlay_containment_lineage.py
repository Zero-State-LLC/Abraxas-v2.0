from core.overlay_containment.lineage import OverlayContainmentLineageNode, OverlayContainmentLineagePacket


def test_lineage_hash() -> None:
    n = OverlayContainmentLineageNode(policy_hash="h", generation=1)
    p = OverlayContainmentLineagePacket(lineage_id="l", lineage_nodes=[n], lineage_depth=1, deterministic_lineage_hash=OverlayContainmentLineagePacket.compute_hash([n]), status="passed")
    assert p.lineage_depth == 1
