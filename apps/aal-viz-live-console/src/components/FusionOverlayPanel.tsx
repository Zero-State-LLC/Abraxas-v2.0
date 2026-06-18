import { useMemo } from 'react';
import { buildFusionOverlayFrame } from '../data/buildGeometricOverlayFrame';
import type { LiveConsoleProjectionBundle } from '../types';
import { GeometricRenderer } from './GeometricRenderer';

interface FusionOverlayPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

export function FusionOverlayPanel({ bundle }: FusionOverlayPanelProps): JSX.Element {
  const frame = useMemo(() => buildFusionOverlayFrame(bundle), [bundle]);

  return (
    <section className="panel-section" data-testid="fusion-overlay-panel">
      <h3 className="panel-heading">Climate + Motif Fusion</h3>
      <p className="panel-caption">
        P40 projection-only fusion overlay ({frame.source_mode.toLowerCase().replace('_', ' ')})
      </p>
      <GeometricRenderer points={frame.points} width="100%" height={100} data-testid="fusion-overlay-svg" />
    </section>
  );
}
