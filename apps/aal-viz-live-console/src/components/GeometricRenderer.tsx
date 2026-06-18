import { type SVGProps } from "react";

export interface GeometricPoint {
  x: number;
  y: number;
}

export interface GeometricEdgeSegment {
  source: GeometricPoint;
  target: GeometricPoint;
}

type GeometricRendererProps = Omit<SVGProps<SVGSVGElement>, "points"> & {
  points?: GeometricPoint[];
  edges?: GeometricEdgeSegment[];
};

export function GeometricRenderer({ points = [], edges = [], ...props }: GeometricRendererProps) {
  const path =
    points.length > 0
      ? points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ")
      : "M 10 50 L 90 50";

  return (
    <svg viewBox="0 0 100 100" role="img" aria-label="geometric-renderer" {...props}>
      {edges.map((edge, index) => (
        <line
          key={`edge-${index}`}
          x1={edge.source.x}
          y1={edge.source.y}
          x2={edge.target.x}
          y2={edge.target.y}
          stroke="currentColor"
          strokeWidth={1}
          strokeOpacity={0.45}
          data-testid="geometric-renderer-edge"
        />
      ))}
      <path d={path} fill="none" stroke="currentColor" strokeWidth={2} />
    </svg>
  );
}
