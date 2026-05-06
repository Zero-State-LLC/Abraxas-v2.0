from core.overlay_containment.triggers import OverlayContainmentTriggerPacket


def test_trigger_packet() -> None:
    t = OverlayContainmentTriggerPacket(trigger_id="t1", active_triggers=["aggregate_risk_above_threshold"], status="passed")
    assert t.active_triggers
