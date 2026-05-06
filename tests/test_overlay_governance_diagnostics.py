from core.overlay_governance.diagnostics import OverlayGovernanceDiagnosticPacket
from core.overlay_governance.validators import validate_overlay_governance_ledger
from core.overlay_governance.ledger import OverlayGovernanceLedgerPacket
from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket
from core.overlay_governance.replay import OverlayGovernanceReplayPacket


def test_critical_diagnostic_blocks_seal() -> None:
    d = OverlayGovernanceDiagnosticPacket(diagnostic_id="1", ledger_hash="l", diagnostic_type="continuity_gap", severity="critical", diagnostic_message="x", deterministic_diagnostic_hash=OverlayGovernanceDiagnosticPacket.compute_hash("l", "continuity_gap", "critical", "x"), status="failed")
    ledger = OverlayGovernanceLedgerPacket(ledger_id="1", entries=[], ledger_depth=0, deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash([]), status="passed")
    continuity = OverlayGovernanceContinuityPacket(continuity_id="1", ledger_hash="", expected_event_types=[], observed_event_types=[], missing_event_types=[], continuity_score=1.0, deterministic_continuity_hash=OverlayGovernanceContinuityPacket.compute_hash("", [], [], [], 1.0), status="passed")
    replay = OverlayGovernanceReplayPacket(replay_id="1", source_ledger_hash="", replay_ledger_hash="", deterministic_match=True, mismatched_events=[], status="passed")
    assert validate_overlay_governance_ledger(ledger, continuity, replay, [d.model_dump()], None)["status"] == "failed"
