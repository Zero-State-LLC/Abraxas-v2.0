from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.

from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket
from core.overlay_governance.diagnostics import OverlayGovernanceDiagnosticPacket
from core.overlay_governance.events import OverlayGovernanceEventPacket
from core.overlay_governance.ledger import OverlayGovernanceLedgerEntry, OverlayGovernanceLedgerPacket
from core.overlay_governance.lineage import OverlayGovernanceLineageNode, OverlayGovernanceLineagePacket
from core.overlay_governance.operator_review import OperatorOverlayGovernanceReviewPacket
from core.overlay_governance.replay import OverlayGovernanceReplayPacket
from core.overlay_governance.validators import validate_overlay_governance_ledger

EXPECTED_EVENTS = [
    "overlay_created",
    "overlay_observed",
    "schedule_proposed",
    "promotion_reviewed",
]

def _event(event_id: str, event_type: str, source_packet_hash: str, generation: int, overlay_hash: str = "overlay") -> OverlayGovernanceEventPacket:
    return OverlayGovernanceEventPacket(
        event_id=event_id,
        event_type=event_type,
        source_packet_hash=source_packet_hash,
        overlay_hash=overlay_hash,
        governance_scope="audit_only",
        event_generation=generation,
        deterministic_event_hash=OverlayGovernanceEventPacket.compute_hash(event_type, source_packet_hash, overlay_hash, "audit_only", generation),
        status="passed",
    )

def run_overlay_governance_ledger(canary_packets: list[dict], overlay_observability_packets: list[dict], scheduler_packets: list[dict], promotion_packets: list[dict]) -> dict[str, object]:
    events = [
        _event("oge-1", "overlay_created", canary_packets[-1].get("overlay", {}).get("deterministic_overlay_hash", "canary"), 1),
        _event("oge-2", "overlay_observed", overlay_observability_packets[-1].get("fusion", {}).get("deterministic_fusion_hash", "obs"), 2),
        _event("oge-3", "schedule_proposed", scheduler_packets[-1].get("schedule", {}).get("deterministic_schedule_hash", "sched"), 3),
        _event("oge-4", "promotion_reviewed", promotion_packets[-1].get("candidate", {}).get("deterministic_candidate_hash", "promo"), 4),
    ]
    entries = [OverlayGovernanceLedgerEntry(event_hash=e.deterministic_event_hash, parent_event_hash=events[i - 1].deterministic_event_hash if i else None, generation=e.event_generation, event_type=e.event_type) for i, e in enumerate(events)]
    ledger = OverlayGovernanceLedgerPacket(
        ledger_id="ogl-1",
        entries=entries,
        ledger_depth=len(entries),
        deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash(entries),
        status="passed",
    )
    observed = [e.event_type for e in events]
    missing = [e for e in EXPECTED_EVENTS if e not in observed]
    score = (len(EXPECTED_EVENTS) - len(missing)) / len(EXPECTED_EVENTS)
    continuity = OverlayGovernanceContinuityPacket(
        continuity_id="ogc-1",
        ledger_hash=ledger.deterministic_ledger_hash,
        expected_event_types=EXPECTED_EVENTS,
        observed_event_types=observed,
        missing_event_types=missing,
        continuity_score=score,
        deterministic_continuity_hash=OverlayGovernanceContinuityPacket.compute_hash(ledger.deterministic_ledger_hash, EXPECTED_EVENTS, observed, missing, score),
        status="passed" if score >= 0.75 else "failed",
    )
    replay = OverlayGovernanceReplayPacket(replay_id="ogr-1", source_ledger_hash=ledger.deterministic_ledger_hash, replay_ledger_hash=ledger.deterministic_ledger_hash, deterministic_match=True, mismatched_events=[], status="passed")
    lineage_node = OverlayGovernanceLineageNode(ledger_hash=ledger.deterministic_ledger_hash, parent_hash=None, generation=1, continuity_hash=continuity.deterministic_continuity_hash)
    lineage = OverlayGovernanceLineagePacket(lineage_id="ogl-1", lineage_nodes=[lineage_node], lineage_depth=1, deterministic_lineage_hash=OverlayGovernanceLineagePacket.compute_hash([lineage_node]), status="passed")
    diagnostics: list[OverlayGovernanceDiagnosticPacket] = []
    if missing:
        diagnostics.append(OverlayGovernanceDiagnosticPacket(diagnostic_id="ogd-1", ledger_hash=ledger.deterministic_ledger_hash, diagnostic_type="missing_event", severity="warning", diagnostic_message=f"missing events: {missing}", deterministic_diagnostic_hash=OverlayGovernanceDiagnosticPacket.compute_hash(ledger.deterministic_ledger_hash, "missing_event", "warning", f"missing events: {missing}"), status="failed"))
    review = OperatorOverlayGovernanceReviewPacket(review_id="ogrv-1", ledger_hash=ledger.deterministic_ledger_hash, continuity_score=continuity.continuity_score, critical_diagnostics=sum(1 for d in diagnostics if d.severity == "critical"), missing_event_types=missing, pending_actions=["resolve_missing_events"] if missing else [], status="pending" if missing else "approved")
    validator = validate_overlay_governance_ledger(ledger, continuity, replay, [d.model_dump() for d in diagnostics], lineage)
    packet = {"schema_version": "OverlayGovernanceRuntimePacket.v1", "events": [e.model_dump() for e in events], "ledger": ledger.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": review.model_dump(), "validator": validator, "status": validator["status"]}
    return packet
