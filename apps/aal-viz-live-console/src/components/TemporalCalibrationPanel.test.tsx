import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { TemporalCalibrationPanel } from './TemporalCalibrationPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('TemporalCalibrationPanel', () => {
  it('renders summary, timeline preview, curves, and locks', () => {
    render(<TemporalCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('temporal-calibration-panel')).toBeInTheDocument();
    expect(screen.getByTestId('temporal-calibration-summary')).toBeInTheDocument();
    expect(screen.getByTestId('temporal-calibration-timelines')).toBeInTheDocument();
    expect(screen.getByTestId('temporal-calibration-curves')).toBeInTheDocument();
    expect(screen.getByTestId('temporal-calibration-locks')).toBeInTheDocument();
  });

  it('shows temporal gaps and not-computable badges for missing score windows', () => {
    render(<TemporalCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('temporal-calibration-summary').textContent).toContain('TEMPORAL GAPS');
    expect(screen.getByTestId('temporal-calibration-timelines').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('temporal-calibration-curves').textContent).toContain('COHESION1.0000');
    expect(screen.getByTestId('temporal-calibration-curves').textContent).toContain('TURBULENCE0.0000');
  });

  it('does not expose playback controls or authority-bearing locks as true', () => {
    render(<TemporalCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('temporal-calibration-locks');
    expect(locks.textContent).toContain('PLAYBACK CONTROLSFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTHORITY MUTATIONFALSE');
    expect(locks.textContent).toContain('EXECUTIONFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
  });
});
