import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { ProviderReliabilityDashboard } from './ProviderReliabilityDashboard';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

function bundleWithProviderOutcomes(): LiveConsoleProjectionBundle {
  return {
    ...sampleProjectionBundle,
    systems: [
      {
        ...sampleProjectionBundle.systems[0],
        system_id: 'provider_alpha',
        projection_packets: [
          {
            packet_id: 'shared-event-001',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
          {
            packet_id: 'alpha-event-002',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
          {
            packet_id: 'alpha-event-003',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
        ],
      },
      {
        ...sampleProjectionBundle.systems[1],
        system_id: 'provider_beta',
        projection_packets: [
          {
            packet_id: 'shared-event-001',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'AMBIGUOUS',
            display_value: null,
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
        ],
      },
    ],
  };
}

afterEach(cleanup);

describe('ProviderReliabilityDashboard', () => {
  it('renders summary, trust bands, health panel, score timeline, conflicts, and locks', () => {
    render(<ProviderReliabilityDashboard bundle={bundleWithProviderOutcomes()} packetsBundle={null} />);

    expect(screen.getByTestId('provider-reliability-dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('provider-summary')).toBeInTheDocument();
    expect(screen.getByTestId('provider-trust-bands')).toBeInTheDocument();
    expect(screen.getByTestId('provider-health-panel')).toBeInTheDocument();
    expect(screen.getByTestId('provider-score-timeline')).toBeInTheDocument();
    expect(screen.getByTestId('provider-conflict-panel')).toBeInTheDocument();
    expect(screen.getByTestId('provider-locks')).toBeInTheDocument();
  });

  it('shows provider trust bands and conflicts as visual/review-only state', () => {
    render(<ProviderReliabilityDashboard bundle={bundleWithProviderOutcomes()} packetsBundle={null} />);

    expect(screen.getByTestId('provider-summary').textContent).toContain('CONFLICTS');
    expect(screen.getByTestId('provider-trust-bands').textContent).toContain('UNDER_SAMPLED');
    expect(screen.getByTestId('provider-conflict-panel').textContent).toContain('RESULT_MISMATCH');
  });

  it('does not expose controls or authority-bearing locks as true', () => {
    render(<ProviderReliabilityDashboard bundle={bundleWithProviderOutcomes()} packetsBundle={null} />);

    expect(screen.queryAllByRole('button')).toHaveLength(0);
    const locks = screen.getByTestId('provider-locks');
    expect(locks.textContent).toContain('HEALTHCHECKFALSE');
    expect(locks.textContent).toContain('NOTION WRITEFALSE');
    expect(locks.textContent).toContain('WEBSOCKETFALSE');
    expect(locks.textContent).toContain('AUTO EXECUTIONFALSE');
    expect(locks.textContent).toContain('FORECAST MUTATIONFALSE');
    expect(locks.textContent).toContain('BRIER MUTATIONFALSE');
    expect(locks.textContent).toContain('OUTCOME TRUTHFALSE');
    expect(locks.textContent).toContain('ROUTING MUTATIONFALSE');
  });
});
