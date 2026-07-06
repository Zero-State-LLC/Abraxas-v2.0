import type { MigrationPreflightPosture } from '../types';
import { AdvisoryNote, PostureBadge } from './StatusPills';

interface MigrationPreflightPosturePanelProps {
  posture?: MigrationPreflightPosture;
}

export function MigrationPreflightPosturePanel({
  posture,
}: MigrationPreflightPosturePanelProps): JSX.Element {
  const sourceStatus = posture?.source_status ?? 'MISSING';
  const status = posture?.status ?? 'NOT_COMPUTABLE';
  const passCount = posture?.pass_count ?? 0;
  const heldCount = posture?.held_count ?? 0;
  const checkCount = posture?.check_count ?? 0;
  const blockedActionCount = posture?.blocked_action_count ?? 0;
  const blockedActionSample = posture?.blocked_action_sample ?? [];
  const recommendedMove =
    posture?.recommended_next_engineering_move ??
    'Rebuild the continuity namespace migration preflight receipt.';

  return (
    <div className="panel-block" data-testid="migration-preflight-posture-panel">
      <div className="panel-header">
        <span className="panel-icon">○</span>
        MIGRATION PREFLIGHT
      </div>
      <div className="panel-body panel-body--dense">
        <div className="posture-stack" data-testid="migration-preflight-posture-badges">
          <PostureBadge label={sourceStatus} />
          <PostureBadge label={status} />
          <PostureBadge label={`${passCount}/${checkCount} PASS`} />
          <PostureBadge label={`${heldCount} HELD`} />
          <PostureBadge label={`${blockedActionCount} BLOCKED`} />
        </div>

        <div className="authority-table">
          <div className="authority-table__row">
            <span className="authority-table__key">RUNNER STATUS</span>
            <span className="authority-table__val authority-table__val--false">
              {posture?.migration_runner_status ?? 'NOT_COMPUTABLE'}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">ALIAS DESIGN</span>
            <span className="authority-table__val authority-table__val--false">
              {posture?.alias_design_state ?? 'NOT_COMPUTABLE'}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">IMPLEMENTATION</span>
            <span className="authority-table__val authority-table__val--false">
              {posture?.valid_for_implementation === false ? 'HELD' : 'NOT_COMPUTABLE'}
            </span>
          </div>
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
          Display-only preflight. This panel does not materialize aliases, rename paths, or execute migration logic.
        </AdvisoryNote>
      </div>
    </div>
  );
}
