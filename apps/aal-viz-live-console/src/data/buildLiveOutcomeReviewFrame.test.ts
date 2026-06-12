import { describe, expect, it } from 'vitest';
import { buildLiveOutcomeReviewFrame } from './buildLiveOutcomeReviewFrame';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

const LOCKED_PACKET_AUTHORITY = {
  execution_allowed: false as const,
  runtime_mutation_allowed: false as const,
  promotion_allowed: false as const,
  production_activation_allowed: false as const,
  metric_emission_allowed: false as const,
  forecast_influence_allowed: false as const,
  p43_lanes_allowed: false as const,
};

const SAMPLE_PACKETS: OperatorActionPacketsBundle = {
  schema_version: 'AALViz.OperatorActionPackets.v0.1',
  generated_at: '2026-05-30T00:00:00Z',
  authority: LOCKED_PACKET_AUTHORITY,
  source_projection_bundle_hash: null,
  fail_closed_reason: null,
      packets: [
    {
      packet_id: 'review-pkt-001',
      source_frontier_ref: 'missing-outcome-target-001',
      action_title: 'REVIEW DECISION',
      action_type: 'REVIEW_REQUIRED',
      recommended_next_step: 'REVIEW_LOW_PROVENANCE',
      authority_required: 'OPERATOR_REVIEW',
      allowed: true,
      execution_allowed: false,
      runtime_mutation_allowed: false,
      promotion_allowed: false,
      prompt_body: 'Review the low-provenance outcome candidate.',
      validation_checklist: ['confirm outcome'],
      blocked_scopes: ['EXECUTION', 'FORECAST_MUTATION'],
      provenance_refs: ['forecast-outcome-pkt-001'],
      fail_closed_reason: null,
    },
  ],
};

function bundleWithOutcome(): LiveConsoleProjectionBundle {
  return {
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
      ...sampleProjectionBundle.systems.slice(1),
    ],
  };
}

describe('buildLiveOutcomeReviewFrame', () => {
  it('builds deterministic live outcome review frames', () => {
    const bundle = bundleWithOutcome();
    const first = buildLiveOutcomeReviewFrame(bundle, SAMPLE_PACKETS);
    const second = buildLiveOutcomeReviewFrame(bundle, SAMPLE_PACKETS);

    expect(first).toEqual(second);
    expect(first.packet_type).toBe('AALVizLiveOutcomeReviewFrame.v1');
    expect(first.authority).toBe('OUTCOME_INTAKE_REVIEW_AND_PROJECTION_ONLY');
    expect(first.mutation_policy).toBe('APPEND_ONLY_WITH_CORRECTION_PACKETS');
    expect(first.provenance_hash).toMatch(/^[a-f0-9]{8}$/);
  });

  it('normalizes outcome feed candidates without final truth authority', () => {
    const frame = buildLiveOutcomeReviewFrame(bundleWithOutcome(), SAMPLE_PACKETS);
    const feedPacket = frame.feed_packets.find((packet) => packet.provider_event_id === 'forecast-outcome-pkt-001');

    expect(feedPacket?.normalized_status).toBe('RESOLVED');
    expect(feedPacket?.normalized_result).toBe(1);
    expect(feedPacket?.candidate_resolution_only).toBe(true);
    expect(feedPacket?.final_truth_authority).toBe(false);
    expect(feedPacket?.source_forecast_probability_mutated).toBe(false);
    expect(feedPacket?.source_score_mutated).toBe(false);
  });

  it('routes low-provenance and pending decision outcomes to review', () => {
    const frame = buildLiveOutcomeReviewFrame(bundleWithOutcome(), SAMPLE_PACKETS);
    const reasons = frame.review_items.map((item) => item.review_reason);

    expect(reasons).toContain('LOW_PROVENANCE');
    expect(reasons).toContain('PENDING_RESOLUTION');
    expect(frame.review_items.every((item) => item.outcome_resolution_authority === false)).toBe(true);
    expect(frame.review_items.every((item) => item.review_decision_descriptive_only === true)).toBe(true);
  });

  it('keeps correction workflow append-only and empty until explicit correction evidence exists', () => {
    const frame = buildLiveOutcomeReviewFrame(bundleWithOutcome(), SAMPLE_PACKETS);

    expect(frame.correction_packets).toEqual([]);
    expect(frame.review_locks.append_only_with_correction_packets).toBe(true);
    expect(frame.review_locks.corrections_preserve_previous_and_corrected_hashes).toBe(true);
  });

  it('locks adapters, writeback, broadcasts, execution, routing, forecast, score, and truth authority', () => {
    const frame = buildLiveOutcomeReviewFrame(bundleWithOutcome(), SAMPLE_PACKETS);

    expect(frame.review_locks.provider_polling_enabled).toBe(false);
    expect(frame.review_locks.notion_write_adapter_enabled).toBe(false);
    expect(frame.review_locks.websocket_broadcast_enabled).toBe(false);
    expect(frame.review_locks.autonomous_execution_allowed).toBe(false);
    expect(frame.review_locks.outcome_resolution_without_review_allowed).toBe(false);
    expect(frame.review_locks.forecast_probability_mutation_allowed).toBe(false);
    expect(frame.review_locks.score_mutation_allowed).toBe(false);
    expect(frame.review_locks.authority_tier_mutation_allowed).toBe(false);
    expect(frame.review_locks.strategy_routing_mutation_allowed).toBe(false);
    expect(frame.review_locks.execution_authority).toBe(false);
    expect(frame.review_locks.truth_authority).toBe(false);
  });
});
