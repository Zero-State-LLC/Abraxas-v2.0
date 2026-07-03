import type {
  CombinedHealthMigrationArtifactFinding,
  CombinedHealthMigrationArtifactPosture,
} from '../types';
import { AdvisoryNote, PostureBadge, postureVariant } from './StatusPills';

interface CombinedHealthMigrationArtifactPanelProps {
  posture?: CombinedHealthMigrationArtifactPosture;
}

function stageSummaryText(stageSummary: Record<string, number>): string {
  const entries = Object.entries(stageSummary);
  if (entries.length === 0) {
    return 'NO_STAGE_SUMMARY';
  }
  return entries.map(([label, count]) => `${label}:${count}`).join(' | ');
}

function severityVariant(severity: string) {
  if (severity === 'HIGH') return 'red' as const;
  if (severity === 'MEDIUM') return 'gold' as const;
  if (severity === 'LOW') return 'emerald' as const;
  return postureVariant(severity);
}

function FindingList({
  title,
  findings,
}: {
  title: string;
  findings: CombinedHealthMigrationArtifactFinding[];
}): JSX.Element {
  return (
    <div className="posture-section">
      <strong className="posture-section__label">{title}</strong>
      {findings.length === 0 ? (
        <div>NO_FINDINGS</div>
      ) : (
        <ul className="finding-list">
          {findings.map((finding) => (
            <li key={`${finding.source}:${finding.code}`} className="finding-list__item">
              <div className="finding-list__header">
                <strong>{finding.code}</strong>
                <PostureBadge label={finding.severity} variant={severityVariant(finding.severity)} subtle />
              </div>
              <div>{finding.detail}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function CombinedHealthMigrationArtifactPanel({
  posture,
}: CombinedHealthMigrationArtifactPanelProps): JSX.Element {
  const sourceStatus = posture?.source_status ?? 'MISSING';
  const status = posture?.status ?? 'NOT_COMPUTABLE';
  const healthStatus = posture?.health_status ?? 'NOT_COMPUTABLE';
  const migrationStatus = posture?.migration_runner_status ?? 'NOT_COMPUTABLE';
  const artifactStatus = posture?.artifact_lifecycle_status ?? 'NOT_COMPUTABLE';
  const executionResult = posture?.requested_execution_result ?? 'NOT_COMPUTABLE';
  const executionReason =
    posture?.requested_execution_reason ??
    'Combined live projection posture is unavailable in the current advisory bundle.';
  const safeNextSurface = posture?.safe_next_surface ?? 'NOT_COMPUTABLE';
  const recommendedMove =
    posture?.recommended_next_engineering_move ?? 'Rebuild the subsystem health dashboard route.';
  const blockedActionCount = posture?.blocked_action_count ?? 0;
  const blockedActionSample = posture?.blocked_action_sample ?? [];
  const stageCount = posture?.stage_count ?? 0;
  const stageSummary = stageSummaryText(posture?.stage_posture_summary ?? {});
  const subsystemCount = posture?.subsystem_count ?? 0;
  const missingContractCount = posture?.missing_contract_count ?? 0;
  const managedArtifactCount = posture?.managed_artifact_count ?? 0;
  const orphanedArtifactCount = posture?.orphaned_artifact_count ?? 0;
  const ambiguousArtifactCount = posture?.ambiguous_artifact_count ?? 0;
  const blockedContinuityEdgeCount = posture?.blocked_continuity_edge_count ?? 0;
  const findings = posture?.findings_by_source ?? {
    health: [],
    migration: [],
    artifact: [],
  };

  return (
    <div className="panel-block" data-testid="combined-health-migration-artifact-panel">
      <div className="panel-header">
        <span className="panel-icon">+</span>
        COMBINED LIVE POSTURE
      </div>
      <div className="panel-body panel-body--dense">
        <div className="posture-stack" data-testid="combined-health-migration-artifact-badges">
          <PostureBadge label={sourceStatus} />
          <PostureBadge label={status} />
          <PostureBadge label={healthStatus} />
          <PostureBadge label={migrationStatus} />
          <PostureBadge label={artifactStatus} />
        </div>

        <div className="authority-table">
          <div className="authority-table__row">
            <span className="authority-table__key">SOURCE STATUS</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={sourceStatus} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">COMBINED STATUS</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={status} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">HEALTH</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={healthStatus} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">MIGRATION</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={migrationStatus} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">ARTIFACTS</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={artifactStatus} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">SAFE NEXT</span>
            <span className="authority-table__val authority-table__val--false">
              {safeNextSurface}
            </span>
          </div>
        </div>

        <div className="posture-copy posture-copy--muted">{executionReason}</div>

        <div className="posture-section">
          <strong className="posture-section__label">EXECUTION POSTURE</strong>
          <div>
            <PostureBadge label={executionResult} subtle />
          </div>
        </div>
        <div className="posture-section">
          <strong className="posture-section__label">SUMMARY</strong>
          <div className="posture-summary-grid">
            <div>Subsystems: {subsystemCount}</div>
            <div>Missing contracts: {missingContractCount}</div>
            <div>Managed artifacts: {managedArtifactCount}</div>
            <div>Orphaned artifacts: {orphanedArtifactCount}</div>
            <div>Ambiguous artifacts: {ambiguousArtifactCount}</div>
            <div>Blocked continuity edges: {blockedContinuityEdgeCount}</div>
            <div>Blocked actions: {blockedActionCount}</div>
            <div>Stages: {stageCount}</div>
            <div className="posture-summary-grid__wide">Stage posture: {stageSummary}</div>
          </div>
        </div>
        <div className="posture-section">
          <strong className="posture-section__label">BLOCKED AUTHORITY</strong>
          <div>
            {blockedActionSample.length > 0
              ? blockedActionSample.join(' | ')
              : 'NO_BLOCKED_ACTION_SAMPLE'}
          </div>
        </div>
        <FindingList title="HEALTH FINDINGS" findings={findings.health} />
        <FindingList title="MIGRATION FINDINGS" findings={findings.migration} />
        <FindingList title="ARTIFACT FINDINGS" findings={findings.artifact} />
        <div className="posture-section">
          <strong className="posture-section__label">NEXT ENGINEERING MOVE</strong>
          <div>{recommendedMove}</div>
        </div>
        <AdvisoryNote>
          Advisory visibility only. This panel does not run migration logic, classify artifacts,
          or grant authority.
        </AdvisoryNote>
      </div>
    </div>
  );
}
