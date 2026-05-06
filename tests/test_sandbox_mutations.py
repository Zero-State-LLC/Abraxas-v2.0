from core.sandbox.mutations import SandboxMutationProposal


def test_mutation_hash_deterministic() -> None:
    h = SandboxMutationProposal.compute_hash("b", "scheduler_adjustment", "p")
    assert h == SandboxMutationProposal.compute_hash("b", "scheduler_adjustment", "p")
