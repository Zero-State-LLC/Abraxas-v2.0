import type { MigrationRunnerPosture } from '../types';

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
        <span className="panel-icon">◫</span>
        CONTINUITY MIGRATION RUNNER
      </div>
      <div className="panel-body">
        <div className="authority-table">
          <div className="authority-table__row">
            <span className="authority-table__key">SOURCE STATUS</span>
            <span className="authority-table__val authority-table__val--false">{sourceStatus}</span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">RUNNER STATUS</span>
            <span className="authority-table__val authority-table__val--false">{status}</span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">EXECUTION POSTURE</span>
            <span className="authority-table__val authority-table__val--false">
              {executionResult}
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
        <div style={{ marginTop: '8px', fontSize: '10px', color: 'var(--clr-text-muted)' }}>
          {executionReason}
        </div>
        <div style={{ marginTop: '8px', fontSize: '10px' }}>
          <strong>SAFE NEXT SURFACE</strong>
          <div>{safeNextSurface}</div>
        </div>
        <div style={{ marginTop: '8px', fontSize: '10px' }}>
          <strong>STAGE POSTURE</strong>
          <div>{stageSummary}</div>
        </div>
        <div style={{ marginTop: '8px', fontSize: '10px' }}>
          <strong>BLOCKED AUTHORITY</strong>
          <div>
            {blockedActionSample.length > 0
              ? blockedActionSample.join(' · ')
              : 'NO_BLOCKED_ACTION_SAMPLE'}
          </div>
        </div>
        <div style={{ marginTop: '8px', fontSize: '10px' }}>
          <strong>NEXT ENGINEERING MOVE</strong>
          <div>{recommendedMove}</div>
        </div>
        <div
          style={{
            marginTop: '10px',
            fontSize: '9px',
            color: 'var(--clr-text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          Advisory visibility only. This panel does not run migration logic or grant authority.
        </div>
      </div>
    </div>
  );
}
