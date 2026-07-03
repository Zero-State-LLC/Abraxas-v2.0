import type { MigrationRunnerPosture } from '../types';
import { AdvisoryNote, PostureBadge } from './StatusPills';

interface MigrationRunnerPosturePanelProps {
  posture?: MigrationRunnerPosture;
}

function stageSummaryText(stageSummary: Record<string, number>): string {
  const entries = Object.entries(stageSummary);
  if (entries.length === 0) {
    return 'NO_STAGE_SUMMARY';
  }
  return entries.map(([label, count]) => `${label}:${count}`).join(' · ');
}

export function MigrationRunnerPosturePanel({
  posture,
}: MigrationRunnerPosturePanelProps): JSX.Element {
  const sourceStatus = posture?.source_status ?? 'MISSING';
  const status = posture?.status ?? 'NOT_COMPUTABLE';
  const executionResult = posture?.requested_execution_result ?? 'NOT_COMPUTABLE';
  const executionReason =
    posture?.requested_execution_reason ??
    'Migration runner posture is unavailable in the current advisory bundle.';
  const safeNextSurface = posture?.safe_next_surface ?? 'NOT_COMPUTABLE';
  const recommendedMove =
    posture?.recommended_next_engineering_move ?? 'Rebuild the dashboard receipt route.';
  const blockedActionCount = posture?.blocked_action_count ?? 0;
  const blockedActionSample = posture?.blocked_action_sample ?? [];
  const stageCount = posture?.stage_count ?? 0;
  const stageSummary = stageSummaryText(posture?.stage_posture_summary ?? {});

  return (
    <div className="panel-block" data-testid="migration-runner-posture-panel">
      <div className="panel-header">
        <span className="panel-icon">○</span>
        CONTINUITY MIGRATION RUNNER
      </div>
      <div className="panel-body panel-body--dense">
        <div className="posture-stack" data-testid="migration-runner-posture-badges">
          <PostureBadge label={sourceStatus} />
          <PostureBadge label={status} />
          <PostureBadge label={executionResult} />
          <PostureBadge label={`${blockedActionCount} BLOCKED ACTIONS`} />
          <PostureBadge label={`${stageCount} STAGES`} />
        </div>

        <div className="authority-table">
          <div className="authority-table__row">
            <span className="authority-table__key">SOURCE STATUS</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={sourceStatus} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">RUNNER STATUS</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={status} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">EXECUTION POSTURE</span>
            <span className="authority-table__val authority-table__val--false">
              <PostureBadge label={executionResult} subtle />
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">RUN ID</span>
            <span className="authority-table__val authority-table__val--false">
              {posture?.migration_run_id ?? 'NOT_COMPUTABLE'}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">BLOCKED ACTIONS</span>
            <span className="authority-table__val authority-table__val--false">
              {blockedActionCount}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">STAGES</span>
            <span className="authority-table__val authority-table__val--false">{stageCount}</span>
          </div>
        </div>

        <div className="posture-copy posture-copy--muted">{executionReason}</div>

        <div className="posture-section">
          <strong className="posture-section__label">SAFE NEXT SURFACE</strong>
          <div>{safeNextSurface}</div>
        </div>
        <div className="posture-section">
          <strong className="posture-section__label">STAGE POSTURE</strong>
          <div>{stageSummary}</div>
        </div>
        <div className="posture-section">
          <strong className="posture-section__label">BLOCKED AUTHORITY</strong>
          <div>
            {blockedActionSample.length > 0
              ? blockedActionSample.join(' · ')
              : 'NO_BLOCKED_ACTION_SAMPLE'}
          </div>
        </div>
        <div className="posture-section">
          <strong className="posture-section__label">NEXT ENGINEERING MOVE</strong>
          <div>{recommendedMove}</div>
        </div>

        <AdvisoryNote>
          Advisory visibility only. This panel does not run migration logic or grant authority.
        </AdvisoryNote>
      </div>
    </div>
  );
}
