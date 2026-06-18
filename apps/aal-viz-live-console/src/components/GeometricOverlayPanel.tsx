import { GeometricRenderer } from './GeometricRenderer';

export function GeometricOverlayPanel(): JSX.Element {
  const points = [
    { x: 10, y: 80 },
    { x: 30, y: 20 },
    { x: 70, y: 60 },
    { x: 90, y: 30 },
  ];

  return (
    <section className="panel-section" data-testid="geometric-overlay-panel">
      <h3 className="panel-heading">Geometric Overlay</h3>
      <p className="panel-caption">Projection-only SVG boundary (advisory)</p>
      <GeometricRenderer points={points} width="100%" height={120} />
    </section>
  );
}
