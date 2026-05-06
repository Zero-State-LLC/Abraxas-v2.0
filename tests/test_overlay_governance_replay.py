from core.overlay_governance.replay import OverlayGovernanceReplayPacket
from core.overlay_governance.validators import validate_overlay_governance_ledger
from core.overlay_governance.ledger import OverlayGovernanceLedgerPacket
from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket


def test_replay_mismatch_blocks_seal() -> None:
    replay = OverlayGovernanceReplayPacket(replay_id="1", source_ledger_hash="a", replay_ledger_hash="b", deterministic_match=False, mismatched_events=["x"], status="failed")
    ledger = OverlayGovernanceLedgerPacket(ledger_id="1", entries=[], ledger_depth=0, deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash([]), status="passed")
    continuity = OverlayGovernanceContinuityPacket(continuity_id="1", ledger_hash="", expected_event_types=[], observed_event_types=[], missing_event_types=[], continuity_score=1.0, deterministic_continuity_hash=OverlayGovernanceContinuityPacket.compute_hash("", [], [], [], 1.0), status="passed")
    assert validate_overlay_governance_ledger(ledger, continuity, replay, [], None)["status"] == "failed"
