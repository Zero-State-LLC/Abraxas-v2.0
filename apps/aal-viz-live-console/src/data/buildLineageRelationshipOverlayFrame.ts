import type {
  LineageOverlayNode,
  LineageRelationshipEdge,
  LineageRelationshipOverlayFrame,
  LiveConsoleProjectionBundle,
  RelationshipLinkKind,
  RelationshipType,
  SystemProjection,
} from '../types';

const RELATIONSHIP_TYPES: RelationshipType[] = [
  'PROVENANCE_PARENT',
  'DERIVED_FROM',
  'FORECAST_LINEAGE',
  'OUTCOME_RESOLUTION',
  'CONTRADICTION',
  'MOTIF_RESONANCE',
  'STRATEGY_DEPENDENCY',
  'OPERATOR_DECISION',
  'OBSERVED_LINK_CLAIM',
  'INFERRED_LINK_CLAIM',
  'SPECULATIVE_LINK_CLAIM',
];

const LINK_KINDS: RelationshipLinkKind[] = [
  'OBSERVED_LINK',
  'INFERRED_LINK',
  'SPECULATIVE_LINK',
  'NOT_COMPUTABLE_LINK',
];

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  }
  if (value !== null && typeof value === 'object') {
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function stableUiHash(value: unknown): string {
  const input = stableStringify(value);
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index++) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function buildNode(system: SystemProjection): LineageOverlayNode {
  return {
    node_id: system.system_id,
    label: system.display_name,
    system_id: system.system_id,
    status: system.status,
    authority_tier: 'VISUAL_PROJECTION_ONLY',
    provenance_state: system.ledger_receipts.length > 0 ? 'OBSERVED' : 'NOT_COMPUTABLE',
    selection_focus_allowed: true,
    packet_count: system.projection_packets.length,
    receipt_count: system.ledger_receipts.length,
  };
}

function linkKindFor(system: SystemProjection): RelationshipLinkKind {
  if (system.status === 'NOT_COMPUTABLE') return 'NOT_COMPUTABLE_LINK';
  if (system.status === 'FAIL_CLOSED') return 'SPECULATIVE_LINK';
  if (system.status === 'PARTIAL') return 'INFERRED_LINK';
  return system.ledger_receipts.length > 0 ? 'OBSERVED_LINK' : 'NOT_COMPUTABLE_LINK';
}

function edgeTypeFor(system: SystemProjection): RelationshipType {
  if (system.status === 'FAIL_CLOSED') return 'CONTRADICTION';
  if (system.status === 'NOT_COMPUTABLE') return 'SPECULATIVE_LINK_CLAIM';
  if (system.projection_packets.some((packet) => packet.packet_type.includes('OPERATOR'))) {
    return 'OPERATOR_DECISION';
  }
  if (system.projection_packets.some((packet) => packet.packet_type.includes('RISK'))) {
    return 'FORECAST_LINEAGE';
  }
  if (system.projection_packets.some((packet) => packet.packet_type.includes('METRIC'))) {
    return 'MOTIF_RESONANCE';
  }
  return 'DERIVED_FROM';
}

function confidenceFor(kind: RelationshipLinkKind): LineageRelationshipEdge['confidence'] {
  if (kind === 'OBSERVED_LINK') return 'HIGH';
  if (kind === 'INFERRED_LINK') return 'MEDIUM';
  if (kind === 'SPECULATIVE_LINK') return 'LOW';
  return 'NOT_COMPUTABLE';
}

function provenanceFor(kind: RelationshipLinkKind): LineageRelationshipEdge['provenance_state'] {
  if (kind === 'OBSERVED_LINK') return 'OBSERVED';
  if (kind === 'INFERRED_LINK') return 'INFERRED';
  if (kind === 'SPECULATIVE_LINK') return 'SPECULATIVE';
  return 'NOT_COMPUTABLE';
}

function buildEdges(systems: SystemProjection[]): LineageRelationshipEdge[] {
  if (systems.length === 0) return [];
  const root = systems[0];
  return systems.slice(1).map((system, index) => {
    const kind = linkKindFor(system);
    const type = edgeTypeFor(system);
    return {
      edge_id: `lineage-edge-${String(index + 1).padStart(3, '0')}`,
      source_node_id: root.system_id,
      target_node_id: system.system_id,
      relationship_type: type,
      link_kind: kind,
      confidence: confidenceFor(kind),
      authority_tier: 'VISUAL_PROJECTION_ONLY',
      provenance_state: provenanceFor(kind),
      renders_dimmed: kind === 'NOT_COMPUTABLE_LINK',
      label: kind === 'NOT_COMPUTABLE_LINK' ? `${type}: NOT_COMPUTABLE` : `${type}: ${kind}`,
    };
  });
}

export function buildLineageRelationshipOverlayFrame(
  bundle: LiveConsoleProjectionBundle,
): LineageRelationshipOverlayFrame {
  const frameWithoutHash = {
    packet_type: 'AALVizLineageRelationshipOverlayFrame.v1' as const,
    authority: 'VISUAL_PROJECTION_ONLY' as const,
    relationship_arrow_policy: 'DISPLAY_DECLARED_RELATIONSHIP_ONLY' as const,
    projection_only: true as const,
    non_filtering_compliance: true as const,
    nodes: bundle.systems.map(buildNode),
    edges: buildEdges(bundle.systems),
    relationship_types: RELATIONSHIP_TYPES,
    link_kind_legend: LINK_KINDS,
    rendering_locks: {
      gpu_simulation_mutates_packets: false as const,
      selection_highlight_mutates_packets: false as const,
      selection_highlight_ranks_packets: false as const,
      scoring_authority: false as const,
      forecasting_authority: false as const,
      validation_authority: false as const,
      promotion_authority: false as const,
      truth_authority: false as const,
      missing_source_renders_not_computable: true as const,
    },
  };

  return {
    ...frameWithoutHash,
    provenance_hash: stableUiHash(frameWithoutHash),
  };
}
