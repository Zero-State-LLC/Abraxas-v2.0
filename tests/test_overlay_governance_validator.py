from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket
from core.overlay_governance.ledger import OverlayGovernanceLedgerEntry, OverlayGovernanceLedgerPacket
from core.overlay_governance.replay import OverlayGovernanceReplayPacket
from core.overlay_governance.validators import validate_overlay_governance_ledger


def test_autonomous_promotion_event_fails_closed() -> None:
    entry = OverlayGovernanceLedgerEntry(event_hash="autonomous-1", generation=1, event_type="promotion_reviewed")
    ledger = OverlayGovernanceLedgerPacket(ledger_id="1", entries=[entry], ledger_depth=1, deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash([entry]), status="passed")
    continuity = OverlayGovernanceContinuityPacket(continuity_id="1", ledger_hash="", expected_event_types=[], observed_event_types=[], missing_event_types=[], continuity_score=1.0, deterministic_continuity_hash=OverlayGovernanceContinuityPacket.compute_hash("", [], [], [], 1.0), status="passed")
    replay = OverlayGovernanceReplayPacket(replay_id="1", source_ledger_hash="", replay_ledger_hash="", deterministic_match=True, mismatched_events=[], status="passed")
    assert validate_overlay_governance_ledger(ledger, continuity, replay, [], None)["status"] == "failed"
