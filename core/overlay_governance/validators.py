from __future__ import annotations

from typing import Any

from core.overlay_governance.continuity import OverlayGovernanceContinuityPacket
from core.overlay_governance.ledger import OverlayGovernanceLedgerPacket
from core.overlay_governance.lineage import OverlayGovernanceLineagePacket
from core.overlay_governance.replay import OverlayGovernanceReplayPacket

_FORBIDDEN_SOURCE_HASHES = frozenset(
    {"", "canary", "obs", "sched", "promo", "unknown", "overlay"}
)


def validate_overlay_governance_ledger(
    ledger_packet: OverlayGovernanceLedgerPacket,
    continuity_packet: OverlayGovernanceContinuityPacket,
    replay_packet: OverlayGovernanceReplayPacket,
    diagnostics: list[dict],
    lineage_packet: OverlayGovernanceLineagePacket | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    if replay_packet.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch invalidates ledger seal"}
    if any(d.get("severity") == "critical" for d in diagnostics):
        return {"status": "failed", "reason": "critical diagnostics block seal"}
    if continuity_packet.missing_event_types:
        return {
            "status": "failed",
            "reason": "missing expected governance events fail closed",
        }
    if continuity_packet.status != "passed":
        return {
            "status": "failed",
            "reason": "continuity failure blocks ledger seal",
        }
    if any(
        e.event_type == "promotion_reviewed" and e.event_hash.startswith("autonomous")
        for e in ledger_packet.entries
    ):
        return {"status": "failed", "reason": "autonomous promotion event fails closed"}
    if events:
        for event in events:
            source_hash = str(event.get("source_packet_hash", "")).strip()
            if source_hash in _FORBIDDEN_SOURCE_HASHES:
                return {
                    "status": "failed",
                    "reason": "sentinel source packet hashes fail closed",
                }
    try:
        ledger_packet.authority.assert_locked()
        continuity_packet.authority.assert_locked()
        replay_packet.authority.assert_locked()
        if lineage_packet is not None:
            lineage_packet.authority.assert_locked()
    except ValueError:
        return {"status": "failed", "reason": "mutation authority fails closed"}
    if lineage_packet is not None:
        for node in lineage_packet.lineage_nodes:
            if node.parent_hash == node.ledger_hash:
                return {
                    "status": "failed",
                    "reason": "governance lineage cycles fail closed",
                }
    return {"status": "passed", "reason": "overlay governance ledger validated"}
