import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { ScoringBindingPanel } from './ScoringBindingPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('ScoringBindingPanel', () => {
  it('renders scoring posture, join records, calibration summary, and locks', () => {
    render(<ScoringBindingPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('scoring-binding-panel')).toBeInTheDocument();
    expect(screen.getByTestId('scoring-binding-summary')).toBeInTheDocument();
    expect(screen.getByTestId('scoring-records')).toBeInTheDocument();
    expect(screen.getByTestId('calibration-summary')).toBeInTheDocument();
    expect(screen.getByTestId('scoring-locks')).toBeInTheDocument();
  });

  it('keeps missing forecast/outcome scoring not-computable', () => {
    render(<ScoringBindingPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('scoring-binding-summary').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('calibration-summary').textContent).toContain('MEAN BRIERNOT_COMPUTABLE');
    expect(screen.getByTestId('scoring-records').textContent).toContain('NOT_COMPUTABLE');
  });

  it('does not render scoring controls or authority-bearing locks as true', () => {
    render(<ScoringBindingPanel bundle={sampleProjectionBundle} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('scoring-locks');
    expect(locks.textContent).toContain('AUTO PROMOTIONFALSE');
    expect(locks.textContent).toContain('EXECUTION AUTHORITYFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
    expect(locks.textContent).toContain('WEIGHT MUTATIONFALSE');
    expect(locks.textContent).toContain('NOTION SCORE WRITEFALSE');
    expect(locks.textContent).toContain('WS SCORE BROADCASTFALSE');
  });
});

