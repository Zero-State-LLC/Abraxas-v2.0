from core.overlay_governance.events import OverlayGovernanceEventPacket


def test_deterministic_event_hash() -> None:
    h = OverlayGovernanceEventPacket.compute_hash("overlay_created", "a", "o", "audit_only", 1)
    p = OverlayGovernanceEventPacket(event_id="1", event_type="overlay_created", source_packet_hash="a", overlay_hash="o", governance_scope="audit_only", event_generation=1, deterministic_event_hash=h, status="passed")
    assert p.deterministic_event_hash == h
