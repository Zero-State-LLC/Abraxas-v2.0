import { useMemo } from 'react';
import { buildOperatorDecisionOutcomeFrame } from '../data/buildOperatorDecisionOutcomeFrame';
import type { OperatorActionPacketsBundle } from '../types';

interface OperatorDecisionOutcomePanelProps {
  packetsBundle: OperatorActionPacketsBundle | null;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function OperatorDecisionOutcomePanel({ packetsBundle }: OperatorDecisionOutcomePanelProps): JSX.Element {
  const frame = useMemo(() => buildOperatorDecisionOutcomeFrame(packetsBundle), [packetsBundle]);
  const pending = frame.outcome_attributions.filter((packet) => packet.attribution_status === 'PENDING').length;
  const notComputable = frame.outcome_attributions.filter(
    (packet) => packet.decision_effect === 'NOT_COMPUTABLE',
  ).length;
  const decisionPreview = frame.decision_packets.slice(0, 6);
  const attributionPreview = frame.outcome_attributions.slice(0, 6);
  const firstAttribution = attributionPreview[0] ?? null;

  return (
    <section
      className="operator-decision-outcome-panel"
      data-testid="operator-decision-outcome-panel"
      aria-label="AAL-Viz Operator Decision Packets and Outcome Attribution"
    >
      <div className="operator-decision-outcome-panel__header">
        <span className="operator-decision-outcome-panel__title">OPERATOR DECISIONS + OUTCOME ATTRIBUTION</span>
        <span className="operator-decision-outcome-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="operator-decision-outcome-grid">
        <div
          className="operator-decision-outcome-section operator-decision-outcome-section--wide"
          data-testid="operator-decision-summary"
        >
          <div className="operator-decision-outcome-section__label">DESCRIPTIVE DECISION LOG</div>
          <div className="operator-decision-summary-row">
            <span>{frame.decision_packets.length} DECISIONS</span>
            <span>{frame.outcome_attributions.length} ATTRIBUTIONS</span>
            <span>{pending} PENDING</span>
            <span>{notComputable} NOT_COMPUTABLE</span>
          </div>
          <div className="operator-decision-outcome-section__meta">
            Decision quality is baseline metric minus post-decision metric; missing outcomes stay pending.
          </div>
        </div>

        <div className="operator-decision-outcome-section" data-testid="operator-decision-packets">
          <div className="operator-decision-outcome-section__label">OPERATOR DECISION PACKETS</div>
          {decisionPreview.length === 0 ? (
            <div className="operator-decision-empty">NO OPERATOR DECISION PACKETS</div>
          ) : (
            <ul className="operator-decision-list">
              {decisionPreview.map((packet) => (
                <li className={`operator-decision-row operator-decision-row--${packet.decision_type}`} key={packet.decision_id}>
                  <span>{packet.target_id}</span>
                  <span>{packet.target_type}</span>
                  <strong>{packet.decision_type}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="operator-decision-outcome-section" data-testid="decision-outcome-attributions">
          <div className="operator-decision-outcome-section__label">OUTCOME ATTRIBUTION</div>
          {attributionPreview.length === 0 ? (
            <div className="operator-decision-empty">NO OUTCOME JOINS</div>
          ) : (
            <ul className="operator-decision-list">
              {attributionPreview.map((packet) => (
                <li
                  className={`operator-decision-row operator-decision-row--${packet.attribution_status}`}
                  key={packet.attribution_id}
                >
                  <span>{packet.target_id}</span>
                  <span>{packet.decision_effect}</span>
                  <strong>{packet.attribution_status}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="operator-decision-outcome-section" data-testid="decision-quality-badge">
          <div className="operator-decision-outcome-section__label">DECISION QUALITY BADGE</div>
          <div className="operator-decision-effect-grid">
            <span>CONFIDENCE DELTA</span><strong>{formatMetric(firstAttribution?.confidence_delta ?? null)}</strong>
            <span>BRIER DELTA</span><strong>{formatMetric(firstAttribution?.brier_delta ?? null)}</strong>
            <span>CONTRIBUTION</span><strong>{formatMetric(firstAttribution?.contribution_score ?? null)}</strong>
            <span>QUALITY SCORE</span><strong>{formatMetric(firstAttribution?.decision_quality_score ?? null)}</strong>
            <span>OBSERVED RESULT</span><strong>{firstAttribution?.observed_result ?? 'NOT_COMPUTABLE'}</strong>
          </div>
        </div>

        <div className="operator-decision-outcome-section" data-testid="operator-decision-locks">
          <div className="operator-decision-outcome-section__label">DECISION LOCKS</div>
          <div className="operator-decision-effect-grid">
            <span>NOTION WRITE</span><strong>{String(frame.decision_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.decision_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.decision_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.decision_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.decision_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span>
            <strong>{String(frame.decision_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>AUTHORITY MUTATION</span>
            <strong>{String(frame.decision_locks.authority_tier_mutation_allowed).toUpperCase()}</strong>
          </div>
          <div className="operator-decision-outcome-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
