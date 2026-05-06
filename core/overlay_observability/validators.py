from __future__ import annotations

from core.overlay_observability.fusion import OverlayObservabilityFusionPacket
from core.overlay_observability.replay import OverlayObservabilityReplayPacket
from core.overlay_observability.stability import OverlayStabilityPacket
from core.overlay_observability.telemetry import OverlayTelemetryPacket


def validate_overlay_observability(
    fusion_packet: OverlayObservabilityFusionPacket,
    telemetry_packet: OverlayTelemetryPacket,
    replay_packet: OverlayObservabilityReplayPacket,
    stability_packet: OverlayStabilityPacket,
    critical_authority_diagnostics: int = 0,
    cyclic_lineage: bool = False,
    production_mutation_attempted: bool = False,
) -> dict[str, object]:
    _ = telemetry_packet
    _ = stability_packet
    if fusion_packet.fusion_scope not in {"diagnostic_only", "replay_only", "projection_only"}:
        return {"status": "failed", "reason": "diagnostic scope cannot route"}
    if replay_packet.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch invalidates stability"}
    if critical_authority_diagnostics > 0:
        return {"status": "failed", "reason": "critical authority diagnostics block seal"}
    if cyclic_lineage or production_mutation_attempted:
        return {"status": "failed", "reason": "fail closed"}
    return {"status": "passed", "reason": "overlay observability validated"}
