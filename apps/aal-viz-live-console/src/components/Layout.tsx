import type { Dispatch } from 'react';
import type { LiveConsoleState, LiveConsoleAction } from '../state/liveConsoleReducer';
import type { SourceMode } from '../types';
import { StatusPills } from './StatusPills';
import { SystemSpineGrid } from './SystemSpineGrid';
import { SystemDetailPanel } from './SystemDetailPanel';
import { ProjectionPacketInspector } from './ProjectionPacketInspector';
import { LedgerReceiptPanel } from './LedgerReceiptPanel';
import { SignalWeatherPanel } from './SignalWeatherPanel';
import { OperatorReviewQueue } from './OperatorReviewQueue';
import { AuthorityBoundaryPanel } from './AuthorityBoundaryPanel';
import { OperatorActionPacketPanel } from './OperatorActionPacketPanel';

interface LayoutProps {
  state: LiveConsoleState;
  dispatch: Dispatch<LiveConsoleAction>;
}

const SOURCE_MODE_STYLE: Record<SourceMode, { color: string; label: string }> = {
  LIVE_ARTIFACT_BUNDLE: { color: 'var(--clr-emerald)', label: '● LIVE ARTIFACT BUNDLE' },
  SAMPLE_FALLBACK: { color: 'var(--clr-gold)', label: '◌ SAMPLE FALLBACK' },
  FAIL_CLOSED: { color: 'var(--clr-red)', label: '⊘ FAIL CLOSED' },
};

export function Layout({ state, dispatch }: LayoutProps): JSX.Element {
  const { bundle, selectedSystemId, source_mode, fail_closed_reason, packets } = state;
  const selectedSystem =
    selectedSystemId != null
      ? (bundle.systems.find((s) => s.system_id === selectedSystemId) ?? null)
      : null;

  const modeStyle = SOURCE_MODE_STYLE[source_mode];

  return (
    <div className="console-root">
      <header className="console-header">
        <span className="console-title">◈ AAL-VIZ LIVE CONSOLE</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span
            style={{
              fontSize: '10px',
              fontWeight: 700,
              color: modeStyle.color,
              letterSpacing: '0.06em',
            }}
          >
            {modeStyle.label}
          </span>
          {fail_closed_reason != null && (
            <span
              style={{
                fontSize: '9px',
                color: 'var(--clr-red)',
                maxWidth: '260px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {fail_closed_reason}
            </span>
          )}
          <span className="console-subtitle">
            {bundle.schema_version} · {bundle.generated_at}
          </span>
        </span>
      </header>

      <div className="pills-row">
        <StatusPills authority={bundle.authority} sourceMode={source_mode} />
      </div>

      <div className="console-grid">
        <aside className="panel">
          <SystemSpineGrid
            systems={bundle.systems}
            selectedSystemId={selectedSystemId}
            onSelect={(id) => dispatch({ type: 'SELECT_SYSTEM', payload: id })}
          />
        </aside>

        <main className="panel-center">
          <SystemDetailPanel system={selectedSystem} />
          <ProjectionPacketInspector system={selectedSystem} />
          <LedgerReceiptPanel system={selectedSystem} />
          <OperatorActionPacketPanel packetsBundle={packets} />
        </main>

        <aside className="panel-right">
          <SignalWeatherPanel systems={bundle.systems} />
          <OperatorReviewQueue queue={bundle.operator_queue} />
          <AuthorityBoundaryPanel authority={bundle.authority} />
        </aside>
      </div>
    </div>
  );
}
