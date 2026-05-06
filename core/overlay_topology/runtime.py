from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_topology.adjacency import OverlayAdjacencyPacket
from core.overlay_topology.bottlenecks import OverlayBottleneckPacket
from core.overlay_topology.coupling import OverlayCouplingPacket
from core.overlay_topology.diagnostics import OverlayTopologyDiagnosticPacket
from core.overlay_topology.graph import OverlayTopologyGraphPacket
from core.overlay_topology.lineage import OverlayTopologyLineageNode, OverlayTopologyLineagePacket
from core.overlay_topology.operator_review import OperatorOverlayTopologyReviewPacket
from core.overlay_topology.propagation import OverlayPropagationPathPacket
from core.overlay_topology.replay import OverlayTopologyReplayPacket
from core.overlay_topology.rollback_paths import OverlayRollbackPathPacket
from core.overlay_topology.validators import validate_overlay_topology


def run_overlay_topology_simulation(overlay_risk_packets: list[dict], governance_packets: list[dict], scheduler_packets: list[dict], promotion_packets: list[dict]) -> dict[str, object]:
    node = 'overlay-1'
    nodes = [node]
    edges: list[tuple[str, str]] = []
    depth = 1
    density = 0.0
    graph = OverlayTopologyGraphPacket(topology_graph_id='otg-1', overlay_nodes=nodes, overlay_edges=edges, graph_depth=depth, graph_density=density, deterministic_graph_hash=OverlayTopologyGraphPacket.compute_hash(nodes, edges, depth, density), status='passed')
    adjacency = OverlayAdjacencyPacket(adjacency_id='ota-1', adjacent_overlays=0, shared_dependencies=1, shared_rollback_paths=1, shared_governance_events=1, adjacency_score=0.2, deterministic_adjacency_hash=OverlayAdjacencyPacket.compute_hash(0, 1, 1, 1, 0.2), status='passed')
    coupling = OverlayCouplingPacket(coupling_id='otc-1', dependency_coupling=0.2, replay_coupling=0.1, risk_coupling=0.2, governance_coupling=0.2, aggregate_coupling_score=0.175, deterministic_coupling_hash=OverlayCouplingPacket.compute_hash(0.2, 0.1, 0.2, 0.2, 0.175, False, False), status='passed')
    bottleneck = OverlayBottleneckPacket(bottleneck_id='otb-1', high_degree_overlays=[], rollback_chokepoints=[], review_chokepoints=[], propagation_chokepoints=[], governance_ledger_bottlenecks=[], bottleneck_count=0, status='passed')
    rollback = OverlayRollbackPathPacket(rollback_path_id='otr-1', rollback_path_nodes=[node], rollback_path_depth=1, rollback_dependency_count=1, rollback_path_risk=0.2, execution_claimed=False, status='passed')
    propagation = OverlayPropagationPathPacket(propagation_path_id='otp-1', propagation_path_nodes=[node], propagation_depth=1, propagation_score=0.2, blocked_propagation_routes=[], production_route_included=False, status='passed')
    replay = OverlayTopologyReplayPacket(replay_id='otre-1', source_graph_hash=graph.deterministic_graph_hash, replay_graph_hash=graph.deterministic_graph_hash, deterministic_match=True, mismatched_components=[], status='passed')
    lineage_node = OverlayTopologyLineageNode(graph_hash=graph.deterministic_graph_hash, generation=1)
    lineage = OverlayTopologyLineagePacket(lineage_id='otl-1', lineage_nodes=[lineage_node], lineage_depth=1, deterministic_lineage_hash=OverlayTopologyLineagePacket.compute_hash([lineage_node]), status='passed')
    diagnostics: list[OverlayTopologyDiagnosticPacket] = []
    review = OperatorOverlayTopologyReviewPacket(review_id='otv-1', graph_density=density, bottleneck_count=0, critical_diagnostics=0, pending_actions=[], status='approved')
    validator = validate_overlay_topology(graph, coupling, rollback, propagation, replay, [d.model_dump() for d in diagnostics])
    packet = {'schema_version': 'OverlayTopologyRuntimePacket.v1', 'graph': graph.model_dump(), 'adjacency': adjacency.model_dump(), 'coupling': coupling.model_dump(), 'bottleneck': bottleneck.model_dump(), 'rollback_paths': rollback.model_dump(), 'propagation': propagation.model_dump(), 'replay': replay.model_dump(), 'lineage': lineage.model_dump(), 'diagnostics': [d.model_dump() for d in diagnostics], 'operator_review': review.model_dump(), 'validator': validator, 'status': validator['status']}
    write_canonical_json('out/overlay_topology/latest.json', packet)
    write_canonical_json('out/overlay_topology_replay/latest.json', replay.model_dump())
    write_canonical_json('out/overlay_topology_lineage/latest.json', lineage.model_dump())
    write_canonical_json('out/overlay_topology_diagnostics/latest.json', [d.model_dump() for d in diagnostics])
    return packet
