from core.sandbox.convergence import SandboxConvergencePacket


def test_convergence_deterministic() -> None:
    s = SandboxConvergencePacket.compute_score(4, 4, 1)
    assert s == SandboxConvergencePacket.compute_score(4, 4, 1)
