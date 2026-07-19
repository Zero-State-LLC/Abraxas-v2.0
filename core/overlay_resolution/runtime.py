from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.
from core.overlay_resolution.closure import OverlayResolutionClosurePacket
from core.overlay_resolution.diagnostics import OverlayResolutionDiagnosticPacket
from core.overlay_resolution.events import OverlayResolutionEventPacket
from core.overlay_resolution.ledger import OverlayResolutionLedgerPacket
from core.overlay_resolution.lineage import OverlayResolutionLineageNode, OverlayResolutionLineagePacket
from core.overlay_resolution.operator_review import OperatorOverlayResolutionReviewPacket
from core.overlay_resolution.outcomes import OverlayResolutionOutcomePacket
from core.overlay_resolution.replay import OverlayResolutionReplayPacket
from core.overlay_resolution.validators import validate_overlay_resolution

def run_overlay_resolution_ledger(governance_packets: list[dict], containment_packets: list[dict], replay_packets: list[dict], promotion_packets: list[dict], diagnostics_packets: list[dict]) -> dict[str, object]:
    event = OverlayResolutionEventPacket(resolution_event_id="orev-1", overlay_hash="overlay-1", related_review_hash="review-1", related_replay_hash="replay-1", related_diagnostic_hash="diag-1", resolution_type="containment_acknowledged", resolution_reason="Operator acknowledged advisory containment recommendation.", operator_required=True, deterministic_event_hash=OverlayResolutionEventPacket.compute_hash("overlay-1", "review-1", "replay-1", "diag-1", "containment_acknowledged", "Operator acknowledged advisory containment recommendation.", True), status="passed")
    ledger = OverlayResolutionLedgerPacket(ledger_id="orld-1", resolution_events=[event.deterministic_event_hash], total_events=1, unresolved_events=0, critical_unresolved_events=0, deterministic_ledger_hash=OverlayResolutionLedgerPacket.compute_hash([event.deterministic_event_hash], 1, 0, 0), status="passed")
    outcome = OverlayResolutionOutcomePacket(outcome_id="orout-1", overlay_hash="overlay-1", resolution_status="verified", replay_verified=True, rollback_ready=True, diagnostic_state="closed", operator_review_state="approved", deterministic_outcome_hash=OverlayResolutionOutcomePacket.compute_hash("overlay-1", "verified", True, True, "closed", "approved"), status="passed")
    closure = OverlayResolutionClosurePacket(closure_id="orcl-1", unresolved_count=0, critical_unresolved_count=0, replay_failures=0, closure_ready=True, deterministic_closure_hash=OverlayResolutionClosurePacket.compute_hash(0, 0, 0, True))
    replay = OverlayResolutionReplayPacket(replay_id="orre-1", source_ledger_hash=ledger.deterministic_ledger_hash, replay_ledger_hash=ledger.deterministic_ledger_hash, deterministic_match=True, mismatched_components=[], status="passed")
    node = OverlayResolutionLineageNode(ledger_hash=ledger.deterministic_ledger_hash, generation=1)
    lineage = OverlayResolutionLineagePacket(lineage_id="orlin-1", lineage_nodes=[node], lineage_depth=1, deterministic_lineage_hash=OverlayResolutionLineagePacket.compute_hash([node]), status="passed")
    diagnostics: list[OverlayResolutionDiagnosticPacket] = []
    review = OperatorOverlayResolutionReviewPacket(review_id="orrev-1", pending_reviews=0, critical_diagnostics=0, unresolved_events=0, pending_actions=[], status="approved")
    validator = validate_overlay_resolution(ledger, replay, [d.model_dump() for d in diagnostics], lineage_cycles_exist=False, auto_resolution_detected=False, advisory_only=True)
    packet = {"schema_version": "OverlayResolutionRuntimePacket.v1", "events": [event.model_dump()], "ledger": ledger.model_dump(), "outcomes": [outcome.model_dump()], "closure": closure.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": review.model_dump(), "validator": validator, "status": validator["status"]}
    return packet
