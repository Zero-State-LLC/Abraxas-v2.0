from core.observability.snapshots import build_projection_state_snapshot


def test_projection_snapshot_projection_only() -> None:
    s = build_projection_state_snapshot({}, {}, {}, {}, {"graph": {"topology_hash": "h"}})
    assert s.projection_only is True
    assert s.inference_authority is False
