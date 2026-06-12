import { useMemo } from 'react';
import { buildProviderReliabilityFrame } from '../data/buildProviderReliabilityFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface ProviderReliabilityDashboardProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function ProviderReliabilityDashboard({
  bundle,
  packetsBundle,
}: ProviderReliabilityDashboardProps): JSX.Element {
  const frame = useMemo(() => buildProviderReliabilityFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const underSampled = frame.reliability_scores.filter((score) => score.trust_band === 'UNDER_SAMPLED').length;
  const notComputable = frame.reliability_scores.filter((score) => score.trust_band === 'NOT_COMPUTABLE').length;
  const scorePreview = frame.reliability_scores.slice(0, 6);
  const observationPreview = frame.observations.slice(0, 6);
  const conflictPreview = frame.conflicts.slice(0, 4);
  const firstScore = scorePreview[0] ?? null;

  return (
    <section
      className="provider-reliability-panel"
      data-testid="provider-reliability-dashboard"
      aria-label="AAL-Viz Provider Reliability Scoring"
    >
      <div className="provider-reliability-panel__header">
        <span className="provider-reliability-panel__title">PROVIDER RELIABILITY SCORING</span>
        <span className="provider-reliability-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="provider-reliability-grid">
        <div className="provider-reliability-section provider-reliability-section--wide" data-testid="provider-summary">
          <div className="provider-reliability-section__label">SOURCE RELIABILITY LEDGER</div>
          <div className="provider-summary-row">
            <span>{frame.observations.length} OBSERVATIONS</span>
            <span>{frame.reliability_scores.length} PROVIDERS</span>
            <span>{underSampled} UNDER_SAMPLED</span>
            <span>{frame.conflicts.length} CONFLICTS</span>
          </div>
          <div className="provider-reliability-section__meta">
            Provider reliability affects review priority and visual trust only; it cannot rewrite outcome truth.
          </div>
        </div>

        <div className="provider-reliability-section" data-testid="provider-trust-bands">
          <div className="provider-reliability-section__label">PROVIDER TRUST BANDS</div>
          {scorePreview.length === 0 ? (
            <div className="provider-empty">NO PROVIDER SCORES</div>
          ) : (
            <ul className="provider-list">
              {scorePreview.map((score) => (
                <li className={`provider-row provider-row--${score.trust_band}`} key={score.score_id}>
                  <span>{score.provider_name}</span>
                  <span>{score.observation_count} obs</span>
                  <strong>{score.trust_band}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="provider-reliability-section" data-testid="provider-health-panel">
          <div className="provider-reliability-section__label">PROVIDER HEALTH PANEL</div>
          {observationPreview.length === 0 ? (
            <div className="provider-empty">NO PROVIDER OBSERVATIONS</div>
          ) : (
            <ul className="provider-list">
              {observationPreview.map((observation) => (
                <li className={`provider-row provider-row--${observation.status}`} key={observation.observation_id}>
                  <span>{observation.provider_name}</span>
                  <span>{observation.provenance}</span>
                  <strong>{observation.status}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="provider-reliability-section" data-testid="provider-score-timeline">
          <div className="provider-reliability-section__label">PROVIDER SCORE TIMELINE</div>
          <div className="provider-effect-grid">
            <span>UPTIME RATE</span><strong>{formatMetric(firstScore?.uptime_rate ?? null)}</strong>
            <span>PROVENANCE</span><strong>{formatMetric(firstScore?.provenance_completeness ?? null)}</strong>
            <span>CONFLICT RATE</span><strong>{formatMetric(firstScore?.conflict_rate ?? null)}</strong>
            <span>RELIABILITY</span><strong>{formatMetric(firstScore?.reliability_score ?? null)}</strong>
            <span>NOT COMPUTABLE</span><strong>{notComputable}</strong>
          </div>
        </div>

        <div className="provider-reliability-section" data-testid="provider-conflict-panel">
          <div className="provider-reliability-section__label">PROVIDER CONFLICT PANEL</div>
          {conflictPreview.length === 0 ? (
            <div className="provider-empty">NO PROVIDER CONFLICTS</div>
          ) : (
            <ul className="provider-list">
              {conflictPreview.map((conflict) => (
                <li className="provider-row provider-row--CONFLICTING" key={conflict.conflict_id}>
                  <span>{conflict.target_event_id}</span>
                  <span>{conflict.provider_ids.length} providers</span>
                  <strong>{conflict.conflict_type}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="provider-reliability-section provider-reliability-section--wide" data-testid="provider-locks">
          <div className="provider-reliability-section__label">PROVIDER RELIABILITY LOCKS</div>
          <div className="provider-lock-grid">
            <span>HEALTHCHECK</span><strong>{String(frame.reliability_locks.provider_healthcheck_enabled).toUpperCase()}</strong>
            <span>NOTION WRITE</span><strong>{String(frame.reliability_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.reliability_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.reliability_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.reliability_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>BRIER MUTATION</span><strong>{String(frame.reliability_locks.brier_score_mutation_allowed).toUpperCase()}</strong>
            <span>OUTCOME TRUTH</span><strong>{String(frame.reliability_locks.outcome_truth_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span>
            <strong>{String(frame.reliability_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
          </div>
          <div className="provider-reliability-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
