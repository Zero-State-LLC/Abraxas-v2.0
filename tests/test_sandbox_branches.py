from core.sandbox.branches import SandboxBranchPacket


def test_branch_hash_deterministic() -> None:
    assert SandboxBranchPacket.compute_hash("a", "b", 1) == SandboxBranchPacket.compute_hash("a", "b", 1)
