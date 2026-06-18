import { useMemo } from 'react';
import { buildFusionOverlayFrame } from '../data/buildGeometricOverlayFrame';
import type { LiveConsoleProjectionBundle } from '../types';
import { GeometricRenderer } from './GeometricRenderer';

interface FusionOverlayPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatSourceMode(sourceMode: string): string {
  return sourceMode.toLowerCase().replace(/_/g, ' ');
}

export function FusionOverlayPanel({ bundle }: FusionOverlayPanelProps): JSX.Element {
  const frame = useMemo(() => buildFusionOverlayFrame(bundle), [bundle]);

  const captionParts = [
    `P40 projection-only fusion overlay (${formatSourceMode(frame.source_mode)})`,
  ];
  if (frame.source_mode === 'P40_ARTIFACT') {
    captionParts.push(
      `${frame.final_status ?? 'UNKNOWN'} · ${frame.fusion_posture ?? 'UNKNOWN'}`,
      `${frame.node_count} nodes · ${frame.resolved_edge_count}/${frame.edge_count} edges resolved`,
    );
  }

  return (
    <section className="panel-section" data-testid="fusion-overlay-panel">
      <h3 className="panel-heading">Climate + Motif Fusion</h3>
      <p className="panel-caption">{captionParts.join(' · ')}</p>
      <GeometricRenderer
        points={frame.points}
        edges={frame.edges}
        width="100%"
        height={100}
        data-testid="fusion-overlay-svg"
      />
    </section>
  );
}
