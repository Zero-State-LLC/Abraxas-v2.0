from __future__ import annotations

from core.overlay_risk.envelopes import OverlayRiskEnvelopePacket
from core.overlay_risk.propagation import OverlayPropagationRiskPacket
from core.overlay_risk.replay import OverlayRiskReplayPacket


def validate_overlay_risk(
    envelopes: list[OverlayRiskEnvelopePacket],
    propagation: OverlayPropagationRiskPacket,
    replay: OverlayRiskReplayPacket,
    diagnostics: list[dict],
) -> dict[str, object]:
    if any(not (0 <= e.aggregate_risk_score <= 1) for e in envelopes):
        return {"status": "failed", "reason": "score bounds"}
    if replay.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch"}
    if propagation.cycles_detected:
        return {"status": "failed", "reason": "propagation cycles"}
    if propagation.autonomous_escalation_detected:
        return {"status": "failed", "reason": "autonomous escalation"}
    if any(d.get("severity") == "critical" for d in diagnostics):
        return {"status": "failed", "reason": "critical diagnostics"}
    propagation.authority.assert_locked()
    for e in envelopes:
        e.authority.assert_locked()
    return {"status": "passed", "reason": "overlay risk validated"}
