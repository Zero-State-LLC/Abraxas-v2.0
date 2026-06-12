import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { DynamicMetricDashboardPanel } from './DynamicMetricDashboardPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

afterEach(cleanup);

describe('DynamicMetricDashboardPanel', () => {
  it('renders the dashboard frame and all required sections', () => {
    render(<DynamicMetricDashboardPanel bundle={sampleProjectionBundle} />);

    expect(screen.getByTestId('dynamic-metric-dashboard-panel')).toBeInTheDocument();
    expect(screen.getByTestId('metric-core-strip')).toBeInTheDocument();
    expect(screen.getByTestId('metric-delta-tracker')).toBeInTheDocument();
    expect(screen.getByTestId('metric-candidate-panel')).toBeInTheDocument();
    expect(screen.getByTestId('metric-system-fusion')).toBeInTheDocument();
    expect(screen.getByTestId('metric-afe-run-stream')).toBeInTheDocument();
    expect(screen.getByTestId('metric-oracle-feed')).toBeInTheDocument();
    expect(screen.getByTestId('metric-shadow-feed')).toBeInTheDocument();
    expect(screen.getByTestId('metric-overlay-preview')).toBeInTheDocument();
    expect(screen.getByTestId('metric-compliance-monitor')).toBeInTheDocument();
  });

  it('renders all core and candidate metrics', () => {
    render(<DynamicMetricDashboardPanel bundle={sampleProjectionBundle} />);

    for (const metric of ['SDR', 'MSI', 'RFR', 'ARF', 'NMC']) {
      expect(screen.getByTestId(`core-metric-${metric}`)).toBeInTheDocument();
    }
    for (const metric of ['HCI', 'ATI', 'MRI', 'IPI', 'SFI']) {
      expect(screen.getByTestId(`candidate-metric-${metric}`)).toBeInTheDocument();
    }
  });

  it('shows candidate metrics as stabilization-required and non-promoting', () => {
    render(<DynamicMetricDashboardPanel bundle={sampleProjectionBundle} />);

    for (const metric of ['HCI', 'ATI', 'MRI', 'IPI', 'SFI']) {
      expect(screen.getByTestId(`candidate-metric-${metric}`).textContent).toContain(
        'STABILIZATION_REQUIRED',
      );
      expect(screen.getByTestId(`candidate-metric-${metric}`).textContent).toContain(
        'PROMOTION_FALSE',
      );
    }
  });

  it('shows non-filtering compliance with no filter, suppression, rewrite, or panel hiding calls', () => {
    render(<DynamicMetricDashboardPanel bundle={sampleProjectionBundle} />);
    const monitor = screen.getByTestId('metric-compliance-monitor');

    expect(monitor.textContent).toContain('OUTPUT PRESERVEDTRUE');
    expect(monitor.textContent).toContain('ANNOTATION ONLYTRUE');
    expect(monitor.textContent).toContain('FILTER CALLS DETECTEDFALSE');
    expect(monitor.textContent).toContain('SUPPRESSION CALLS DETECTEDFALSE');
    expect(monitor.textContent).toContain('REWRITE CALLS DETECTEDFALSE');
    expect(monitor.textContent).toContain('PANEL HIDING DETECTEDFALSE');
  });

  it('does not render enabled action buttons', () => {
    render(<DynamicMetricDashboardPanel bundle={sampleProjectionBundle} />);
    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });
});
