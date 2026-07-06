import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MigrationPreflightPosturePanel } from './MigrationPreflightPosturePanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

describe('MigrationPreflightPosturePanel', () => {
  it('renders migration preflight posture from the bundle', () => {
    render(
      <MigrationPreflightPosturePanel
        posture={sampleProjectionBundle.migration_preflight_posture}
      />,
    );

    expect(screen.getByTestId('migration-preflight-posture-panel')).toBeInTheDocument();
    expect(
      screen.getAllByText('CONTINUITY NAMESPACE MIGRATION PREFLIGHT READY ADVISORY ONLY')[0],
    ).toBeInTheDocument();
    expect(screen.getByText('12/12 PASS')).toBeInTheDocument();
    expect(screen.getByText('DESIGN_ONLY_HELD')).toBeInTheDocument();
    expect(screen.getByText(/Display-only preflight/i)).toBeInTheDocument();
  });

  it('fails closed when preflight posture is missing', () => {
    render(<MigrationPreflightPosturePanel />);

    expect(screen.getAllByText('MISSING').length).toBeGreaterThan(0);
    expect(screen.getAllByText('NOT COMPUTABLE').length).toBeGreaterThan(0);
    expect(screen.getByText('NO_BLOCKED_ACTION_SAMPLE')).toBeInTheDocument();
  });

  it('does not render any enabled action controls', () => {
    render(
      <MigrationPreflightPosturePanel
        posture={sampleProjectionBundle.migration_preflight_posture}
      />,
    );

    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });
});
