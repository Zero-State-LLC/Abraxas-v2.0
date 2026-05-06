from __future__ import annotations

from core.overlay_topology.coupling import OverlayCouplingPacket
from core.overlay_topology.graph import OverlayTopologyGraphPacket
from core.overlay_topology.propagation import OverlayPropagationPathPacket
from core.overlay_topology.replay import OverlayTopologyReplayPacket
from core.overlay_topology.rollback_paths import OverlayRollbackPathPacket


def validate_overlay_topology(
    graph: OverlayTopologyGraphPacket,
    coupling: OverlayCouplingPacket,
    rollback_paths: OverlayRollbackPathPacket,
    propagation: OverlayPropagationPathPacket,
    replay: OverlayTopologyReplayPacket,
    diagnostics: list[dict],
) -> dict[str, object]:
    if not (0 <= graph.graph_density <= 1):
        return {'status': 'failed', 'reason': 'density'}
    if coupling.hidden_dependency_cycle:
        return {'status': 'failed', 'reason': 'hidden dependency cycle'}
    if coupling.production_route_detected:
        return {'status': 'failed', 'reason': 'production route'}
    if propagation.production_route_included:
        return {'status': 'failed', 'reason': 'propagation production route'}
    if rollback_paths.execution_claimed:
        return {'status': 'failed', 'reason': 'rollback execution claimed'}
    if replay.deterministic_match is False:
        return {'status': 'failed', 'reason': 'replay mismatch'}
    if any(d.get('severity') == 'critical' for d in diagnostics):
        return {'status': 'failed', 'reason': 'critical diagnostics'}
    graph.authority.assert_locked()
    coupling.authority.assert_locked()
    return {'status': 'passed', 'reason': 'overlay topology validated'}
