from __future__ import annotations
from core.overlay_resolution.ledger import OverlayResolutionLedgerPacket
from core.overlay_resolution.replay import OverlayResolutionReplayPacket


def validate_overlay_resolution(ledger: OverlayResolutionLedgerPacket, replay: OverlayResolutionReplayPacket, diagnostics: list[dict], lineage_cycles_exist: bool, auto_resolution_detected: bool, advisory_only: bool) -> dict[str, object]:
    if ledger.resolution_events != sorted(ledger.resolution_events):
        return {"status": "failed", "reason": "append ordering invalid"}
    if replay.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch"}
    if any(d.get("severity") == "critical" for d in diagnostics):
        return {"status": "failed", "reason": "critical unresolved diagnostics"}
    if lineage_cycles_exist:
        return {"status": "failed", "reason": "lineage cycles"}
    if auto_resolution_detected:
        return {"status": "failed", "reason": "auto resolution detected"}
    if not advisory_only:
        return {"status": "failed", "reason": "non-advisory resolution"}
    ledger.authority.assert_locked()
    return {"status": "passed", "reason": "overlay resolution validated"}
