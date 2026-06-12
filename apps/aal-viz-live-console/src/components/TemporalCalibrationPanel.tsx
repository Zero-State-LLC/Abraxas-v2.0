import { useMemo } from 'react';
import { buildTemporalCalibrationAnimationFrame } from '../data/buildTemporalCalibrationAnimationFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface TemporalCalibrationPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatMetric(value: number | null | undefined): string {
  return value == null ? 'NOT_COMPUTABLE' : value.toFixed(4);
}

export function TemporalCalibrationPanel({ bundle }: TemporalCalibrationPanelProps): JSX.Element {
  const frame = useMemo(() => buildTemporalCalibrationAnimationFrame(bundle), [bundle]);
  const gapCount = frame.timelines.reduce((sum, timeline) => sum + timeline.gap_markers.length, 0);
  const preview = frame.timelines.slice(0, 8);
  const firstTimeline = preview[0] ?? null;

  return (
    <section
      className="temporal-calibration-panel"
      data-testid="temporal-calibration-panel"
      aria-label="AAL-Viz Temporal Calibration Animation"
    >
      <div className="temporal-calibration-panel__header">
        <span className="temporal-calibration-panel__title">TEMPORAL CALIBRATION ANIMATION</span>
        <span className="temporal-calibration-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="temporal-calibration-grid">
        <div
          className="temporal-calibration-section temporal-calibration-section--wide"
          data-testid="temporal-calibration-summary"
        >
          <div className="temporal-calibration-section__label">STATIC TEMPORAL SUMMARY</div>
          <div className="temporal-calibration-summary-row">
            <span>{frame.timelines.length} TIMELINES</span>
            <span>{gapCount} TEMPORAL GAPS</span>
            <span>SNAPSHOT MODE</span>
            <span>NO CERTAINTY INTERPOLATION</span>
          </div>
          <div className="temporal-calibration-section__meta">
            Animation fields are descriptive only; accessibility mode exposes this static table first.
          </div>
        </div>

        <div className="temporal-calibration-section" data-testid="temporal-calibration-timelines">
          <div className="temporal-calibration-section__label">TIMELINE PREVIEW</div>
          <ul className="temporal-calibration-list">
            {preview.map((timeline) => (
              <li
                className={`temporal-calibration-row temporal-calibration-row--${timeline.animation_badge}`}
                key={timeline.timeline_id}
              >
                <span>{timeline.entity_id}</span>
                <span>{timeline.playback.mode}</span>
                <strong>{timeline.animation_badge}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="temporal-calibration-section" data-testid="temporal-calibration-curves">
          <div className="temporal-calibration-section__label">CURRENT CURVE SNAPSHOT</div>
          <div className="temporal-calibration-effect-grid">
            <span>COHESION</span><strong>{formatMetric(firstTimeline?.temporal_cohesion_curve[0])}</strong>
            <span>TURBULENCE</span><strong>{formatMetric(firstTimeline?.turbulence_curve[0])}</strong>
            <span>TRUST HALO</span><strong>{formatMetric(firstTimeline?.trust_halo_curve[0])}</strong>
            <span>BOUNDARY</span><strong>{formatMetric(firstTimeline?.boundary_integrity_curve[0])}</strong>
            <span>WINDOWS</span><strong>{firstTimeline?.windows.length ?? 0}</strong>
            <span>GAPS</span><strong>{firstTimeline?.gap_markers.length ?? 0}</strong>
          </div>
        </div>

        <div className="temporal-calibration-section" data-testid="temporal-calibration-locks">
          <div className="temporal-calibration-section__label">ANIMATION LOCKS</div>
          <div className="temporal-calibration-effect-grid">
            <span>PLAYBACK CONTROLS</span>
            <strong>{String(frame.animation_locks.animated_playback_controls_enabled).toUpperCase()}</strong>
            <span>FORECAST MUTATION</span>
            <strong>{String(frame.animation_locks.forecast_probability_mutation_allowed).toUpperCase()}</strong>
            <span>SCORE MUTATION</span><strong>{String(frame.animation_locks.score_mutation_allowed).toUpperCase()}</strong>
            <span>AUTHORITY MUTATION</span>
            <strong>{String(frame.animation_locks.authority_tier_mutation_allowed).toUpperCase()}</strong>
            <span>EXECUTION</span><strong>{String(frame.animation_locks.execution_authority).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.animation_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="temporal-calibration-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
