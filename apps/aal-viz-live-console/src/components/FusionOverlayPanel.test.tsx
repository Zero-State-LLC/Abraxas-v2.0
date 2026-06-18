import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FusionOverlayPanel } from './FusionOverlayPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

describe('FusionOverlayPanel', () => {
  it('renders bundle-derived fusion overlay', () => {
    render(<FusionOverlayPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('fusion-overlay-panel')).toBeInTheDocument();
    expect(screen.getByText(/bundle derived/i)).toBeInTheDocument();
    expect(screen.getByTestId('fusion-overlay-svg')).toBeInTheDocument();
  });
});
