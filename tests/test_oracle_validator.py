from core.oracle.conflicts import IntakeConflictPacket
from core.oracle.replay import IntakeReplayPacket
from core.oracle.validators import validate_intake_replay


def test_validator_catches_unresolved_severe_conflicts() -> None:
    replay = IntakeReplayPacket(replay_id="r", source_intake_hash="a", replay_intake_hash="a", deterministic_match=True, mismatched_normalizations=[])
    conflict = IntakeConflictPacket(conflict_id="c", conflicting_hashes=["a"], conflict_type="provenance_mismatch", severity="severe", resolution_required=True)
    result = validate_intake_replay({"source_hash": "x"}, replay, conflicts=[conflict])
    assert result["status"] == "repair_required"
