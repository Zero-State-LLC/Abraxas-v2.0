from core.state.models import GovernedStateSnapshot
from core.state.replay import StateReplayPacket
from core.state.validators import validate_state_replay


def test_validator_catches_mismatch():
    s = GovernedStateSnapshot(snapshot_id="s", pipeline_id="p", state_hash="h", execution_hash="e", topology_hash="t", telemetry_hash="m")
    r = StateReplayPacket(replay_id="r", source_state_hash="x", replayed_state_hash="x", deterministic_match=False, mismatched_transitions=["t1"])
    out = validate_state_replay(s, r)
    assert out["status"] == "invalid"
