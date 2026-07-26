from __future__ import annotations

# WP-D batch3: pure builder — sole-writer scripts publish.
from typing import Any

from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket
from core.overlay_governance.diagnostics import OverlayGovernanceDiagnosticPacket
from core.overlay_governance.events import OverlayGovernanceEventPacket
from core.overlay_governance.ledger import (
    OverlayGovernanceLedgerEntry,
    OverlayGovernanceLedgerPacket,
)
from core.overlay_governance.lineage import (
    OverlayGovernanceLineageNode,
    OverlayGovernanceLineagePacket,
)
from core.overlay_governance.operator_review import (
    OperatorOverlayGovernanceReviewPacket,
)
from core.overlay_governance.replay import OverlayGovernanceReplayPacket
from core.overlay_governance.validators import validate_overlay_governance_ledger

EXPECTED_EVENTS = [
    "overlay_created",
    "overlay_observed",
    "schedule_proposed",
    "promotion_reviewed",
]

# Former silent defaults that fabricated a complete governance chain.
_FORBIDDEN_SOURCE_HASHES = frozenset(
    {"", "canary", "obs", "sched", "promo", "unknown", "overlay"}
)


def _event(
    event_id: str,
    event_type: str,
    source_packet_hash: str,
    generation: int,
    overlay_hash: str = "overlay",
) -> OverlayGovernanceEventPacket:
    return OverlayGovernanceEventPacket(
        event_id=event_id,
        event_type=event_type,
        source_packet_hash=source_packet_hash,
        overlay_hash=overlay_hash,
        governance_scope="audit_only",
        event_generation=generation,
        deterministic_event_hash=OverlayGovernanceEventPacket.compute_hash(
            event_type, source_packet_hash, overlay_hash, "audit_only", generation
        ),
        status="passed",
    )


def _latest_packet(packets: list[dict]) -> dict[str, Any]:
    if not packets:
        return {}
    last = packets[-1]
    return last if isinstance(last, dict) else {}


def _extract_source_hash(packet: dict[str, Any], *path: str) -> str | None:
    current: Any = packet
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    if isinstance(current, str):
        normalized = current.strip()
        if normalized and normalized not in _FORBIDDEN_SOURCE_HASHES:
            return normalized
    return None


def run_overlay_governance_ledger(
    canary_packets: list[dict],
    overlay_observability_packets: list[dict],
    scheduler_packets: list[dict],
    promotion_packets: list[dict],
) -> dict[str, object]:
    """Build overlay governance ledger. Missing upstream evidence fails closed."""
    sources = [
        (
            "overlay_created",
            "oge-1",
            1,
            _extract_source_hash(
                _latest_packet(canary_packets), "overlay", "deterministic_overlay_hash"
            ),
            "missing_canary_overlay_hash",
        ),
        (
            "overlay_observed",
            "oge-2",
            2,
            _extract_source_hash(
                _latest_packet(overlay_observability_packets),
                "fusion",
                "deterministic_fusion_hash",
            ),
            "missing_overlay_observability_fusion_hash",
        ),
        (
            "schedule_proposed",
            "oge-3",
            3,
            _extract_source_hash(
                _latest_packet(scheduler_packets),
                "schedule",
                "deterministic_schedule_hash",
            ),
            "missing_scheduler_schedule_hash",
        ),
        (
            "promotion_reviewed",
            "oge-4",
            4,
            _extract_source_hash(
                _latest_packet(promotion_packets),
                "candidate",
                "deterministic_candidate_hash",
            ),
            "missing_promotion_candidate_hash",
        ),
    ]

    events: list[OverlayGovernanceEventPacket] = []
    missing_evidence: list[str] = []
    for event_type, event_id, generation, source_hash, evidence_id in sources:
        if source_hash is None:
            missing_evidence.append(evidence_id)
            continue
        events.append(_event(event_id, event_type, source_hash, generation))

    entries = [
        OverlayGovernanceLedgerEntry(
            event_hash=event.deterministic_event_hash,
            parent_event_hash=(
                events[index - 1].deterministic_event_hash if index else None
            ),
            generation=event.event_generation,
            event_type=event.event_type,
        )
        for index, event in enumerate(events)
    ]
    ledger = OverlayGovernanceLedgerPacket(
        ledger_id="ogl-1",
        entries=entries,
        ledger_depth=len(entries),
        deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash(entries),
        status="passed" if not missing_evidence else "failed",
    )
    observed = [event.event_type for event in events]
    missing = [event_type for event_type in EXPECTED_EVENTS if event_type not in observed]
    score = (len(EXPECTED_EVENTS) - len(missing)) / len(EXPECTED_EVENTS)
    continuity = OverlayGovernanceContinuityPacket(
        continuity_id="ogc-1",
        ledger_hash=ledger.deterministic_ledger_hash,
        expected_event_types=EXPECTED_EVENTS,
        observed_event_types=observed,
        missing_event_types=missing,
        continuity_score=score,
        deterministic_continuity_hash=OverlayGovernanceContinuityPacket.compute_hash(
            ledger.deterministic_ledger_hash,
            EXPECTED_EVENTS,
            observed,
            missing,
            score,
        ),
        status="passed" if score >= 0.75 and not missing_evidence else "failed",
    )
    replay = OverlayGovernanceReplayPacket(
        replay_id="ogr-1",
        source_ledger_hash=ledger.deterministic_ledger_hash,
        replay_ledger_hash=ledger.deterministic_ledger_hash,
        deterministic_match=True,
        mismatched_events=[],
        status="passed",
    )
    lineage_node = OverlayGovernanceLineageNode(
        ledger_hash=ledger.deterministic_ledger_hash,
        parent_hash=None,
        generation=1,
        continuity_hash=continuity.deterministic_continuity_hash,
    )
    lineage = OverlayGovernanceLineagePacket(
        lineage_id="ogl-1",
        lineage_nodes=[lineage_node],
        lineage_depth=1,
        deterministic_lineage_hash=OverlayGovernanceLineagePacket.compute_hash(
            [lineage_node]
        ),
        status="passed",
    )

    diagnostics: list[OverlayGovernanceDiagnosticPacket] = []
    if missing_evidence:
        message = f"missing upstream evidence: {missing_evidence}"
        diagnostics.append(
            OverlayGovernanceDiagnosticPacket(
                diagnostic_id="ogd-missing-evidence",
                ledger_hash=ledger.deterministic_ledger_hash,
                diagnostic_type="continuity_gap",
                severity="critical",
                diagnostic_message=message,
                deterministic_diagnostic_hash=OverlayGovernanceDiagnosticPacket.compute_hash(
                    ledger.deterministic_ledger_hash,
                    "continuity_gap",
                    "critical",
                    message,
                ),
                status="failed",
            )
        )
    if missing:
        message = f"missing events: {missing}"
        diagnostics.append(
            OverlayGovernanceDiagnosticPacket(
                diagnostic_id="ogd-1",
                ledger_hash=ledger.deterministic_ledger_hash,
                diagnostic_type="missing_event",
                severity="critical" if missing_evidence else "warning",
                diagnostic_message=message,
                deterministic_diagnostic_hash=OverlayGovernanceDiagnosticPacket.compute_hash(
                    ledger.deterministic_ledger_hash,
                    "missing_event",
                    "critical" if missing_evidence else "warning",
                    message,
                ),
                status="failed",
            )
        )

    review = OperatorOverlayGovernanceReviewPacket(
        review_id="ogrv-1",
        ledger_hash=ledger.deterministic_ledger_hash,
        continuity_score=continuity.continuity_score,
        critical_diagnostics=sum(
            1 for diagnostic in diagnostics if diagnostic.severity == "critical"
        ),
        missing_event_types=missing,
        pending_actions=(
            ["resolve_missing_upstream_evidence", "resolve_missing_events"]
            if missing_evidence or missing
            else []
        ),
        status="pending" if missing_evidence or missing else "approved",
    )
    validator = validate_overlay_governance_ledger(
        ledger,
        continuity,
        replay,
        [diagnostic.model_dump() for diagnostic in diagnostics],
        lineage,
        events=[event.model_dump() for event in events],
    )
    return {
        "schema_version": "OverlayGovernanceRuntimePacket.v1",
        "events": [event.model_dump() for event in events],
        "ledger": ledger.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [diagnostic.model_dump() for diagnostic in diagnostics],
        "operator_review": review.model_dump(),
        "validator": validator,
        "status": validator["status"],
    }
