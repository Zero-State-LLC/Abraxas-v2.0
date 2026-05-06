from core.state.models import GovernedStateSnapshot


def test_snapshot_valid_and_deterministic_hash_field():
    s = GovernedStateSnapshot(snapshot_id="s1", pipeline_id="p1", state_hash="h1", execution_hash="e1", topology_hash="t1", telemetry_hash="m1")
    assert s.schema_version == "GovernedStateSnapshot.v1"
