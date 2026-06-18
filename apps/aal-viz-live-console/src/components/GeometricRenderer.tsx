import { type SVGProps } from "react";

type GeometricRendererProps = Omit<SVGProps<SVGSVGElement>, "points"> & {
  points?: Array<{ x: number; y: number }>;
};

export function GeometricRenderer({ points = [], ...props }: GeometricRendererProps) {
  const path =
    points.length > 0
      ? points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ")
      : "M 10 50 L 90 50";

  return (
    <svg viewBox="0 0 100 100" role="img" aria-label="geometric-renderer" {...props}>
      <path d={path} fill="none" stroke="currentColor" strokeWidth={2} />
    </svg>
  );
}
