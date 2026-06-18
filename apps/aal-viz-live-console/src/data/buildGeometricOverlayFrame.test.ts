import { describe, expect, it } from 'vitest';
import { buildFusionOverlayFrame, buildGeometricOverlayFrame } from './buildGeometricOverlayFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

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
  it('derives fusion points from dashboard fusion matrix', () => {
    const frame = buildFusionOverlayFrame(sampleProjectionBundle);

    expect(frame.source_mode).toBe('BUNDLE_DERIVED');
    expect(frame.points.length).toBeGreaterThan(0);
    expect(frame.projection_only).toBe(true);
  });
});
