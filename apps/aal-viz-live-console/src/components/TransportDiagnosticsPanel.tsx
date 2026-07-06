import type { FallbackReason, TransportMode } from '../types';
import type { ConnectionStatus } from '../types';
import { AdvisoryNote, PostureBadge } from './StatusPills';

interface TransportDiagnosticsPanelProps {
  status: ConnectionStatus;
  transportMode: TransportMode;
  reconnectAttempts: number;
  retryDelayMs: number | null;
  lastErrorReason: string | null;
  fallbackReason: FallbackReason;
  lastUpdated: string | null;
}

export function TransportDiagnosticsPanel({
  status,
  transportMode,
  reconnectAttempts,
  retryDelayMs,
  lastErrorReason,
  fallbackReason,
  lastUpdated,
}: TransportDiagnosticsPanelProps): JSX.Element {
  return (
    <div className="panel-block" data-testid="transport-diagnostics-panel">
      <div className="panel-header">
        <span className="panel-icon">○</span>
        TRANSPORT DIAGNOSTICS
      </div>
      <div className="panel-body panel-body--dense">
        <div className="posture-stack" data-testid="transport-diagnostics-badges">
          <PostureBadge label={status} />
          <PostureBadge label={`MODE ${transportMode}`} />
          <PostureBadge label={`RETRIES ${reconnectAttempts}`} />
          <PostureBadge
            label={`RETRY DELAY ${retryDelayMs != null ? `${retryDelayMs}MS` : 'NONE'}`}
          />
        </div>

        <div className="authority-table">
          <div className="authority-table__row">
            <span className="authority-table__key">LAST UPDATED</span>
            <span className="authority-table__val authority-table__val--false">
              {lastUpdated ?? 'NOT_COMPUTABLE'}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">FALLBACK REASON</span>
            <span className="authority-table__val authority-table__val--false">
              {fallbackReason ?? 'NONE'}
            </span>
          </div>
          <div className="authority-table__row">
            <span className="authority-table__key">LAST ERROR</span>
            <span className="authority-table__val authority-table__val--false">
              {lastErrorReason ?? 'NONE'}
            </span>
          </div>
        </div>

        <AdvisoryNote>
          Display-only transport posture. This panel does not open sockets, change polling cadence, or trigger reconnects.
        </AdvisoryNote>
      </div>
    </div>
  );
}
