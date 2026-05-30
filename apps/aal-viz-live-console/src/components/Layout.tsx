import type { Dispatch } from 'react';
import type { LiveConsoleState, LiveConsoleAction } from '../state/liveConsoleReducer';
import { StatusPills } from './StatusPills';
import { SystemSpineGrid } from './SystemSpineGrid';
import { SystemDetailPanel } from './SystemDetailPanel';
import { ProjectionPacketInspector } from './ProjectionPacketInspector';
import { LedgerReceiptPanel } from './LedgerReceiptPanel';
import { SignalWeatherPanel } from './SignalWeatherPanel';
import { OperatorReviewQueue } from './OperatorReviewQueue';
import { AuthorityBoundaryPanel } from './AuthorityBoundaryPanel';

interface LayoutProps {
  state: LiveConsoleState;
  dispatch: Dispatch<LiveConsoleAction>;
}

export function Layout({ state, dispatch }: LayoutProps): JSX.Element {
  const { bundle, selectedSystemId } = state;
  const selectedSystem =
    selectedSystemId != null
      ? (bundle.systems.find((s) => s.system_id === selectedSystemId) ?? null)
      : null;

  return (
    <div className="console-root">
      <header className="console-header">
        <span className="console-title">◈ AAL-VIZ LIVE CONSOLE</span>
        <span className="console-subtitle">
          {bundle.schema_version} · {bundle.generated_at}
        </span>
      </header>

      <div className="pills-row">
        <StatusPills authority={bundle.authority} />
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
