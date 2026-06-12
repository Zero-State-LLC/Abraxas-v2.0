import { describe, expect, it } from 'vitest';
import { buildTemporalCalibrationAnimationFrame } from './buildTemporalCalibrationAnimationFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('buildTemporalCalibrationAnimationFrame', () => {
  it('builds deterministic temporal calibration projection frames', () => {
    const first = buildTemporalCalibrationAnimationFrame(sampleProjectionBundle);
    const second = buildTemporalCalibrationAnimationFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizTemporalCalibrationAnimationFrame.v1');
    expect(first.authority).toBe('VISUAL_TEMPORAL_CALIBRATION_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_FORECAST_SCORE_OR_AUTHORITY_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('renders missing windows as explicit temporal gaps without certainty interpolation', () => {
    const frame = buildTemporalCalibrationAnimationFrame(sampleProjectionBundle);

    expect(frame.timelines.every((timeline) => timeline.animation_badge === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.timelines.every((timeline) => timeline.gap_markers.length === 1)).toBe(true);
    expect(frame.timelines.every((timeline) => timeline.playback.smoothing === 'NONE')).toBe(true);
    expect(frame.animation_locks.missing_windows_render_temporal_gaps).toBe(true);
    expect(frame.animation_locks.missing_windows_interpolated_as_certainty).toBe(false);
  });

  it('marks low-sample scored windows as under-sampled and static snapshot playback', () => {
    const bundle: LiveConsoleProjectionBundle = {
      ...sampleProjectionBundle,
      systems: [
        {
          ...sampleProjectionBundle.systems[0],
          projection_packets: [
            {
              packet_id: 'forecast-outcome-pkt-001',
              packet_type: 'FORECAST_OUTCOME_RESOLUTION',
              status: 'RESOLVED',
              display_value: '1',
              authority_source: 'SHADOW_LANE',
              projection_only: true,
            },
          ],
        },
      ],
    };
    const frame = buildTemporalCalibrationAnimationFrame(bundle);
    const timeline = frame.timelines[0];

    expect(timeline.animation_badge).toBe('UNDER_SAMPLED');
    expect(timeline.gap_markers).toHaveLength(0);
    expect(timeline.playback.mode).toBe('SNAPSHOT');
    expect(timeline.playback.loop).toBe(false);
    expect(timeline.temporal_cohesion_curve[0]).toBeGreaterThan(1);
    expect(timeline.turbulence_curve[0]).toBe(0);
  });

  it('locks animation out of forecast, score, authority, promotion, execution, and truth mutation', () => {
    const frame = buildTemporalCalibrationAnimationFrame(sampleProjectionBundle);

    expect(frame.animation_locks.display_only).toBe(true);
    expect(frame.animation_locks.static_timeline_table_available).toBe(true);
    expect(frame.animation_locks.animated_playback_controls_enabled).toBe(false);
    expect(frame.animation_locks.scoring_mutation_allowed).toBe(false);
    expect(frame.animation_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.animation_locks.score_mutation_allowed).toBe(false);
    expect(frame.animation_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.animation_locks.automatic_promotion_allowed).toBe(false);
    expect(frame.animation_locks.automatic_demotion_allowed).toBe(false);
    expect(frame.animation_locks.execution_authority).toBe(false);
    expect(frame.animation_locks.truth_authority).toBe(false);
  });
});
