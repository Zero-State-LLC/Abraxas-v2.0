import pytest
from core.overlay_observability.telemetry import OverlayTelemetryPacket

def test_telemetry_count_bounds() -> None:
    with pytest.raises(ValueError):
        OverlayTelemetryPacket(telemetry_id='t',overlay_hash='o',replay_match_count=-1,replay_failure_count=0,rollback_count=0,blocked_route_count=0,pending_review_count=0,stability_score=0.5,deterministic_telemetry_hash='x',status='passed')
