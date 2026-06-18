import { buildMetricDashboardFrame } from './buildMetricDashboardFrame';
import type { LiveConsoleProjectionBundle } from '../types';

export interface GeometricPoint {
  x: number;
  y: number;
}

export interface GeometricOverlayFrame {
  packet_type: 'AALVizGeometricOverlayFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  projection_only: true;
  source_mode: 'BUNDLE_DERIVED' | 'FALLBACK_SAMPLE';
  points: GeometricPoint[];
}

export interface FusionOverlayFrame {
  packet_type: 'AALVizFusionOverlayFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  projection_only: true;
  source_mode: 'BUNDLE_DERIVED' | 'FALLBACK_SAMPLE';
  points: GeometricPoint[];
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
  const points = fusionPoints(bundle);
  return {
    packet_type: 'AALVizFusionOverlayFrame.v1',
    authority: 'VISUAL_PROJECTION_ONLY',
    projection_only: true,
    source_mode: points.length > 0 ? 'BUNDLE_DERIVED' : 'FALLBACK_SAMPLE',
    points: points.length > 0 ? points : FALLBACK_FUSION_POINTS,
  };
}
