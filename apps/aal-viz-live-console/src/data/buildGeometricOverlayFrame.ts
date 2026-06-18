import { buildMetricDashboardFrame } from './buildMetricDashboardFrame';
import type { GeometricEdgeSegment } from '../components/GeometricRenderer';
import type { FusionOverlayEdge, FusionOverlayNode, LiveConsoleProjectionBundle } from '../types';

export interface GeometricPoint {
  x: number;
  y: number;
}

export type FusionOverlaySourceMode = 'P40_ARTIFACT' | 'BUNDLE_DERIVED' | 'FALLBACK_SAMPLE';

export interface GeometricOverlayFrame {
  packet_type: 'AALVizGeometricOverlayFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  projection_only: true;
  source_mode: 'BUNDLE_DERIVED' | 'FALLBACK_SAMPLE';
  points: GeometricPoint[];
}

export interface FusionOverlayNodeLabelSummary {
  label: string;
  posture: string;
}

export interface FusionOverlayLayerLegendEntry {
  layer: string;
  count: number;
}

export interface FusionOverlayFrame {
  packet_type: 'AALVizFusionOverlayFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  projection_only: true;
  source_mode: FusionOverlaySourceMode;
  points: GeometricPoint[];
  edges: GeometricEdgeSegment[];
  final_status?: string;
  fusion_posture?: string;
  node_count: number;
  edge_count: number;
  resolved_edge_count: number;
  layer_legend: FusionOverlayLayerLegendEntry[];
  node_label_summary: FusionOverlayNodeLabelSummary[];
}

const FALLBACK_GEOMETRIC_POINTS: GeometricPoint[] = [
  { x: 10, y: 80 },
  { x: 30, y: 20 },
  { x: 70, y: 60 },
  { x: 90, y: 30 },
];

const FALLBACK_FUSION_POINTS: GeometricPoint[] = [
  { x: 5, y: 50 },
  { x: 35, y: 15 },
  { x: 65, y: 85 },
  { x: 95, y: 40 },
];

function clampViewBox(value: number): number {
  return Math.max(5, Math.min(95, value));
}

function stableUiHash(value: string): number {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index++) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

function systemPoints(bundle: LiveConsoleProjectionBundle): GeometricPoint[] {
  const systems = bundle.systems;
  if (systems.length === 0) return [];

  return systems.map((system, index) => {
    const xSpread = systems.length > 1 ? index / (systems.length - 1) : 0.5;
    const x = clampViewBox(10 + xSpread * 80);
    const y = clampViewBox(100 - system.completion_pct * 0.8 - 10);
    return { x, y };
  });
}

function fusionPoints(bundle: LiveConsoleProjectionBundle): GeometricPoint[] {
  const dashboard = buildMetricDashboardFrame(bundle);
  const matrix = dashboard.system_fusion_matrix;
  if (matrix.length === 0) return [];

  return matrix.map((row, index) => {
    const xSpread = matrix.length > 1 ? index / (matrix.length - 1) : 0.5;
    const motifWeight = row.metric_contribution.length % 40;
    return {
      x: clampViewBox(8 + xSpread * 84),
      y: clampViewBox(90 - motifWeight),
    };
  });
}

const NODE_LABEL_SUMMARY_LIMIT = 6;

function layerPrefix(node: FusionOverlayNode): string {
  const source = node.layer_id ?? node.node_id;
  const dotIndex = source.indexOf('.');
  return dotIndex === -1 ? source : source.slice(0, dotIndex);
}

function buildLayerLegend(nodes: FusionOverlayNode[]): FusionOverlayLayerLegendEntry[] {
  const counts = new Map<string, number>();
  for (const node of nodes) {
    const prefix = layerPrefix(node);
    counts.set(prefix, (counts.get(prefix) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([layer, count]) => ({ layer, count }));
}

function buildNodeLabelSummary(nodes: FusionOverlayNode[]): FusionOverlayNodeLabelSummary[] {
  const seen = new Set<string>();
  const summary: FusionOverlayNodeLabelSummary[] = [];
  const sorted = [...nodes].sort((left, right) => {
    const leftLabel = left.label ?? left.node_id;
    const rightLabel = right.label ?? right.node_id;
    return leftLabel.localeCompare(rightLabel);
  });

  for (const node of sorted) {
    const label = node.label ?? node.node_id;
    const posture = node.posture ?? 'UNKNOWN';
    const key = `${label}|${posture}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    summary.push({ label, posture });
    if (summary.length >= NODE_LABEL_SUMMARY_LIMIT) {
      break;
    }
  }

  return summary;
}

function p40NodeLayout(nodes: FusionOverlayNode[]): {
  points: GeometricPoint[];
  nodePositions: Map<string, GeometricPoint>;
} {
  const sorted = [...nodes].sort((left, right) => left.node_id.localeCompare(right.node_id));
  const nodePositions = new Map<string, GeometricPoint>();
  const points = sorted.map((node, index) => {
    const xSpread = sorted.length > 1 ? index / (sorted.length - 1) : 0.5;
    const postureKey = node.posture ?? node.layer_id ?? node.label ?? node.node_id;
    const postureWeight = stableUiHash(postureKey) % 70;
    const point = {
      x: clampViewBox(8 + xSpread * 84),
      y: clampViewBox(92 - postureWeight),
    };
    nodePositions.set(node.node_id, point);
    return point;
  });

  return { points, nodePositions };
}

function resolveP40Edges(
  edges: FusionOverlayEdge[],
  nodePositions: Map<string, GeometricPoint>,
): GeometricEdgeSegment[] {
  const resolved: GeometricEdgeSegment[] = [];
  for (const edge of edges) {
    const source = nodePositions.get(edge.source_node_id);
    const target = nodePositions.get(edge.target_node_id);
    if (source == null || target == null) {
      continue;
    }
    resolved.push({ source, target });
  }
  return resolved;
}

export function buildGeometricOverlayFrame(bundle: LiveConsoleProjectionBundle): GeometricOverlayFrame {
  const points = systemPoints(bundle);
  return {
    packet_type: 'AALVizGeometricOverlayFrame.v1',
    authority: 'VISUAL_PROJECTION_ONLY',
    projection_only: true,
    source_mode: points.length > 0 ? 'BUNDLE_DERIVED' : 'FALLBACK_SAMPLE',
    points: points.length > 0 ? points : FALLBACK_GEOMETRIC_POINTS,
  };
}

export function buildFusionOverlayFrame(bundle: LiveConsoleProjectionBundle): FusionOverlayFrame {
  const fusionOverlay = bundle.fusion_overlay;
  if (fusionOverlay != null && fusionOverlay.overlay_nodes.length > 0) {
    const { points, nodePositions } = p40NodeLayout(fusionOverlay.overlay_nodes);
    const edges = resolveP40Edges(fusionOverlay.overlay_edges, nodePositions);
    return {
      packet_type: 'AALVizFusionOverlayFrame.v1',
      authority: 'VISUAL_PROJECTION_ONLY',
      projection_only: true,
      source_mode: 'P40_ARTIFACT',
      points,
      edges,
      final_status: fusionOverlay.final_status,
      fusion_posture: fusionOverlay.fusion_posture,
      node_count: fusionOverlay.overlay_nodes.length,
      edge_count: fusionOverlay.overlay_edges.length,
      resolved_edge_count: edges.length,
      layer_legend: buildLayerLegend(fusionOverlay.overlay_nodes),
      node_label_summary: buildNodeLabelSummary(fusionOverlay.overlay_nodes),
    };
  }

  const points = fusionPoints(bundle);
  return {
    packet_type: 'AALVizFusionOverlayFrame.v1',
    authority: 'VISUAL_PROJECTION_ONLY',
    projection_only: true,
    source_mode: points.length > 0 ? 'BUNDLE_DERIVED' : 'FALLBACK_SAMPLE',
    points: points.length > 0 ? points : FALLBACK_FUSION_POINTS,
    edges: [],
    node_count: points.length > 0 ? points.length : FALLBACK_FUSION_POINTS.length,
    edge_count: 0,
    resolved_edge_count: 0,
    layer_legend: [],
    node_label_summary: [],
  };
}
