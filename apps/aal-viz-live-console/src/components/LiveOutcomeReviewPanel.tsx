import { useMemo } from 'react';
import { buildLiveOutcomeReviewFrame } from '../data/buildLiveOutcomeReviewFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface LiveOutcomeReviewPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

export function LiveOutcomeReviewPanel({ bundle, packetsBundle }: LiveOutcomeReviewPanelProps): JSX.Element {
  const frame = useMemo(() => buildLiveOutcomeReviewFrame(bundle, packetsBundle), [bundle, packetsBundle]);
  const openReviewCount = frame.review_items.filter((item) => item.review_status === 'OPEN').length;
  const lowProvenanceCount = frame.review_items.filter((item) => item.review_reason === 'LOW_PROVENANCE').length;
  const pendingCount = frame.review_items.filter((item) => item.review_reason === 'PENDING_RESOLUTION').length;
  const feedPreview = frame.feed_packets.slice(0, 6);
  const reviewPreview = frame.review_items.slice(0, 6);

  return (
    <section
      className="live-outcome-review-panel"
      data-testid="live-outcome-review-panel"
      aria-label="AAL-Viz Live Outcome Feeds and Decision Review Queue"
    >
      <div className="live-outcome-review-panel__header">
        <span className="live-outcome-review-panel__title">LIVE OUTCOMES + REVIEW QUEUE</span>
        <span className="live-outcome-review-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="live-outcome-review-grid">
        <div className="live-outcome-review-section live-outcome-review-section--wide" data-testid="live-outcome-summary">
          <div className="live-outcome-review-section__label">OUTCOME INTAKE REVIEW SURFACE</div>
          <div className="live-outcome-summary-row">
            <span>{frame.feed_packets.length} FEED PACKETS</span>
            <span>{frame.review_items.length} REVIEW ITEMS</span>
            <span>{openReviewCount} OPEN</span>
            <span>{frame.correction_packets.length} CORRECTIONS</span>
          </div>
          <div className="live-outcome-review-section__meta">
            Feed packets are candidate resolutions only; explicit review/correction evidence remains required.
          </div>
        </div>

        <div className="live-outcome-review-section" data-testid="live-outcome-feed">
          <div className="live-outcome-review-section__label">LIVE OUTCOME FEED</div>
          {feedPreview.length === 0 ? (
            <div className="live-outcome-empty">NO LIVE OUTCOME FEED CANDIDATES</div>
          ) : (
            <ul className="live-outcome-list">
              {feedPreview.map((packet) => (
                <li className={`live-outcome-row live-outcome-row--${packet.normalized_status}`} key={packet.feed_packet_id}>
                  <span>{packet.provider_event_id}</span>
                  <span>{packet.provenance}</span>
                  <strong>{packet.normalized_status}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="live-outcome-review-section" data-testid="decision-review-queue">
          <div className="live-outcome-review-section__label">DECISION REVIEW QUEUE</div>
          {reviewPreview.length === 0 ? (
            <div className="live-outcome-empty">NO REVIEW ITEMS</div>
          ) : (
            <ul className="live-outcome-list">
              {reviewPreview.map((item) => (
                <li className={`live-outcome-row live-outcome-row--${item.priority}`} key={item.review_id}>
                  <span>{item.target_id}</span>
                  <span>{item.review_reason}</span>
                  <strong>{item.priority}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="live-outcome-review-section" data-testid="pending-resolution-tracker">
          <div className="live-outcome-review-section__label">PENDING RESOLUTION TRACKER</div>
          <div className="live-outcome-effect-grid">
            <span>PENDING RESOLUTION</span><strong>{pendingCount}</strong>
            <span>LOW PROVENANCE</span><strong>{lowProvenanceCount}</strong>
            <span>STALE ROUTES</span>
            <strong>{String(frame.review_locks.stale_pending_routes_to_review).toUpperCase()}</strong>
            <span>CONFLICT ROUTES</span>
            <strong>{String(frame.review_locks.ambiguous_or_conflicting_routes_to_review).toUpperCase()}</strong>
          </div>
        </div>

        <div className="live-outcome-review-section" data-testid="correction-workflow-panel">
          <div className="live-outcome-review-section__label">CORRECTION WORKFLOW</div>
          <div className="live-outcome-effect-grid">
            <span>CORRECTION PACKETS</span><strong>{frame.correction_packets.length}</strong>
            <span>APPEND ONLY</span><strong>{String(frame.review_locks.append_only_with_correction_packets).toUpperCase()}</strong>
            <span>HASH PRESERVATION</span>
            <strong>{String(frame.review_locks.corrections_preserve_previous_and_corrected_hashes).toUpperCase()}</strong>
            <span>RESOLUTION AUTHORITY</span>
            <strong>{String(frame.review_locks.outcome_resolution_without_review_allowed).toUpperCase()}</strong>
          </div>
        </div>

        <div className="live-outcome-review-section live-outcome-review-section--wide" data-testid="live-outcome-locks">
          <div className="live-outcome-review-section__label">OUTCOME REVIEW LOCKS</div>
          <div className="live-outcome-lock-grid">
            <span>PROVIDER POLLING</span><strong>{String(frame.review_locks.provider_polling_enabled).toUpperCase()}</strong>
            <span>NOTION WRITE</span><strong>{String(frame.review_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.review_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.review_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.review_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.review_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>ROUTING MUTATION</span>
            <strong>{String(frame.review_locks.strategy_routing_mutation_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.review_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="live-outcome-review-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
