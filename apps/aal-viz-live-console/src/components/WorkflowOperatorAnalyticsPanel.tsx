import { useMemo } from 'react';
import { buildWorkflowOperatorAnalyticsFrame } from '../data/buildWorkflowOperatorAnalyticsFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface WorkflowOperatorAnalyticsPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

function formatRate(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : `${Math.round(value * 100)}%`;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function WorkflowOperatorAnalyticsPanel({
  bundle,
  packetsBundle,
}: WorkflowOperatorAnalyticsPanelProps): JSX.Element {
  const frame = useMemo(() => buildWorkflowOperatorAnalyticsFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const analytics = frame.workflow_analytics;
  const operator = frame.operator_performance[0] ?? null;

  return (
    <section
      className="workflow-analytics-panel"
      data-testid="workflow-operator-analytics-panel"
      aria-label="AAL-Viz Workflow Analytics and Operator Performance"
    >
      <div className="workflow-analytics-panel__header">
        <span className="workflow-analytics-panel__title">WORKFLOW ANALYTICS + OPERATOR PERFORMANCE</span>
        <span className="workflow-analytics-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="workflow-analytics-grid">
        <div className="workflow-analytics-section workflow-analytics-section--wide" data-testid="workflow-analytics-summary">
          <div className="workflow-analytics-section__label">DESCRIPTIVE ANALYTICS</div>
          <div className="workflow-analytics-summary-row">
            <span>{analytics.workflow_count} WORKFLOWS</span>
            <span>{analytics.completed_count} COMPLETED</span>
            <span>{analytics.blocked_count} BLOCKED</span>
            <span>{analytics.analytics_status}</span>
          </div>
          <div className="workflow-analytics-section__meta">
            Analytics are feedback-only and cannot promote, demote, execute, route, score, or mutate records.
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="workflow-bottleneck-panel">
          <div className="workflow-analytics-section__label">WORKFLOW BOTTLENECK</div>
          <div className="workflow-analytics-metric-grid">
            <span>BOTTLENECK STEP</span><strong>{analytics.bottleneck_step}</strong>
            <span>TRIAGE LATENCY</span><strong>{analytics.mean_time_to_triage_ms ?? 'NOT_COMPUTABLE'}</strong>
            <span>DECISION LATENCY</span><strong>{analytics.mean_time_to_decision_ms ?? 'NOT_COMPUTABLE'}</strong>
            <span>COMMIT LATENCY</span><strong>{analytics.mean_time_to_commit_ms ?? 'NOT_COMPUTABLE'}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="review-aging-panel">
          <div className="workflow-analytics-section__label">REVIEW AGING</div>
          <div className="workflow-analytics-metric-grid">
            <span>STALE REVIEW RATE</span><strong>{formatRate(analytics.stale_review_rate)}</strong>
            <span>NOT COMPUTABLE</span><strong>{analytics.not_computable_count}</strong>
            <span>DISMISSED</span><strong>{analytics.dismissed_count}</strong>
            <span>WINDOWED</span><strong>{String(frame.analytics_locks.windowed_and_timestamped).toUpperCase()}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="suggestion-effectiveness-panel">
          <div className="workflow-analytics-section__label">SUGGESTION EFFECTIVENESS</div>
          <div className="workflow-analytics-metric-grid">
            <span>ACCEPTANCE RATE</span><strong>{formatRate(analytics.suggestion_acceptance_rate)}</strong>
            <span>CORRECTION RATE</span><strong>{formatRate(analytics.correction_rate)}</strong>
            <span>LOW SAMPLE GUARD</span><strong>{String(frame.analytics_locks.low_sample_size_renders_under_sampled).toUpperCase()}</strong>
            <span>PENDING NOT SCORED</span>
            <strong>{String(frame.analytics_locks.pending_decisions_not_scored_positive_or_negative).toUpperCase()}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="operator-performance-dashboard">
          <div className="workflow-analytics-section__label">OPERATOR PERFORMANCE FEEDBACK</div>
          {operator == null ? (
            <div className="workflow-analytics-empty">NO OPERATOR PERFORMANCE</div>
          ) : (
            <div className="workflow-analytics-metric-grid">
              <span>OPERATOR</span><strong>{operator.operator_id}</strong>
              <span>REVIEWED</span><strong>{operator.reviewed_count}</strong>
              <span>EVIDENCE RATE</span><strong>{formatRate(operator.evidence_completion_rate)}</strong>
              <span>STATUS</span><strong>{operator.performance_status}</strong>
            </div>
          )}
        </div>

        <div className="workflow-analytics-section" data-testid="operator-calibration-panel">
          <div className="workflow-analytics-section__label">OPERATOR CALIBRATION</div>
          <div className="workflow-analytics-metric-grid">
            <span>QUALITY SCORE</span><strong>{formatMetric(operator?.mean_decision_quality_score ?? null)}</strong>
            <span>CALIBRATION ERROR</span><strong>{formatMetric(operator?.operator_calibration_error ?? null)}</strong>
            <span>RANK AUTHORITY</span><strong>{String(operator?.rank_authority ?? false).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(operator?.truth_authority ?? false).toUpperCase()}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="override-outcome-panel">
          <div className="workflow-analytics-section__label">OVERRIDE OUTCOME TRACKING</div>
          <div className="workflow-analytics-metric-grid">
            <span>OVERRIDES</span><strong>{operator?.override_count ?? 0}</strong>
            <span>POSITIVE</span><strong>{formatRate(operator?.positive_decision_rate ?? null)}</strong>
            <span>NEGATIVE</span><strong>{formatRate(operator?.negative_decision_rate ?? null)}</strong>
            <span>PENDING</span><strong>{formatRate(operator?.pending_decision_rate ?? null)}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section" data-testid="correction-quality-panel">
          <div className="workflow-analytics-section__label">CORRECTION QUALITY TRACKING</div>
          <div className="workflow-analytics-metric-grid">
            <span>CORRECTIONS</span><strong>{operator?.correction_count ?? 0}</strong>
            <span>HASH PRESERVATION</span>
            <strong>{String(frame.analytics_locks.prior_and_corrected_hashes_preserved).toUpperCase()}</strong>
            <span>OUTCOME MUTATION</span><strong>{String(frame.analytics_locks.outcome_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.analytics_locks.score_mutation_allowed).toUpperCase()}</strong>
          </div>
        </div>

        <div className="workflow-analytics-section workflow-analytics-section--wide" data-testid="operator-feedback-visual-mapping">
          <div className="workflow-analytics-section__label">AAL-VIZ VISUAL OVERLAYS</div>
          <div className="workflow-analytics-visual-grid">
            {Object.entries(frame.visual_mapping).map(([key, effect]) => (
              <span key={key}>{key}: {effect}</span>
            ))}
          </div>
        </div>

        <div className="workflow-analytics-section workflow-analytics-section--wide" data-testid="workflow-analytics-locks">
          <div className="workflow-analytics-section__label">ANALYTICS LOCKS</div>
          <div className="workflow-analytics-lock-grid">
            <span>NOTION WRITE</span><strong>{String(frame.analytics_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.analytics_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.analytics_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>PROMOTION</span><strong>{String(frame.analytics_locks.promotion_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span><strong>{String(frame.analytics_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>PROVIDER AUTHORITY</span>
            <strong>{String(frame.analytics_locks.provider_authority_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span><strong>{String(frame.analytics_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.analytics_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="workflow-analytics-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
