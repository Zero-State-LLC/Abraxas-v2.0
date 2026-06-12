import { describe, expect, it } from 'vitest';
import { buildReviewSuggestionMatrixFrame } from './buildReviewSuggestionMatrixFrame';
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

describe('buildReviewSuggestionMatrixFrame', () => {
  it('builds deterministic advisory suggestion and provider matrix frames', () => {
    const bundle = bundleWithProviderOutcomes();
    const first = buildReviewSuggestionMatrixFrame(bundle, null);
    const second = buildReviewSuggestionMatrixFrame(bundle, null);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizReviewSuggestionMatrixFrame.v1');
    expect(first.authority).toBe('ADVISORY_REVIEW_RECOMMENDATION_AND_SOURCE_COMPARISON_ONLY');
    expect(first.mutation_policy).toBe('NO_EXECUTION_OUTCOME_FORECAST_SCORE_AUTHORITY_OR_ROUTING_MUTATION');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('emits advisory suggestions with reason codes, evidence, and no mutation authority', () => {
    const frame = buildReviewSuggestionMatrixFrame(bundleWithProviderOutcomes(), null);

    expect(frame.suggestions.length).toBeGreaterThan(0);
    expect(frame.suggestions.every((suggestion) => suggestion.authority === 'SUGGESTION_ONLY')).toBe(true);
    expect(frame.suggestions.every((suggestion) => suggestion.reason_codes.length > 0)).toBe(true);
    expect(frame.suggestions.every((suggestion) => suggestion.required_evidence.length > 0)).toBe(true);
    expect(frame.suggestions.every((suggestion) => suggestion.outcome_resolution_authority === false)).toBe(true);
    expect(frame.suggestions.every((suggestion) => suggestion.forecast_mutation_allowed === false)).toBe(true);
    expect(frame.suggestions.every((suggestion) => suggestion.routing_mutation_allowed === false)).toBe(true);
  });

  it('builds a descriptive provider comparison matrix with under-sampled provider state preserved', () => {
    const frame = buildReviewSuggestionMatrixFrame(bundleWithProviderOutcomes(), null);
    const beta = frame.provider_matrix.providers.find((provider) => provider.provider_id === 'AAL_VIZ_provider_beta');

    expect(frame.provider_matrix.providers.length).toBeGreaterThan(0);
    expect(frame.provider_matrix.descriptive_comparison_only).toBe(true);
    expect(frame.provider_matrix.provider_removal_authority).toBe(false);
    expect(frame.provider_matrix.outcome_truth_authority).toBe(false);
    expect(beta?.trust_band).toBe('UNDER_SAMPLED');
    expect(beta?.rank).toBeNull();
  });

  it('locks suggestions and matrix out of writeback, execution, correction, forecast, score, routing, and truth authority', () => {
    const frame = buildReviewSuggestionMatrixFrame(bundleWithProviderOutcomes(), null);

    expect(frame.suggestion_locks.suggestion_only).toBe(true);
    expect(frame.suggestion_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.suggestion_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.suggestion_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.suggestion_locks.outcome_resolution_allowed).toBe(false);
    expect(frame.suggestion_locks.correction_application_allowed).toBe(false);
    expect(frame.suggestion_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.suggestion_locks.score_mutation_allowed).toBe(false);
    expect(frame.suggestion_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.suggestion_locks.provider_removal_allowed).toBe(false);
    expect(frame.suggestion_locks.execution_authority).toBe(false);
    expect(frame.suggestion_locks.truth_authority).toBe(false);
  });
});
