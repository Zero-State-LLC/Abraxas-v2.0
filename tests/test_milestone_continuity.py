from core.spine.milestone_continuity import validate_milestone_continuity


def test_milestone_continuity_packet_builds():
    packet = validate_milestone_continuity()
    assert packet.schema_version == "MilestoneContinuityPacket.v1"


def test_missing_route_detection():
    packet = validate_milestone_continuity()
    assert isinstance(packet.missing_routes, list)
