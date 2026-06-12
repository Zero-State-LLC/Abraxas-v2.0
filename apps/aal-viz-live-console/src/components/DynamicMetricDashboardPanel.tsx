import { useMemo } from 'react';
import { buildMetricDashboardFrame } from '../data/buildMetricDashboardFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface DynamicMetricDashboardPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatDelta(value: number): string {
  if (value > 0) return `+${value.toFixed(2)}`;
  return value.toFixed(2);
}

export function DynamicMetricDashboardPanel({
  bundle,
}: DynamicMetricDashboardPanelProps): JSX.Element {
  const frame = useMemo(() => buildMetricDashboardFrame(bundle), [bundle]);
  const compliance = frame.non_filtering_compliance_monitor;

  return (
    <section
      className="metric-dashboard-panel"
      data-testid="dynamic-metric-dashboard-panel"
      aria-label="ABX Dynamic Metric Dashboard"
    >
      <div className="metric-dashboard-panel__header">
        <span className="metric-dashboard-panel__title">ABX DYNAMIC METRIC DASHBOARD</span>
        <span className="metric-dashboard-panel__notice">
          {frame.authority} · {frame.output_effect}
        </span>
      </div>

      <div className="metric-dashboard-grid" data-testid="metric-dashboard-panels">
        <div className="metric-section metric-section--wide" data-testid="metric-core-strip">
          <div className="metric-section__label">CORE ABX METRIC STRIP</div>
          <div className="metric-strip">
            {frame.core_metrics.map((metric) => (
              <div className="metric-tile" key={metric.metric} data-testid={`core-metric-${metric.metric}`}>
                <span className="metric-tile__key">{metric.metric}</span>
                <span className="metric-tile__value">{metric.value.toFixed(2)}</span>
                <span className="metric-tile__hint">{metric.definition}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="metric-section" data-testid="metric-delta-tracker">
          <div className="metric-section__label">DELTA TRACKER</div>
          <div className="metric-section__meta">
            {frame.previous_batch_id} to {frame.batch_id}
          </div>
          <ul className="metric-list">
            {frame.delta.map((delta) => (
              <li className="metric-list__row" key={delta.metric} data-testid={`metric-delta-${delta.metric}`}>
                <span>{delta.metric}</span>
                <span>{formatDelta(delta.value)}</span>
                <span className={`metric-state metric-state--${delta.state}`}>{delta.state}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="metric-section" data-testid="metric-candidate-panel">
          <div className="metric-section__label">DYNAMIC METRIC EXPANSION</div>
          <div className="candidate-grid">
            {frame.candidate_metrics.map((metric) => (
              <div className="candidate-card" key={metric.metric} data-testid={`candidate-metric-${metric.metric}`}>
                <span className="candidate-card__key">{metric.metric}</span>
                <span className="candidate-card__value">{metric.value.toFixed(2)}</span>
                <span className="candidate-card__meaning">{metric.meaning}</span>
                <span className="candidate-card__lock">STABILIZATION_REQUIRED · PROMOTION_FALSE</span>
              </div>
            ))}
          </div>
        </div>

        <div className="metric-section" data-testid="metric-system-fusion">
          <div className="metric-section__label">SYSTEM FUSION MATRIX</div>
          <ul className="fusion-list">
            {frame.system_fusion_matrix.map((row) => (
              <li className="fusion-list__row" key={row.system}>
                <span className="fusion-list__system">{row.system}</span>
                <span>{row.metric_contribution}</span>
                <span>{row.use}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="metric-section" data-testid="metric-afe-run-stream">
          <div className="metric-section__label">AFE RUN STREAM</div>
          <div className="metric-feed">
            {frame.afe_run_stream.length === 0 ? (
              <span className="metric-feed__empty">NO AFE PACKETS LOADED</span>
            ) : (
              frame.afe_run_stream.map((packet) => (
                <span className="metric-feed__item" key={packet.packet_id}>{packet.packet_type}</span>
              ))
            )}
          </div>
        </div>

        <div className="metric-section" data-testid="metric-oracle-feed">
          <div className="metric-section__label">ORACLE ANNOTATION FEED</div>
          <div className="metric-feed">
            {frame.oracle_annotation_feed.length === 0 ? (
              <span className="metric-feed__empty">NO ORACLE ANNOTATIONS LOADED</span>
            ) : (
              frame.oracle_annotation_feed.map((packet) => (
                <span className="metric-feed__item" key={packet.packet_id}>{packet.packet_type}</span>
              ))
            )}
          </div>
        </div>

        <div className="metric-section" data-testid="metric-shadow-feed">
          <div className="metric-section__label">SHADOW DRIFT FEED</div>
          <div className="metric-feed">
            {frame.shadow_observation_feed.map((packet) => (
              <span className="metric-feed__item" key={packet.packet_id}>{packet.status}</span>
            ))}
          </div>
        </div>

        <div className="metric-section" data-testid="metric-overlay-preview">
          <div className="metric-section__label">AAL-VIZ OVERLAY PREVIEW</div>
          <div className="overlay-chip-list">
            {frame.aal_viz_overlay_preview.map((projection) => (
              <span className="overlay-chip" key={projection}>{projection}</span>
            ))}
          </div>
          <div className="metric-section__meta">MAX OPACITY {frame.rendering_locks.max_overlay_opacity}</div>
        </div>

        <div className="metric-section" data-testid="metric-compliance-monitor">
          <div className="metric-section__label">NON-FILTERING COMPLIANCE MONITOR</div>
          <div className="compliance-grid">
            <span>OUTPUT PRESERVED</span><strong>{String(compliance.output_preserved).toUpperCase()}</strong>
            <span>ANNOTATION ONLY</span><strong>{String(compliance.annotation_only).toUpperCase()}</strong>
            <span>FILTER CALLS DETECTED</span><strong>{String(compliance.filter_calls_detected).toUpperCase()}</strong>
            <span>SUPPRESSION CALLS DETECTED</span><strong>{String(compliance.suppression_calls_detected).toUpperCase()}</strong>
            <span>REWRITE CALLS DETECTED</span><strong>{String(compliance.rewrite_calls_detected).toUpperCase()}</strong>
            <span>PANEL HIDING DETECTED</span><strong>{String(compliance.panel_hiding_detected).toUpperCase()}</strong>
          </div>
          <div className="metric-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
