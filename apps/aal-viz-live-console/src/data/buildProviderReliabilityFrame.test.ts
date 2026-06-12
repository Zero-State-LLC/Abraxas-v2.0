import { describe, expect, it } from 'vitest';
import { buildProviderReliabilityFrame } from './buildProviderReliabilityFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle } from '../types';

function bundleWithProviderOutcomes(): LiveConsoleProjectionBundle {
  return {
    ...sampleProjectionBundle,
    systems: [
      {
        ...sampleProjectionBundle.systems[0],
        system_id: 'provider_alpha',
        projection_packets: [
          {
            packet_id: 'shared-event-001',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
          {
            packet_id: 'alpha-event-002',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
          {
            packet_id: 'alpha-event-003',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'RESOLVED',
            display_value: '1',
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
        ],
      },
      {
        ...sampleProjectionBundle.systems[1],
        system_id: 'provider_beta',
        projection_packets: [
          {
            packet_id: 'shared-event-001',
            packet_type: 'FORECAST_OUTCOME_RESOLUTION',
            status: 'AMBIGUOUS',
            display_value: null,
            authority_source: 'SHADOW_LANE',
            projection_only: true,
          },
        ],
      },
    ],
  };
}

describe('buildProviderReliabilityFrame', () => {
  it('builds deterministic provider reliability frames', () => {
    const bundle = bundleWithProviderOutcomes();
    const first = buildProviderReliabilityFrame(bundle, null);
    const second = buildProviderReliabilityFrame(bundle, null);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizProviderReliabilityFrame.v1');
    expect(first.authority).toBe('SOURCE_RELIABILITY_SCORING_AND_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('NO_FORECAST_OUTCOME_SCORE_AUTHORITY_OR_ROUTING_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('creates provider observations from live outcome feed candidates without truth authority', () => {
    const frame = buildProviderReliabilityFrame(bundleWithProviderOutcomes(), null);

    expect(frame.observations.length).toBeGreaterThanOrEqual(4);
    expect(frame.observations.every((observation) => observation.provider_score_only)).toBe(true);
    expect(frame.observations.every((observation) => observation.forecast_mutation_allowed === false)).toBe(true);
    expect(frame.observations.every((observation) => observation.outcome_truth_authority === false)).toBe(true);
  });

  it('scores providers with trust bands while keeping under-sampled providers non-promotional', () => {
    const frame = buildProviderReliabilityFrame(bundleWithProviderOutcomes(), null);
    const alpha = frame.reliability_scores.find((score) => score.provider_id === 'AAL_VIZ_provider_alpha');
    const beta = frame.reliability_scores.find((score) => score.provider_id === 'AAL_VIZ_provider_beta');

    expect(alpha?.observation_count).toBe(3);
    expect(alpha?.trust_band).not.toBe('UNDER_SAMPLED');
    expect(alpha?.reliability_score).not.toBeNull();
    expect(beta?.observation_count).toBe(1);
    expect(beta?.trust_band).toBe('UNDER_SAMPLED');
    expect(beta?.reliability_score).toBeNull();
    expect(beta?.forecast_probability_mutated).toBe(false);
    expect(beta?.brier_score_mutated).toBe(false);
    expect(beta?.outcome_truth_mutated).toBe(false);
  });

  it('emits provider conflicts as review-only packets', () => {
    const frame = buildProviderReliabilityFrame(bundleWithProviderOutcomes(), null);

    expect(frame.conflicts).toHaveLength(1);
    expect(frame.conflicts[0].target_event_id).toBe('shared-event-001');
    expect(frame.conflicts[0].conflict_type).toBe('RESULT_MISMATCH');
    expect(frame.conflicts[0].creates_review_item_only).toBe(true);
    expect(frame.conflicts[0].outcome_truth_authority).toBe(false);
  });

  it('locks provider reliability out of healthcheck writes, broadcasts, execution, routing, forecast, score, and truth mutation', () => {
    const frame = buildProviderReliabilityFrame(bundleWithProviderOutcomes(), null);

    expect(frame.reliability_locks.provider_healthcheck_enabled).toBe(false);
    expect(frame.reliability_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.reliability_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.reliability_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.reliability_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.reliability_locks.brier_score_mutation_allowed).toBe(false);
    expect(frame.reliability_locks.outcome_truth_mutation_allowed).toBe(false);
    expect(frame.reliability_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.reliability_locks.execution_authority).toBe(false);
    expect(frame.reliability_locks.truth_authority).toBe(false);
  });
});
