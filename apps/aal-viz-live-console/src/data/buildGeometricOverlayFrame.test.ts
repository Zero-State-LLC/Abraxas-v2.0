import { describe, expect, it } from 'vitest';
import { buildFusionOverlayFrame, buildGeometricOverlayFrame } from './buildGeometricOverlayFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { FusionOverlayPacket, LiveConsoleProjectionBundle } from '../types';

const p40FusionOverlay: FusionOverlayPacket = {
  packet_type: 'AALVizClimateMotifFusionOverlay.v1',
  final_status: 'PROJECTION_DEGRADED',
  fusion_posture: 'PRESSURE_PERSISTENCE',
  overlay_nodes: [
    { node_id: 'climate.node.weather', label: 'Weather', posture: 'WATCH', layer_id: 'climate.weather_state' },
    { node_id: 'climate.node.routing', label: 'Routing', posture: 'BLOCKED', layer_id: 'climate.routing_state' },
    { node_id: 'seasonality.node.recurrence', label: 'Seasonality Recurrence', posture: 'PRESSURE_PERSISTENCE' },
  ],
  overlay_edges: [
    {
      edge_id: 'climate.edge.weather.routing',
      source_node_id: 'climate.node.weather',
      target_node_id: 'climate.node.routing',
      relation: 'influences',
    },
  ],
  governance_flags: {
    advisory_only: true,
    projection_only: true,
  },
};

describe('buildGeometricOverlayFrame', () => {
  it('derives geometric points from bundle systems', () => {
    const frame = buildGeometricOverlayFrame(sampleProjectionBundle);

    expect(frame.source_mode).toBe('BUNDLE_DERIVED');
    expect(frame.points.length).toBe(sampleProjectionBundle.systems.length);
    expect(frame.projection_only).toBe(true);
  });

  it('falls back to sample geometry for empty bundles', () => {
    const emptyBundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [],
    };
    const frame = buildGeometricOverlayFrame(emptyBundle);

    expect(frame.source_mode).toBe('FALLBACK_SAMPLE');
    expect(frame.points).toHaveLength(4);
  });
});

describe('buildFusionOverlayFrame', () => {
  it('prefers P40 fusion overlay nodes when present', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      fusion_overlay: p40FusionOverlay,
    };
    const frame = buildFusionOverlayFrame(bundle);

    expect(frame.source_mode).toBe('P40_ARTIFACT');
    expect(frame.points).toHaveLength(3);
    expect(frame.final_status).toBe('PROJECTION_DEGRADED');
    expect(frame.fusion_posture).toBe('PRESSURE_PERSISTENCE');
    expect(frame.node_count).toBe(3);
    expect(frame.edge_count).toBe(1);
    expect(frame.projection_only).toBe(true);
  });

  it('derives fusion points from dashboard fusion matrix without P40', () => {
    const frame = buildFusionOverlayFrame(sampleProjectionBundle);

    expect(frame.source_mode).toBe('BUNDLE_DERIVED');
    expect(frame.points.length).toBeGreaterThan(0);
    expect(frame.projection_only).toBe(true);
    expect(frame.edge_count).toBe(0);
  });

  it('uses dashboard fusion matrix heuristic without P40 even when systems are empty', () => {
    const emptyBundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [],
    };
    const frame = buildFusionOverlayFrame(emptyBundle);

    expect(frame.source_mode).toBe('BUNDLE_DERIVED');
    expect(frame.points.length).toBeGreaterThan(0);
    expect(frame.edge_count).toBe(0);
  });
});
