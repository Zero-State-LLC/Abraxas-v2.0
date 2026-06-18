import { GeometricRenderer } from './GeometricRenderer';

export function FusionOverlayPanel(): JSX.Element {
  return (
    <section className="panel-section" data-testid="fusion-overlay-panel">
      <h3 className="panel-heading">Climate + Motif Fusion</h3>
      <p className="panel-caption">P40 projection-only fusion overlay consumer</p>
      <GeometricRenderer
        points={[
          { x: 5, y: 50 },
          { x: 35, y: 15 },
          { x: 65, y: 85 },
          { x: 95, y: 40 },
        ]}
        width="100%"
        height={100}
      />
    </section>
  );
}
