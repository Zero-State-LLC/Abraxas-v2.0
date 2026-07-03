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
    expect(screen.getAllByText('READY WITH FINDINGS')[0]).toBeInTheDocument();
    expect(
      screen.getAllByText('SUBSYSTEM HEALTH DASHBOARD READY ADVISORY ONLY')[0],
    ).toBeInTheDocument();
    expect(
      screen.getAllByText('CONTINUITY NAMESPACE MIGRATION RUNNER READY ADVISORY ONLY')[0],
    ).toBeInTheDocument();
    expect(screen.getAllByText('ADVISORY ONLY').length).toBeGreaterThan(0);
    expect(screen.getByTestId('combined-health-migration-artifact-badges')).toBeInTheDocument();
    expect(screen.getByText(/Advisory visibility only/i)).toBeInTheDocument();
    expect(screen.getAllByText('ADVISORY ONLY').length).toBeGreaterThan(0);
  });

  it('renders degraded posture when the combined source is missing', () => {
    render(<CombinedHealthMigrationArtifactPanel />);

    expect(screen.getAllByText('MISSING').length).toBeGreaterThan(0);
    expect(screen.getAllByText('NOT COMPUTABLE').length).toBeGreaterThan(0);
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
