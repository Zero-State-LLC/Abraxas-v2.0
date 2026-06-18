import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GeometricOverlayPanel } from './GeometricOverlayPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('GeometricOverlayPanel', () => {
  it('renders bundle-derived geometry', () => {
    render(<GeometricOverlayPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('geometric-overlay-panel')).toBeInTheDocument();
    expect(screen.getByText(/bundle derived/i)).toBeInTheDocument();
    expect(screen.getByTestId('geometric-overlay-svg')).toBeInTheDocument();
  });

  it('renders fallback geometry for empty systems', () => {
    const emptyBundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [],
    };
    render(<GeometricOverlayPanel bundle={emptyBundle} />);

    expect(screen.getByText(/fallback sample/i)).toBeInTheDocument();
  });
});
