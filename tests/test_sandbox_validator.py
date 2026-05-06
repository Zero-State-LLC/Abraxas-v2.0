from core.sandbox.branches import SandboxBranchPacket
from core.sandbox.replay import SandboxReplayPacket
from core.sandbox.validators import validate_sandbox_replay


def test_validator_catches_production_mutation_attempt() -> None:
    b = SandboxBranchPacket(branch_id="b", parent_state_hash="p", sandbox_state_hash="s", branch_generation=1, topology_hash="t")
    r = SandboxReplayPacket(replay_id="r", branch_hash="s", deterministic_match=True, replayed_mutations=["production_mutation"], mismatched_mutations=[])
    result = validate_sandbox_replay(b, r)
    assert result["status"] == "repair_required"
