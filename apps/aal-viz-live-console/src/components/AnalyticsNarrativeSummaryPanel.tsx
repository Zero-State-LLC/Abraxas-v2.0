import { useMemo } from 'react';
import { buildAnalyticsNarrativeSummaryFrame } from '../data/buildAnalyticsNarrativeSummaryFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface AnalyticsNarrativeSummaryPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

export function AnalyticsNarrativeSummaryPanel({
  bundle,
  packetsBundle,
}: AnalyticsNarrativeSummaryPanelProps): JSX.Element {
  const frame = useMemo(() => buildAnalyticsNarrativeSummaryFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const narrative = frame.narrative_packet;

  return (
    <section
      className="narrative-summary-panel"
      data-testid="analytics-narrative-summary-panel"
      aria-label="AAL-Viz Analytics Narrative Summary"
    >
      <div className="narrative-summary-panel__header">
        <span className="narrative-summary-panel__title">ANALYTICS NARRATIVE SUMMARY</span>
        <span className="narrative-summary-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="narrative-summary-grid">
        <div className="narrative-summary-section narrative-summary-section--wide" data-testid="narrative-briefing-card">
          <div className="narrative-summary-section__label">BRIEFING CARD</div>
          <div className="narrative-briefing-card">
            <strong>{narrative.headline}</strong>
            <span>{narrative.summary}</span>
            <span>{narrative.severity_band} · {narrative.narrative_type} · {narrative.authority}</span>
          </div>
          <div className="narrative-summary-section__meta">
            Narrative summaries compress analytics only; they do not create facts or execute actions.
          </div>
        </div>

        <div className="narrative-summary-section" data-testid="narrative-findings">
          <div className="narrative-summary-section__label">PROVENANCE-LABELED FINDINGS</div>
          {narrative.key_findings.map((finding) => (
            <div className={`narrative-finding narrative-finding--${finding.provenance}`} key={finding.finding_id}>
              <strong>{finding.label}</strong>
              <span>{finding.claim}</span>
              <span>{finding.provenance} · confidence {finding.confidence.toFixed(2)}</span>
            </div>
          ))}
        </div>

        <div className="narrative-summary-section" data-testid="narrative-template-rules">
          <div className="narrative-summary-section__label">DETERMINISTIC TEMPLATE RULES</div>
          {frame.template_rules.map((rule) => (
            <div className="narrative-template-rule" key={rule.template_id}>
              <span>{rule.input_metric_type} · {rule.output_block_type}</span>
              <strong>{rule.provenance_rule}</strong>
            </div>
          ))}
        </div>

        <div className="narrative-summary-section" data-testid="narrative-gap-list">
          <div className="narrative-summary-section__label">NARRATIVE GAP LIST</div>
          {narrative.not_computable_items.length === 0 ? (
            <div className="narrative-empty">NO NOT_COMPUTABLE GAPS</div>
          ) : (
            <ul className="narrative-list">
              {narrative.not_computable_items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="narrative-summary-section" data-testid="narrative-review-prompts">
          <div className="narrative-summary-section__label">REVIEW PROMPTS ONLY</div>
          {narrative.recommended_review_items.length === 0 ? (
            <div className="narrative-empty">NO REVIEW PROMPTS</div>
          ) : (
            <ul className="narrative-list">
              {narrative.recommended_review_items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="narrative-summary-section narrative-summary-section--wide" data-testid="narrative-generation-flow">
          <div className="narrative-summary-section__label">SUMMARY GENERATION FLOW</div>
          <div className="narrative-flow">
            {frame.generation_flow.map((step) => (
              <span key={step}>{step}</span>
            ))}
          </div>
        </div>

        <div className="narrative-summary-section" data-testid="narrative-source-packets">
          <div className="narrative-summary-section__label">SOURCE PACKETS</div>
          <div className="narrative-source-grid">
            {narrative.source_packet_ids.map((sourceId) => (
              <span key={sourceId}>{sourceId}</span>
            ))}
          </div>
        </div>

        <div className="narrative-summary-section" data-testid="narrative-confidence-rules">
          <div className="narrative-summary-section__label">CONFIDENCE + PROVENANCE</div>
          <div className="narrative-metric-grid">
            <span>FINDING SOURCES</span>
            <strong>{String(frame.narrative_locks.every_finding_has_source_metric_ids).toUpperCase()}</strong>
            <span>INFERRED LABELED</span>
            <strong>{String(frame.narrative_locks.inferred_claims_labeled_inferred).toUpperCase()}</strong>
            <span>CONFIDENCE CAPPED</span>
            <strong>{String(frame.narrative_locks.confidence_capped_by_evidence_class).toUpperCase()}</strong>
          </div>
        </div>

        <div className="narrative-summary-section narrative-summary-section--wide" data-testid="narrative-summary-locks">
          <div className="narrative-summary-section__label">NARRATIVE LOCKS</div>
          <div className="narrative-lock-grid">
            <span>NOTION WRITE</span><strong>{String(frame.narrative_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.narrative_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.narrative_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>OUTCOME RESOLVE</span><strong>{String(frame.narrative_locks.outcome_resolution_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.narrative_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.narrative_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span><strong>{String(frame.narrative_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.narrative_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="narrative-summary-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
