import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CombinedHealthMigrationArtifactPanel } from './CombinedHealthMigrationArtifactPanel';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';

describe('CombinedHealthMigrationArtifactPanel', () => {
  it('renders combined posture from the bundle', () => {
    render(
      <CombinedHealthMigrationArtifactPanel
        posture={sampleProjectionBundle.combined_health_migration_artifact_posture}
      />,
    );

    expect(screen.getByTestId('combined-health-migration-artifact-panel')).toBeInTheDocument();
    expect(screen.getByText('READY_WITH_FINDINGS')).toBeInTheDocument();
    expect(screen.getByText('SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY')).toBeInTheDocument();
    expect(
      screen.getByText('CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY'),
    ).toBeInTheDocument();
    expect(screen.getByText('ADVISORY_ONLY')).toBeInTheDocument();
    expect(screen.getByText(/Advisory visibility only/i)).toBeInTheDocument();
  });

  it('renders degraded posture when the combined source is missing', () => {
    render(<CombinedHealthMigrationArtifactPanel />);

    expect(screen.getByText('MISSING')).toBeInTheDocument();
    expect(screen.getAllByText('NOT_COMPUTABLE').length).toBeGreaterThan(0);
    expect(screen.getByText('NO_BLOCKED_ACTION_SAMPLE')).toBeInTheDocument();
    expect(screen.getAllByText('NO_FINDINGS')).toHaveLength(3);
  });

  it('renders grouped drilldown findings and no action controls', () => {
    render(
      <CombinedHealthMigrationArtifactPanel
        posture={sampleProjectionBundle.combined_health_migration_artifact_posture}
      />,
    );

    expect(screen.getByText('HEALTH FINDINGS')).toBeInTheDocument();
    expect(screen.getByText('MIGRATION FINDINGS')).toBeInTheDocument();
    expect(screen.getByText('ARTIFACT FINDINGS')).toBeInTheDocument();
    expect(screen.queryAllByRole('button')).toHaveLength(0);
  });
});
