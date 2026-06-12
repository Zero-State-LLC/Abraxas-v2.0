import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { ClusterCalibrationPanel } from './ClusterCalibrationPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('ClusterCalibrationPanel', () => {
  it('renders summary, cluster preview, effects, and locks', () => {
    render(<ClusterCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('cluster-calibration-panel')).toBeInTheDocument();
    expect(screen.getByTestId('cluster-calibration-summary')).toBeInTheDocument();
    expect(screen.getByTestId('cluster-calibration-clusters')).toBeInTheDocument();
    expect(screen.getByTestId('cluster-calibration-effects')).toBeInTheDocument();
    expect(screen.getByTestId('cluster-calibration-locks')).toBeInTheDocument();
  });

  it('shows neutral not-computable cluster weather for missing score data', () => {
    render(<ClusterCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('cluster-calibration-summary').textContent).toContain(
      'CLUSTER_CALIBRATION_NOT_COMPUTABLE',
    );
    expect(screen.getByTestId('cluster-calibration-clusters').textContent).toContain('NOT_COMPUTABLE');
    expect(screen.getByTestId('cluster-calibration-effects').textContent).toContain('COHESION1.0000');
    expect(screen.getByTestId('cluster-calibration-effects').textContent).toContain('TURBULENCE0.0000');
  });

  it('does not expose cluster mutation controls or authority-bearing locks as true', () => {
    render(<ClusterCalibrationPanel bundle={sampleProjectionBundle} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('cluster-calibration-locks');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('SCORE MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTHORITY MUTATIONFALSE');
    expect(locks.textContent).toContain('AUTO PROMOTIONFALSE');
    expect(locks.textContent).toContain('EXECUTIONFALSE');
    expect(locks.textContent).toContain('TRUTH AUTHORITYFALSE');
  });
});
