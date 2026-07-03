import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MigrationRunnerPosturePanel } from './MigrationRunnerPosturePanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

describe('MigrationRunnerPosturePanel', () => {
  it('renders migration runner posture from the bundle', () => {
    render(
      <MigrationRunnerPosturePanel
        posture={sampleProjectionBundle.migration_runner_posture}
      />,
    );

    expect(screen.getByTestId('migration-runner-posture-panel')).toBeInTheDocument();
    expect(
      screen.getByText('CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY'),
    ).toBeInTheDocument();
    expect(screen.getByText(/Advisory visibility only/i)).toBeInTheDocument();
  });

  it('fails closed when migration posture is missing', () => {
    render(<MigrationRunnerPosturePanel />);

    expect(screen.getByText('MISSING')).toBeInTheDocument();
    expect(screen.getAllByText('NOT_COMPUTABLE').length).toBeGreaterThan(0);
    expect(screen.getByText('NO_BLOCKED_ACTION_SAMPLE')).toBeInTheDocument();
  });

  it('does not render any enabled action controls', () => {
    render(
      <MigrationRunnerPosturePanel
        posture={sampleProjectionBundle.migration_runner_posture}
      />,
    );

    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });
});
