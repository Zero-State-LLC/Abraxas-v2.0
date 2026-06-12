import { useMemo } from 'react';
import { buildStrategyAttributionDriftFrame } from '../data/buildStrategyAttributionDriftFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface StrategyAttributionPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function StrategyAttributionPanel({ bundle }: StrategyAttributionPanelProps): JSX.Element {
  const frame = useMemo(() => buildStrategyAttributionDriftFrame(bundle), [bundle]);
  const notComputable = frame.attribution_packets.filter((packet) => packet.attribution_status === 'NOT_COMPUTABLE').length;
  const underSampled = frame.attribution_packets.filter((packet) => packet.attribution_status === 'UNDER_SAMPLED').length;
  const attributionPreview = frame.attribution_packets.slice(0, 8);
  const driftPreview = frame.drift_packets.slice(0, 8);
  const firstPacket = attributionPreview[0] ?? null;

  return (
    <section
      className="strategy-attribution-panel"
      data-testid="strategy-attribution-panel"
      aria-label="AAL-Viz Strategy Attribution and Domain Drift"
    >
      <div className="strategy-attribution-panel__header">
        <span className="strategy-attribution-panel__title">STRATEGY ATTRIBUTION + DOMAIN DRIFT</span>
        <span className="strategy-attribution-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="strategy-attribution-grid">
        <div
          className="strategy-attribution-section strategy-attribution-section--wide"
          data-testid="strategy-attribution-summary"
        >
          <div className="strategy-attribution-section__label">DESCRIPTIVE ATTRIBUTION LEDGER</div>
          <div className="strategy-attribution-summary-row">
            <span>{frame.attribution_packets.length} ATTRIBUTIONS</span>
            <span>{frame.drift_packets.length} DRIFT WINDOWS</span>
            <span>{underSampled} UNDER_SAMPLED</span>
            <span>{notComputable} NOT_COMPUTABLE</span>
          </div>
          <div className="strategy-attribution-section__meta">
            Contribution score is baseline minus mean Brier; absent baselines stay NOT_COMPUTABLE.
          </div>
        </div>

        <div className="strategy-attribution-section" data-testid="strategy-attribution-packets">
          <div className="strategy-attribution-section__label">STRATEGY ATTRIBUTION</div>
          <ul className="strategy-attribution-list">
            {attributionPreview.map((packet) => (
              <li
                className={`strategy-attribution-row strategy-attribution-row--${packet.attribution_status}`}
                key={packet.attribution_id}
              >
                <span>{packet.strategy_name}</span>
                <span>{packet.signal_family}</span>
                <strong>{packet.attribution_status}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="strategy-attribution-section" data-testid="domain-drift-timeline">
          <div className="strategy-attribution-section__label">DOMAIN SCORE DRIFT</div>
          <ul className="strategy-attribution-list">
            {driftPreview.map((packet) => (
              <li className={`strategy-attribution-row strategy-attribution-row--${packet.drift_direction}`} key={packet.drift_id}>
                <span>{packet.domain}</span>
                <span>{packet.sample_size} samples</span>
                <strong>{packet.drift_direction}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="strategy-attribution-section" data-testid="contribution-score-badge">
          <div className="strategy-attribution-section__label">CONTRIBUTION SCORE BADGE</div>
          <div className="strategy-attribution-effect-grid">
            <span>MEAN BRIER</span><strong>{formatMetric(firstPacket?.mean_brier ?? null)}</strong>
            <span>BASELINE</span><strong>{formatMetric(firstPacket?.baseline_mean_brier ?? null)}</strong>
            <span>BRIER DELTA</span><strong>{formatMetric(firstPacket?.brier_delta ?? null)}</strong>
            <span>CONTRIBUTION</span><strong>{formatMetric(firstPacket?.contribution_score ?? null)}</strong>
            <span>LINEAGE JOIN</span><strong>{firstPacket?.lineage_join_state ?? 'NOT_COMPUTABLE'}</strong>
          </div>
        </div>

        <div className="strategy-attribution-section" data-testid="strategy-attribution-locks">
          <div className="strategy-attribution-section__label">ATTRIBUTION LOCKS</div>
          <div className="strategy-attribution-effect-grid">
            <span>NOTION WRITE</span><strong>{String(frame.attribution_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.attribution_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span>
            <strong>{String(frame.attribution_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.attribution_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.attribution_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>AUTHORITY MUTATION</span>
            <strong>{String(frame.attribution_locks.authority_tier_mutation_allowed).toUpperCase()}</strong>
          </div>
          <div className="strategy-attribution-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
