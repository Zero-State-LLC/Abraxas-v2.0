import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { BrierNodeBehaviorPanel } from './BrierNodeBehaviorPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('BrierNodeBehaviorPanel', () => {
  it('renders summary, behavior preview, effects, and locks', () => {
    render(<BrierNodeBehaviorPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('brier-node-behavior-panel')).toBeInTheDocument();
    expect(screen.getByTestId('brier-node-summary')).toBeInTheDocument();
    expect(screen.getByTestId('brier-node-behaviors')).toBeInTheDocument();
    expect(screen.getByTestId('brier-node-visual-effects')).toBeInTheDocument();
    expect(screen.getByTestId('brier-node-locks')).toBeInTheDocument();
  });

  it('shows neutral calibration-not-computable behavior for missing score data', () => {
    render(<BrierNodeBehaviorPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('brier-node-summary').textContent).toContain('CALIBRATION_NOT_COMPUTABLE');
    expect(screen.getByTestId('brier-node-behaviors').textContent).toContain('CALIBRATION_NOT_COMPUTABLE');
    expect(screen.getByTestId('brier-node-visual-effects').textContent).toContain('STABILITY1.0000');
    expect(screen.getByTestId('brier-node-visual-effects').textContent).toContain('JITTER0.0000');
  });

  it('does not expose behavior mutation controls or authority-bearing locks as true', () => {
    render(<BrierNodeBehaviorPanel bundle={sampleProjectionBundle} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('brier-node-locks');
    expect(locks.textContent).toContain('SCORING MUTATIONFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTHORITY MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTO PROMOTIONFALSE');
    expect(locks.textContent).toContain('AUTO DEMOTIONFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
  });
});

