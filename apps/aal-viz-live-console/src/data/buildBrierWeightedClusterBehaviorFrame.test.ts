import { describe, expect, it } from 'vitest';
import { buildBrierWeightedClusterBehaviorFrame } from './buildBrierWeightedClusterBehaviorFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

describe('buildBrierWeightedClusterBehaviorFrame', () => {
  it('builds deterministic projection-only cluster behavior frames', () => {
    const first = buildBrierWeightedClusterBehaviorFrame(sampleProjectionBundle);
    const second = buildBrierWeightedClusterBehaviorFrame(sampleProjectionBundle);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizBrierWeightedClusterBehaviorFrame.v1');
    expect(first.authority).toBe('VISUAL_CALIBRATION_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_FORECAST_SCORE_OR_AUTHORITY_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('renders missing cluster scoring as not-computable neutral weather', () => {
    const frame = buildBrierWeightedClusterBehaviorFrame(sampleProjectionBundle);

    expect(frame.clusters.every((cluster) => cluster.scoring_status === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.clusters.every((cluster) => cluster.calibration_weather === 'NOT_COMPUTABLE')).toBe(true);
    expect(frame.clusters.every((cluster) => cluster.cohesion_multiplier === 1)).toBe(true);
    expect(frame.clusters.every((cluster) => cluster.turbulence === 0)).toBe(true);
    expect(frame.clusters.every((cluster) => cluster.source_score_mutated === false)).toBe(true);
  });

  it('damps scored cluster behavior when scored member count is low', () => {
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
    const frame = buildBrierWeightedClusterBehaviorFrame(bundle);
    const cluster = frame.clusters[0];

    expect(cluster.scoring_status).toBe('UNDER_SAMPLED');
    expect(cluster.calibration_weather).toBe('UNDER_SAMPLED');
    expect(cluster.mean_brier).toBe(0);
    expect(cluster.cohesion_multiplier).toBeGreaterThan(1);
    expect(cluster.cohesion_multiplier).toBeLessThan(1.25);
    expect(cluster.turbulence).toBe(0);
  });

  it('locks cluster behavior out of forecast, score, authority, promotion, execution, and truth mutation', () => {
    const frame = buildBrierWeightedClusterBehaviorFrame(sampleProjectionBundle);

    expect(frame.cluster_locks.display_only).toBe(true);
    expect(frame.cluster_locks.cluster_weather_static_mode_available).toBe(true);
    expect(frame.cluster_locks.scoring_mutation_allowed).toBe(false);
    expect(frame.cluster_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.cluster_locks.score_mutation_allowed).toBe(false);
    expect(frame.cluster_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.cluster_locks.automatic_promotion_allowed).toBe(false);
    expect(frame.cluster_locks.automatic_demotion_allowed).toBe(false);
    expect(frame.cluster_locks.execution_authority).toBe(false);
    expect(frame.cluster_locks.truth_authority).toBe(false);
  });
});
