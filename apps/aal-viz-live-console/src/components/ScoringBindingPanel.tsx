import { useMemo } from 'react';
import { buildScoringBindingFrame } from '../data/buildScoringBindingFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface ScoringBindingPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatNullableMetric(value: number | null): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function ScoringBindingPanel({ bundle }: ScoringBindingPanelProps): JSX.Element {
  const frame = useMemo(() => buildScoringBindingFrame(bundle), [bundle]);
  const scoredCount = frame.scoring_records.filter((record) => record.scoring_status === 'SCORED').length;
  const notComputableCount = frame.scoring_records.length - scoredCount;
  const previewRecords = frame.scoring_records.slice(0, 8);

  return (
    <section className="scoring-binding-panel" data-testid="scoring-binding-panel" aria-label="AAL-Viz Scoring Binding">
      <div className="scoring-binding-panel__header">
        <span className="scoring-binding-panel__title">RUN LEDGER + BRIER SCORING</span>
        <span className="scoring-binding-panel__notice">
          {frame.authority} · {frame.promotion_policy}
        </span>
      </div>

      <div className="scoring-binding-grid">
        <div className="scoring-binding-section scoring-binding-section--wide" data-testid="scoring-binding-summary">
          <div className="scoring-binding-section__label">SCORING POSTURE</div>
          <div className="scoring-binding-summary-row">
            <span>{frame.scoring_records.length} CLAIM SLOTS</span>
            <span>{scoredCount} SCORED</span>
            <span>{notComputableCount} NOT_COMPUTABLE</span>
            <span>MEAN BRIER {formatNullableMetric(frame.calibration_summary.mean_brier)}</span>
          </div>
          <div className="scoring-binding-section__meta">
            Missing forecast probability or outcome resolution stays NOT_COMPUTABLE.
          </div>
        </div>

        <div className="scoring-binding-section" data-testid="scoring-records">
          <div className="scoring-binding-section__label">FORECAST / OUTCOME JOIN</div>
          <ul className="scoring-binding-list">
            {previewRecords.map((record) => (
              <li className={`scoring-binding-row scoring-binding-row--${record.scoring_status}`} key={record.score_id}>
                <span>{record.subject}</span>
                <span>{record.join_state}</span>
                <strong>{formatNullableMetric(record.brier_score)}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="scoring-binding-section" data-testid="calibration-summary">
          <div className="scoring-binding-section__label">CALIBRATION SUMMARY</div>
          <div className="scoring-binding-metric-grid">
            <span>BUCKETS</span><strong>{frame.calibration_summary.bucket_count}</strong>
            <span>SAMPLE SIZE</span><strong>{frame.calibration_summary.sample_size}</strong>
            <span>MEAN BRIER</span><strong>{formatNullableMetric(frame.calibration_summary.mean_brier)}</strong>
            <span>CALIBRATION ERROR</span><strong>{formatNullableMetric(frame.calibration_summary.calibration_error)}</strong>
          </div>
        </div>

        <div className="scoring-binding-section" data-testid="scoring-locks">
          <div className="scoring-binding-section__label">SCORING LOCKS</div>
          <div className="scoring-binding-metric-grid">
            <span>AUTO PROMOTION</span><strong>{String(frame.scoring_locks.automatic_promotion_allowed).toUpperCase()}</strong>
            <span>EXECUTION AUTHORITY</span><strong>{String(frame.scoring_locks.execution_authority).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.scoring_locks.truth_authority).toUpperCase()}</strong>
            <span>WEIGHT MUTATION</span><strong>{String(frame.scoring_locks.model_weight_mutation_allowed).toUpperCase()}</strong>
            <span>NOTION SCORE WRITE</span><strong>{String(frame.scoring_locks.notion_score_write_enabled).toUpperCase()}</strong>
            <span>WS SCORE BROADCAST</span><strong>{String(frame.scoring_locks.websocket_score_broadcast_enabled).toUpperCase()}</strong>
          </div>
          <div className="scoring-binding-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}

