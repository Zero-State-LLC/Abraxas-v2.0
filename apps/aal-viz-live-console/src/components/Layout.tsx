import type { Dispatch } from 'react';
import type { LiveConsoleState, LiveConsoleAction } from '../state/liveConsoleReducer';
import type { ConnectionStatus, SourceMode } from '../types';
import { StatusPills } from './StatusPills';
import { SystemSpineGrid } from './SystemSpineGrid';
import { SystemDetailPanel } from './SystemDetailPanel';
import { ProjectionPacketInspector } from './ProjectionPacketInspector';
import { LedgerReceiptPanel } from './LedgerReceiptPanel';
import { SignalWeatherPanel } from './SignalWeatherPanel';
import { OperatorReviewQueue } from './OperatorReviewQueue';
import { AuthorityBoundaryPanel } from './AuthorityBoundaryPanel';
import { OperatorActionPacketPanel } from './OperatorActionPacketPanel';
import { OperatorWorkflowPanel } from './OperatorWorkflowPanel';
import { EvidenceChecklistPanel } from './EvidenceChecklistPanel';
import { DecisionAttributionPanel } from './DecisionAttributionPanel';
import { SuggestionCardsPanel } from './SuggestionCardsPanel';
import { WorkflowAnalyticsPanel } from './WorkflowAnalyticsPanel';
import { PacketDiffViewerPanel } from './PacketDiffViewerPanel';
import { DynamicMetricDashboardPanel } from './DynamicMetricDashboardPanel';
import { LineageRelationshipOverlayPanel } from './LineageRelationshipOverlayPanel';
import { PacketBindingLayerPanel } from './PacketBindingLayerPanel';
import { ScoringBindingPanel } from './ScoringBindingPanel';
import { BrierNodeBehaviorPanel } from './BrierNodeBehaviorPanel';
import { ClusterCalibrationPanel } from './ClusterCalibrationPanel';
import { TemporalCalibrationPanel } from './TemporalCalibrationPanel';
import { StrategyAttributionPanel } from './StrategyAttributionPanel';
import { OperatorDecisionOutcomePanel } from './OperatorDecisionOutcomePanel';
import { LiveOutcomeReviewPanel } from './LiveOutcomeReviewPanel';
import { ProviderReliabilityDashboard } from './ProviderReliabilityDashboard';
import { ReviewSuggestionMatrixPanel } from './ReviewSuggestionMatrixPanel';
import { OperatorWorkflowCommandCenterPanel } from './OperatorWorkflowCommandCenterPanel';
import { WorkflowOperatorAnalyticsPanel } from './WorkflowOperatorAnalyticsPanel';
import { AnalyticsNarrativeSummaryPanel } from './AnalyticsNarrativeSummaryPanel';
import { CinematicBriefingPanel } from './CinematicBriefingPanel';
import { GeometricOverlayPanel } from './GeometricOverlayPanel';
import { FusionOverlayPanel } from './FusionOverlayPanel';
import { OperatorNarrativeReportPanel } from './OperatorNarrativeReportPanel';
import { MigrationRunnerPosturePanel } from './MigrationRunnerPosturePanel';
import { CombinedHealthMigrationArtifactPanel } from './CombinedHealthMigrationArtifactPanel';

interface LayoutProps {
  state: LiveConsoleState;
  dispatch: Dispatch<LiveConsoleAction>;
}

const SOURCE_MODE_STYLE: Record<SourceMode, { color: string; label: string }> = {
  LIVE_ARTIFACT_BUNDLE: { color: 'var(--clr-emerald)', label: '● LIVE ARTIFACT BUNDLE' },
  SAMPLE_FALLBACK: { color: 'var(--clr-gold)', label: '◌ SAMPLE FALLBACK' },
  FAIL_CLOSED: { color: 'var(--clr-red)', label: '⊘ FAIL CLOSED' },
};

const CONNECTION_STYLE: Record<ConnectionStatus, { color: string; label: string }> = {
  CONNECTING: { color: 'var(--clr-gold)', label: 'CONNECTING' },
  LIVE_STREAM: { color: 'var(--clr-emerald)', label: 'LIVE STREAM' },
  POLLING_FALLBACK: { color: 'var(--clr-gold)', label: 'POLLING FALLBACK' },
  SAMPLE_FALLBACK: { color: 'var(--clr-gold)', label: 'SAMPLE FALLBACK' },
  FAIL_CLOSED: { color: 'var(--clr-red)', label: 'FAIL CLOSED' },
};

function formatDiagnosticLabel(value: string | null): string {
  if (value == null || value === '') {
    return 'NONE';
  }
  return value.split('_').join(' ');
}

export function Layout({ state, dispatch }: LayoutProps): JSX.Element {
  const {
    bundle,
    selectedSystemId,
    source_mode,
    fail_closed_reason,
    packets,
    connection_status,
    connection_last_updated,
    connection_reconnect_attempts,
    connection_retry_delay_ms,
    connection_transport_mode,
    connection_last_error_reason,
    connection_fallback_reason,
  } = state;
  const selectedSystem =
    selectedSystemId != null
      ? (bundle.systems.find((s) => s.system_id === selectedSystemId) ?? null)
      : null;

  const modeStyle = SOURCE_MODE_STYLE[source_mode];
  const connectionStyle = CONNECTION_STYLE[connection_status];

  return (
    <div className="console-root">
      <header className="console-header">
        <span className="console-title">◈ AAL-VIZ LIVE CONSOLE</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span
            data-testid="source-mode-indicator"
            style={{
              fontSize: '10px',
              fontWeight: 700,
              color: modeStyle.color,
              letterSpacing: '0.06em',
            }}
          >
            {modeStyle.label}
          </span>
          <span
            data-testid="connection-status-indicator"
            style={{
              fontSize: '10px',
              fontWeight: 700,
              color: connectionStyle.color,
              letterSpacing: '0.06em',
            }}
          >
            {connectionStyle.label}
            {connection_reconnect_attempts > 0
              ? ` Â· RETRIES ${connection_reconnect_attempts}`
              : ''}
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

      {connection_last_updated != null && (
        <div className="feed-status-row" data-testid="feed-status-row">
          FEED {connection_last_updated}
        </div>
      )}

      <div
        className="feed-status-row"
        data-testid="feed-transport-details"
        style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}
      >
        <span>TRANSPORT {formatDiagnosticLabel(connection_transport_mode)}</span>
        <span>FALLBACK {formatDiagnosticLabel(connection_fallback_reason)}</span>
        <span>LAST ERROR {formatDiagnosticLabel(connection_last_error_reason)}</span>
        <span>
          RETRY DELAY {connection_retry_delay_ms != null ? `${connection_retry_delay_ms}ms` : 'NONE'}
        </span>
      </div>

      <div className="pills-row">
        <StatusPills
          authority={bundle.authority}
          sourceMode={source_mode}
          connectionStatus={connection_status}
        />
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
          <DynamicMetricDashboardPanel bundle={bundle} />
          <LineageRelationshipOverlayPanel bundle={bundle} />
          <PacketBindingLayerPanel bundle={bundle} />
          <ScoringBindingPanel bundle={bundle} />
          <BrierNodeBehaviorPanel bundle={bundle} />
          <ClusterCalibrationPanel bundle={bundle} />
          <TemporalCalibrationPanel bundle={bundle} />
          <StrategyAttributionPanel bundle={bundle} />
          <OperatorDecisionOutcomePanel packetsBundle={packets} />
          <LiveOutcomeReviewPanel bundle={bundle} packetsBundle={packets} />
          <ProviderReliabilityDashboard bundle={bundle} packetsBundle={packets} />
          <ReviewSuggestionMatrixPanel bundle={bundle} packetsBundle={packets} />
          <OperatorWorkflowCommandCenterPanel bundle={bundle} packetsBundle={packets} />
          <WorkflowOperatorAnalyticsPanel bundle={bundle} packetsBundle={packets} />
          <AnalyticsNarrativeSummaryPanel bundle={bundle} packetsBundle={packets} />
          <CinematicBriefingPanel bundle={bundle} packetsBundle={packets} />
          <GeometricOverlayPanel bundle={bundle} />
          <FusionOverlayPanel bundle={bundle} />
          <OperatorNarrativeReportPanel bundle={bundle} />
          <SystemDetailPanel system={selectedSystem} />
          <ProjectionPacketInspector system={selectedSystem} />
          <LedgerReceiptPanel system={selectedSystem} />
          <OperatorActionPacketPanel packetsBundle={packets} />
          <OperatorWorkflowPanel packetsBundle={packets} />
          <EvidenceChecklistPanel packetsBundle={packets} />
          <DecisionAttributionPanel packetsBundle={packets} />
          <SuggestionCardsPanel packetsBundle={packets} />
          <WorkflowAnalyticsPanel packetsBundle={packets} />
          <PacketDiffViewerPanel packetsBundle={packets} />
        </main>

        <aside className="panel-right">
          <SignalWeatherPanel systems={bundle.systems} />
          <OperatorReviewQueue queue={bundle.operator_queue} />
          <CombinedHealthMigrationArtifactPanel
            posture={bundle.combined_health_migration_artifact_posture}
          />
          <MigrationRunnerPosturePanel posture={bundle.migration_runner_posture} />
          <AuthorityBoundaryPanel authority={bundle.authority} />
        </aside>
      </div>
    </div>
  );
}
