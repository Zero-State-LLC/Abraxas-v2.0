from core.spine.milestone_registry import MilestoneLineageNode, MilestoneRegistryPacket


def test_deterministic_milestone_registry_hashing() -> None:
    nodes=[MilestoneLineageNode(milestone_id="a", stabilization_hash="h", generation=0)]
    h=MilestoneRegistryPacket.compute_hash("a", ["a"], "h", nodes)
    assert h == MilestoneRegistryPacket.compute_hash("a", ["a"], "h", nodes)
