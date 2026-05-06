from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket


def test_continuity_score_deterministic() -> None:
    h = OverlayGovernanceContinuityPacket.compute_hash("l", ["a"], ["a"], [], 1.0)
    p = OverlayGovernanceContinuityPacket(continuity_id="1", ledger_hash="l", expected_event_types=["a"], observed_event_types=["a"], missing_event_types=[], continuity_score=1.0, deterministic_continuity_hash=h, status="passed")
    assert p.continuity_score == 1.0


def test_missing_events_lower_score() -> None:
    h = OverlayGovernanceContinuityPacket.compute_hash("l", ["a", "b"], ["a"], ["b"], 0.5)
    p = OverlayGovernanceContinuityPacket(continuity_id="1", ledger_hash="l", expected_event_types=["a", "b"], observed_event_types=["a"], missing_event_types=["b"], continuity_score=0.5, deterministic_continuity_hash=h, status="failed")
    assert p.continuity_score < 1.0
