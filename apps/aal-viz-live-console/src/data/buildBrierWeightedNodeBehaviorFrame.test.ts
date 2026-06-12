import { describe, expect, it } from 'vitest';
import { buildBrierWeightedNodeBehaviorFrame } from './buildBrierWeightedNodeBehaviorFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('buildBrierWeightedNodeBehaviorFrame', () => {
  it('builds deterministic visual-calibration projection frames', () => {
    const first = buildBrierWeightedNodeBehaviorFrame(sampleProjectionBundle);
    const second = buildBrierWeightedNodeBehaviorFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizBrierWeightedNodeBehaviorFrame.v1');
    expect(first.authority).toBe('VISUAL_CALIBRATION_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_FORECAST_OR_AUTHORITY_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('renders missing scoring records as calibration-not-computable neutral behavior', () => {
    const frame = buildBrierWeightedNodeBehaviorFrame(sampleProjectionBundle);

    expect(frame.behaviors.every((behavior) => behavior.calibration_badge === 'CALIBRATION_NOT_COMPUTABLE')).toBe(true);
    expect(frame.behaviors.every((behavior) => behavior.stability_multiplier === 1)).toBe(true);
    expect(frame.behaviors.every((behavior) => behavior.jitter_penalty === 0)).toBe(true);
    expect(frame.behaviors.every((behavior) => behavior.source_forecast_probability_mutated === false)).toBe(true);
  });

  it('damps scored behavior when sample size is low', () => {
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
    const frame = buildBrierWeightedNodeBehaviorFrame(bundle);

    expect(frame.behaviors[0].calibration_badge).toBe('UNDER_SAMPLED');
    expect(frame.behaviors[0].brier_score).toBe(0);
    expect(frame.behaviors[0].stability_multiplier).toBeGreaterThan(1);
    expect(frame.behaviors[0].stability_multiplier).toBeLessThan(1.25);
    expect(frame.behaviors[0].trust_drag).toBe(0);
  });

  it('locks behavior out of scoring, forecast, authority, promotion, execution, and truth mutation', () => {
    const frame = buildBrierWeightedNodeBehaviorFrame(sampleProjectionBundle);

    expect(frame.behavior_locks.display_only).toBe(true);
    expect(frame.behavior_locks.scoring_mutation_allowed).toBe(false);
    expect(frame.behavior_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.behavior_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.behavior_locks.automatic_promotion_allowed).toBe(false);
    expect(frame.behavior_locks.automatic_demotion_allowed).toBe(false);
    expect(frame.behavior_locks.execution_authority).toBe(false);
    expect(frame.behavior_locks.truth_authority).toBe(false);
  });
});

