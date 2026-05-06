from core.oracle.conflicts import IntakeConflictPacket


def test_unresolved_conflicts_block_approval_marker() -> None:
    c = IntakeConflictPacket(conflict_id="c", conflicting_hashes=["a", "b"], conflict_type="replay_mismatch", severity="severe", resolution_required=True)
    assert c.resolution_required
