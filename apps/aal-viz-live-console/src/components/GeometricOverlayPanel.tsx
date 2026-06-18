import { useMemo } from 'react';
import { buildGeometricOverlayFrame } from '../data/buildGeometricOverlayFrame';
import type { LiveConsoleProjectionBundle } from '../types';
import { GeometricRenderer } from './GeometricRenderer';

interface GeometricOverlayPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

export function GeometricOverlayPanel({ bundle }: GeometricOverlayPanelProps): JSX.Element {
  const frame = useMemo(() => buildGeometricOverlayFrame(bundle), [bundle]);

  return (
    <section className="panel-section" data-testid="geometric-overlay-panel">
      <h3 className="panel-heading">Geometric Overlay</h3>
      <p className="panel-caption">
        Projection-only SVG boundary ({frame.source_mode.toLowerCase().replace('_', ' ')})
      </p>
      <GeometricRenderer points={frame.points} width="100%" height={120} data-testid="geometric-overlay-svg" />
    </section>
  );
}
