import { lazy, Suspense, useState, type Dispatch, type KeyboardEvent } from 'react';
import type { LiveConsoleState, LiveConsoleAction } from '../state/liveConsoleReducer';
import type { ConnectionStatus, SourceMode } from '../types';
import { PostureBadge, StatusPills, type PillVariant } from './StatusPills';
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
import { MigrationPreflightPosturePanel } from './MigrationPreflightPosturePanel';
import { CombinedHealthMigrationArtifactPanel } from './CombinedHealthMigrationArtifactPanel';
import { TransportDiagnosticsPanel } from './TransportDiagnosticsPanel';
import { OPERATOR_PLATFORM_VIEWS, type OperatorPlatformView } from './operatorPlatformNavigation';
import { OperatorPlatformSimpleViewPanel } from './OperatorPlatformSimpleViews';
import type { OperatorPlatformGraphState } from './OperatorPlatformViews';

const OperatorPlatformGraphViewPanel = lazy(async () => {
  const module = await import('./OperatorPlatformViews');
  return { default: module.OperatorPlatformGraphViewPanel };
});
const OperatorPlatformChangesView = lazy(() => import('./OperatorPlatformChangesView'));
const OperatorPlatformAlertsView = lazy(() => import('./OperatorPlatformAlertsView'));

interface LayoutProps {
  state: LiveConsoleState;
  dispatch: Dispatch<LiveConsoleAction>;
}

const SOURCE_MODE_STYLE: Record<SourceMode, { label: string; variant: PillVariant }> = {
  LIVE_ARTIFACT_BUNDLE: { label: 'LIVE ARTIFACT BUNDLE', variant: 'emerald' },
  SAMPLE_FALLBACK: { label: 'SAMPLE FALLBACK', variant: 'gold' },
  FAIL_CLOSED: { label: 'FAIL CLOSED', variant: 'red' },
};

const CONNECTION_STYLE: Record<ConnectionStatus, { label: string; variant: PillVariant }> = {
  CONNECTING: { label: 'CONNECTING', variant: 'gold' },
  LIVE_STREAM: { label: 'LIVE STREAM', variant: 'emerald' },
  POLLING_FALLBACK: { label: 'POLLING FALLBACK', variant: 'gold' },
  SAMPLE_FALLBACK: { label: 'SAMPLE FALLBACK', variant: 'gold' },
  FAIL_CLOSED: { label: 'FAIL CLOSED', variant: 'red' },
};

export function Layout({ state, dispatch }: LayoutProps): JSX.Element {
  const [activeView, setActiveView] = useState<OperatorPlatformView>('status');
  const [graphState, setGraphState] = useState<OperatorPlatformGraphState>({
    yggQuery: '',
    yggSelectedNodeClasses: ['INTERFACE', 'ROUTE', 'RUNE', 'SYSTEM'],
    yggSelectedEdgeClasses: ['BINDS', 'CONSUMES', 'EVIDENCES', 'EXPOSES', 'PRODUCES', 'REFERENCES', 'RENDER_RELATION', 'ROUTES_TO', 'VALIDATES'],
    yggSelectedProvenance: ['INFERRED', 'OBSERVED'],
    yggSelectedConfidence: ['INFERRED', 'NOT_COMPUTABLE', 'SUPPORTED', 'VERIFIED'],
    yggSelectedRoles: ['OPERATOR'],
    yggSelectedId: null,
    yggTraversalDepth: 1,
    yggPathTargetId: null,
    yggDiffOverlay: true,
    yggIntegritySeverities: ['HIGH', 'INFO', 'LOW', 'MEDIUM', 'NOT_COMPUTABLE'],
    yggIntegrityTypes: ['GENERATION_MISMATCH', 'INFERRED_LINK', 'MISSING_EVIDENCE', 'SECTION_NOT_COMPUTABLE', 'SOURCE_INTEGRITY_GAP', 'STALE_ENTITY', 'TEMPORAL_REMOVAL', 'TEMPORAL_WEAKENING', 'UNRESOLVED_ENTITY'],
    yggAlertOverlay: true,
    yggSelectedAlertId: null,
    contractQuery: '',
    contractSelectedId: null,
  });
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
  const platform = bundle.operator_platform;
  const platformStatus = platform.system_status.payload;
  const platformDiff = platform.temporal_diff.payload;
  const integrity = bundle.yggdrasil_topology_integrity;
  const integritySummary = integrity?.payload?.summary;
  const alerts = bundle.route_receipt_advisory_alerts;
  const onTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number): void => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    const nextIndex = (index + direction + OPERATOR_PLATFORM_VIEWS.length) % OPERATOR_PLATFORM_VIEWS.length;
    const next = OPERATOR_PLATFORM_VIEWS[nextIndex];
    setActiveView(next.id);
    document.getElementById(`operator-tab-${next.id}`)?.focus();
  };

  return (
    <div className="console-root">
      <header className="console-header">
        <span className="console-title">AAL-VIZ LIVE CONSOLE</span>
        <span className="console-header__meta">
          <PostureBadge
            label={modeStyle.label}
            variant={modeStyle.variant}
            subtle
            testId="source-mode-indicator"
          />
          <PostureBadge
            label={
              connection_reconnect_attempts > 0
                ? `${connectionStyle.label} RETRIES ${connection_reconnect_attempts}`
                : connectionStyle.label
            }
            variant={connectionStyle.variant}
            subtle
            testId="connection-status-indicator"
          />
          {fail_closed_reason != null && (
            <span className="console-header__fail-reason">{fail_closed_reason}</span>
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

      <div className="pills-row">
        <StatusPills
          authority={bundle.authority}
          sourceMode={source_mode}
          connectionStatus={connection_status}
        />
      </div>

      <nav className="operator-tabs" role="tablist" aria-label="Operator platform views">
        {OPERATOR_PLATFORM_VIEWS.map((view, index) => (
          <button
            id={`operator-tab-${view.id}`}
            key={view.id}
            type="button"
            role="tab"
            aria-selected={activeView === view.id}
            aria-controls={`operator-panel-${view.id}`}
            tabIndex={activeView === view.id ? 0 : -1}
            onClick={() => setActiveView(view.id)}
            onKeyDown={(event) => onTabKeyDown(event, index)}
          >
            {view.label}
          </button>
        ))}
      </nav>

      {activeView === 'status' ? (
        <div
          className="operator-tab-panel"
          id="operator-panel-status"
          role="tabpanel"
          aria-labelledby="operator-tab-status"
        >
          <section className="status-overview" aria-label="System status overview">
            <div><span>Stabilization</span><strong>{platformStatus?.stabilization_status ?? 'NOT_COMPUTABLE'}</strong></div>
            <div><span>Systems ready</span><strong>{platformStatus?.ready_system_count ?? 0} / {platformStatus?.system_count ?? 0}</strong></div>
            <div><span>Receipts indexed</span><strong>{platformStatus?.receipt_count ?? 0}</strong></div>
            <div><span>Current changes</span><strong>{platformDiff?.total_change_count ?? 0}</strong></div>
            <div><span>Inherited debt</span><strong>{platformStatus?.inherited_debt.length ?? 0}</strong></div>
          </section>
          <section className="integrity-status-summary" aria-label="YGGDRASIL topology integrity">
            <div>
              <span>Topology integrity</span>
              <strong>{integrity?.status ?? 'NOT_COMPUTABLE'}</strong>
            </div>
            <div><span>High</span><strong>{integritySummary?.severity_counts.HIGH ?? 0}</strong></div>
            <div><span>Medium</span><strong>{integritySummary?.severity_counts.MEDIUM ?? 0}</strong></div>
            <div><span>Affected entities</span><strong>{integritySummary?.affected_entity_count ?? 0}</strong></div>
            <div><span>Not computable</span><strong>{integritySummary?.non_computable_count ?? 0}</strong></div>
          </section>
          <section className="alert-status-summary" aria-label="Advisory alert summary">
            <div><span>Advisory alerts</span><strong>{alerts?.status ?? 'NOT_COMPUTABLE'}</strong></div>
            <div><span>Active</span><strong>{alerts?.summary.active_count ?? 0}</strong></div>
            <div><span>Resolved</span><strong>{alerts?.summary.resolved_count ?? 0}</strong></div>
            <div><span>Suppressed</span><strong>{alerts?.summary.suppressed_count ?? 0}</strong></div>
            <div><span>Published receipts</span><strong>{alerts?.summary.published_receipt_count ?? 0}</strong></div>
          </section>
          {(platformStatus?.operator_summary.length ?? 0) > 0 && (
            <div className="operator-summary-line">{platformStatus?.operator_summary.join(' · ')}</div>
          )}
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
          <TransportDiagnosticsPanel
            status={connection_status}
            transportMode={connection_transport_mode}
            reconnectAttempts={connection_reconnect_attempts}
            retryDelayMs={connection_retry_delay_ms}
            lastErrorReason={connection_last_error_reason}
            fallbackReason={connection_fallback_reason}
            lastUpdated={connection_last_updated}
          />
          <CombinedHealthMigrationArtifactPanel
            posture={bundle.combined_health_migration_artifact_posture}
          />
          <MigrationPreflightPosturePanel posture={bundle.migration_preflight_posture} />
          <MigrationRunnerPosturePanel posture={bundle.migration_runner_posture} />
          <AuthorityBoundaryPanel authority={bundle.authority} />
        </aside>
          </div>
        </div>
      ) : (
        <div
          className="operator-tab-panel"
          id={`operator-panel-${activeView}`}
          role="tabpanel"
          aria-labelledby={`operator-tab-${activeView}`}
        >
          {activeView === 'production' || activeView === 'evidence' ? (
            <OperatorPlatformSimpleViewPanel view={activeView} platform={platform} />
          ) : (
            <Suspense fallback={<div className="operator-loading" role="status">Loading operator view...</div>}>
              {activeView === 'changes' ? (
                <OperatorPlatformChangesView
                  platform={platform}
                  deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
                />
              ) : activeView === 'alerts' ? (
                <OperatorPlatformAlertsView
                  alerts={alerts}
                  deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
                  onOpenInYggdrasil={(alertId, entityId) => {
                    setGraphState({ ...graphState, yggSelectedAlertId: alertId, yggSelectedId: entityId, yggAlertOverlay: true });
                    setActiveView('yggdrasil');
                  }}
                />
              ) : (
                <OperatorPlatformGraphViewPanel
                  view={activeView}
                  platform={platform}
                  topologyProjection={bundle.yggdrasil_topology}
                  integrityProjection={bundle.yggdrasil_topology_integrity}
                  deltaIntelligence={bundle.yggdrasil_topology_delta_intelligence}
                  advisoryAlerts={alerts}
                  graphState={graphState}
                  onGraphStateChange={setGraphState}
                />
              )}
            </Suspense>
          )}
        </div>
      )}
    </div>
  );
}
