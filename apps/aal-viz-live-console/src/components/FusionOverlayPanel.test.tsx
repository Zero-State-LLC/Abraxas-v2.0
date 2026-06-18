import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FusionOverlayPanel } from './FusionOverlayPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { FusionOverlayPacket, LiveConsoleProjectionBundle } from '../types';

const p40FusionOverlay: FusionOverlayPacket = {
  packet_type: 'AALVizClimateMotifFusionOverlay.v1',
  final_status: 'PROJECTION_DEGRADED',
  fusion_posture: 'PRESSURE_PERSISTENCE',
  overlay_nodes: [
    { node_id: 'climate.node.weather', label: 'Weather', posture: 'WATCH' },
    { node_id: 'climate.node.routing', label: 'Routing', posture: 'BLOCKED' },
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

describe('FusionOverlayPanel', () => {
  it('renders bundle-derived fusion overlay', () => {
    render(<FusionOverlayPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('fusion-overlay-panel')).toBeInTheDocument();
    expect(screen.getByText(/bundle derived/i)).toBeInTheDocument();
    expect(screen.getByTestId('fusion-overlay-svg')).toBeInTheDocument();
  });

  it('renders P40 artifact posture and counts when fusion overlay is present', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      fusion_overlay: p40FusionOverlay,
    };
    render(<FusionOverlayPanel bundle={bundle} />);

    expect(screen.getByText(/p40 artifact/i)).toBeInTheDocument();
    expect(screen.getByText(/PROJECTION_DEGRADED/i)).toBeInTheDocument();
    expect(screen.getByText(/PRESSURE_PERSISTENCE/i)).toBeInTheDocument();
    expect(screen.getByText(/2 nodes · 1\/1 edges resolved/i)).toBeInTheDocument();
    expect(screen.getAllByTestId('geometric-renderer-edge')).toHaveLength(1);
  });
});
