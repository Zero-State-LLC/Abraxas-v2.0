import { useMemo } from 'react';
import { buildReviewSuggestionMatrixFrame } from '../data/buildReviewSuggestionMatrixFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface ReviewSuggestionMatrixPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function ReviewSuggestionMatrixPanel({
  bundle,
  packetsBundle,
}: ReviewSuggestionMatrixPanelProps): JSX.Element {
  const frame = useMemo(() => buildReviewSuggestionMatrixFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const critical = frame.suggestions.filter((suggestion) => suggestion.urgency_band === 'CRITICAL').length;
  const high = frame.suggestions.filter((suggestion) => suggestion.urgency_band === 'HIGH').length;
  const suggestionPreview = frame.suggestions.slice(0, 6);
  const providerPreview = frame.provider_matrix.providers.slice(0, 6);

  return (
    <section
      className="review-suggestion-panel"
      data-testid="review-suggestion-matrix-panel"
      aria-label="AAL-Viz Automated Review Suggestions and Provider Comparison Matrix"
    >
      <div className="review-suggestion-panel__header">
        <span className="review-suggestion-panel__title">REVIEW SUGGESTIONS + PROVIDER MATRIX</span>
        <span className="review-suggestion-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="review-suggestion-grid">
        <div className="review-suggestion-section review-suggestion-section--wide" data-testid="review-suggestion-summary">
          <div className="review-suggestion-section__label">ADVISORY REVIEW RECOMMENDATIONS</div>
          <div className="review-suggestion-summary-row">
            <span>{frame.suggestions.length} SUGGESTIONS</span>
            <span>{critical} CRITICAL</span>
            <span>{high} HIGH</span>
            <span>{frame.provider_matrix.providers.length} PROVIDERS</span>
          </div>
          <div className="review-suggestion-section__meta">
            Suggestions require evidence and cannot resolve outcomes, apply corrections, mutate scores, or remove providers.
          </div>
        </div>

        <div className="review-suggestion-section" data-testid="automated-review-suggestions">
          <div className="review-suggestion-section__label">AUTOMATED REVIEW SUGGESTIONS</div>
          {suggestionPreview.length === 0 ? (
            <div className="review-suggestion-empty">NO REVIEW SUGGESTIONS</div>
          ) : (
            <ul className="review-suggestion-list">
              {suggestionPreview.map((suggestion) => (
                <li
                  className={`review-suggestion-row review-suggestion-row--${suggestion.urgency_band}`}
                  key={suggestion.suggestion_id}
                >
                  <span>{suggestion.target_id}</span>
                  <span>{suggestion.suggestion_type}</span>
                  <strong>{suggestion.urgency_band}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="review-suggestion-section" data-testid="provider-comparison-matrix">
          <div className="review-suggestion-section__label">PROVIDER COMPARISON MATRIX</div>
          {providerPreview.length === 0 ? (
            <div className="review-suggestion-empty">NO PROVIDER MATRIX</div>
          ) : (
            <ul className="review-suggestion-list">
              {providerPreview.map((provider) => (
                <li className={`review-suggestion-row review-suggestion-row--${provider.trust_band}`} key={provider.provider_id}>
                  <span>{provider.provider_name}</span>
                  <span>rank {provider.rank ?? 'NC'}</span>
                  <strong>{provider.trust_band}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="review-suggestion-section" data-testid="suggestion-reason-codes">
          <div className="review-suggestion-section__label">REASON CODE LEGEND</div>
          <div className="review-suggestion-effect-grid">
            <span>REASON CODES</span>
            <strong>{String(frame.suggestion_locks.every_suggestion_has_reason_codes).toUpperCase()}</strong>
            <span>REQUIRED EVIDENCE</span>
            <strong>{String(frame.suggestion_locks.every_suggestion_has_required_evidence).toUpperCase()}</strong>
            <span>MATRIX STATUS</span><strong>{frame.provider_matrix.matrix_status}</strong>
            <span>UNDER SAMPLED</span>
            <strong>{String(frame.suggestion_locks.under_sampled_provider_shows_under_sampled).toUpperCase()}</strong>
          </div>
        </div>

        <div className="review-suggestion-section" data-testid="source-redundancy-recommendations">
          <div className="review-suggestion-section__label">SOURCE REDUNDANCY RECOMMENDATIONS</div>
          <div className="review-suggestion-effect-grid">
            <span>TOP PRIORITY</span><strong>{formatMetric(suggestionPreview[0]?.priority_score ?? null)}</strong>
            <span>PROVIDER REMOVAL</span><strong>{String(frame.provider_matrix.provider_removal_authority).toUpperCase()}</strong>
            <span>OUTCOME TRUTH</span><strong>{String(frame.provider_matrix.outcome_truth_authority).toUpperCase()}</strong>
            <span>COMPARISON ONLY</span><strong>{String(frame.provider_matrix.descriptive_comparison_only).toUpperCase()}</strong>
          </div>
        </div>

        <div className="review-suggestion-section review-suggestion-section--wide" data-testid="review-suggestion-locks">
          <div className="review-suggestion-section__label">SUGGESTION + MATRIX LOCKS</div>
          <div className="review-suggestion-lock-grid">
            <span>NOTION WRITE</span><strong>{String(frame.suggestion_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.suggestion_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.suggestion_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>OUTCOME RESOLVE</span><strong>{String(frame.suggestion_locks.outcome_resolution_allowed).toUpperCase()}</strong>
            <span>CORRECTION APPLY</span><strong>{String(frame.suggestion_locks.correction_application_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.suggestion_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.suggestion_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span>
            <strong>{String(frame.suggestion_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
          </div>
          <div className="review-suggestion-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
